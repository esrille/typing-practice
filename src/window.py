# typing-practice - Typing Practice
#
# Copyright (c) 2020-2022 Esrille Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import package

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gio, GLib, Gtk, Gdk, Pango, PangoCairo

from chart import Chart
from engine import Engine, EngineMode, Stats
from hurigana import HuriganaLayout
import ime
from keyboard import Keyboard
from roomazi import Roomazi

import cairo
from datetime import date
import gettext
import logging
import os


logger = logging.getLogger(__name__)
_ = lambda a: gettext.dgettext(package.get_name(), a)


WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 550
WIDTH = 600
HEIGHT = 510
FONT_SIZE = 20
HINT_SIZE = 16
LINE_HEIGHT = 30
LINE_SPACING = 15
PRACTICE_LINE_SPACING = 50
DEFAULT_FONT = "Noto Sans Mono CJK JP 20px"
HINT_FONT = "Noto Sans Mono CJK JP 16px"
HINT_SPACING = 8
MARGIN_LEFT = (WINDOW_WIDTH - WIDTH) / 2
MARGIN_RIGHT = MARGIN_LEFT
MARGIN_TOP = (WINDOW_HEIGHT - HEIGHT) / 2
MARGIN_BOTTOM = MARGIN_TOP
STOPWATCH_WIDTH = 80
STOPWATCH_HEIGHT = 18
CHART_WIDTH = WIDTH
CHART_HEIGHT = 400
PRACTICE_CENTER = MARGIN_LEFT + (MARGIN_RIGHT + 600) / 2


def get_title():
    return _("Typing Practice")


def get_prefix(s1, s2):
    i = 0
    while i < min(len(s1), len(s2)):
        if s1[i] != s2[i]:
            break
        i += 1
    return s1[:i]


class View(Gtk.DrawingArea):

    def __init__(self):
        Gtk.DrawingArea.__init__(self)

        self.caret = Gdk.Rectangle()

        self.connect("draw", self.on_draw)
        self.connect("key-press-event", self.on_key_press)
        self.connect("key-release-event", self.on_key_release)
        self.connect("focus-in-event", self.on_focus_in)
        self.connect("focus-out-event", self.on_focus_out)

        self.im_context = Gtk.IMMulticontext()
        self.im_context.set_client_window(self.get_window())
        self.im_context.connect("commit", self.on_commit)
        self.im_context.connect("delete-surrounding", self.on_delete_surrounding)
        self.im_context.connect("retrieve-surrounding", self.on_retrieve_surrounding)
        self.im_context.connect("preedit-changed", self.on_preedit_changed)
        self.im_context.connect("preedit-end", self.on_preedit_end)
        self.im_context.connect("preedit-start", self.on_preedit_start)

        self.set_can_focus(True)

        self.roomazi = Roomazi()
        self.keyboard = Keyboard(self.roomazi)
        self.engine = Engine(self.roomazi)

    def _clear(self, wid, ctx):
        width = wid.get_allocated_width()
        height = wid.get_allocated_height()
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()
        ctx.set_source_rgb(0, 0, 0)

    def _draw_caret(self, ctx, layout, current, x, y):
        ctx.save()
        st, we = layout.get_cursor_pos(len(current.encode()))
        self.caret.x = x + st.x / Pango.SCALE - 1
        self.caret.y = y + st.y / Pango.SCALE
        self.caret.width = st.width / Pango.SCALE + 2
        self.caret.height = st.height / Pango.SCALE
        if (1, 13) <= cairo.version_info:
            ctx.set_operator(cairo.Operator.DIFFERENCE)
            ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(self.caret.x, self.caret.y, self.caret.width, self.caret.height)
        ctx.fill()
        ctx.restore()
        x, y = self.translate_coordinates(self.get_toplevel(), self.caret.x, self.caret.y)
        self.caret.x = x
        self.caret.y = y
        self.im_context.set_cursor_location(self.caret)

    def _draw_hints(self, wid, ctx: cairo.Context, hint):
        hint = self.engine.markup(hint)

        ctx.set_source_rgb(0x99 / 255, 0x99 / 255, 0x99 / 255)
        ctx.set_line_width(1)
        ctx.move_to(MARGIN_LEFT - 10, 5)
        ctx.line_to(MARGIN_LEFT - 10, WINDOW_HEIGHT - 5)
        ctx.stroke()

        ctx.set_source_rgb(0, 0, 0)
        hurigana = HuriganaLayout(ctx)
        hurigana.set_ruby_size(HINT_SIZE / 2.5)
        desc = Pango.font_description_from_string(HINT_FONT)
        hurigana.set_font_description(desc)
        hurigana.set_width(MARGIN_LEFT - 30)
        hurigana.set_spacing(HINT_SPACING)
        hurigana.set_markup(hint)
        hurigana.draw(10, MARGIN_TOP)

    def _draw_menu(self, wid, ctx):
        # Draw text
        hurigana = HuriganaLayout(ctx)
        hurigana.set_ruby_size(FONT_SIZE / 2.5)
        desc = Pango.font_description_from_string(DEFAULT_FONT)
        hurigana.set_font_description(desc)
        hurigana.set_width(WIDTH)
        hurigana.set_spacing(LINE_SPACING)
        markup = self.engine.markup(self.engine.get_text())
        hurigana.set_markup(markup)
        hurigana.draw(MARGIN_LEFT, MARGIN_TOP)

        self._draw_hints(wid, ctx, self.engine.get_hint())

    if Pango.version_check(1, 44, 0) is None:

        def _draw_typed(self, ctx, layout, hurigana):
            typed = get_prefix(self.engine.get_plain(), self.engine.get_typed())
            correct_length = len(typed)
            typed = hurigana.adjust_typed(typed)
            attr_list = Pango.AttrList().new()

            formatted = typed
            so = 0
            eo = len(formatted.encode())
            attr = Pango.attr_foreground_new(0x0000, 0x6600, 0xcc00)
            attr.start_index = so
            attr.end_index = eo
            attr_list.insert(attr)

            if correct_length < len(self.engine.get_typed()):
                typed += self.engine.get_typed()[correct_length:]
                formatted += self.engine.get_typed()[correct_length:]
                so = eo
                eo = so + len(self.engine.get_typed()[correct_length:].encode())
                attr = Pango.attr_background_new(0xff00, 0xcc00, 0xff00)
                attr.start_index = so
                attr.end_index = eo
                attr_list.insert(attr)
                attr = Pango.attr_foreground_new(0xff00, 0x0000, 0x0000)
                attr.start_index = so
                attr.end_index = eo
                attr_list.insert(attr)

            preedit = self.engine.get_preedit()
            if preedit[0] and 0 < preedit[2]:
                typed += preedit[0][:preedit[2]]
                formatted += preedit[0][:preedit[2]]
                so = eo
                eo = so + len(preedit[0][:preedit[2]].encode())
                attr = Pango.attr_foreground_new(0x0000, 0x6600, 0xff00)
                attr.start_index = so
                attr.end_index = eo
                attr_list.insert(attr)

                # Note with Pango 1.48, the following splice() does not work
                # as expected. It works with Pango 1.44, though. So we will
                # manually marge preedit attributes into attr_list:
                #   attr_list.splice(preedit[1], so, 0)
                attributes = preedit[1].get_attributes()
                for i in attributes:
                    i.start_index += so
                    i.end_index += so
                    attr_list.change(i)

            layout.set_text(formatted, -1)
            layout.set_attributes(attr_list)
            PangoCairo.update_layout(ctx, layout)
            PangoCairo.show_layout(ctx, layout)
            return layout, typed

    else:

        def _draw_typed(self, ctx, layout, hurigana):
            attr_list_preedit = Pango.AttrList().new()
            typed = get_prefix(self.engine.get_plain(), self.engine.get_typed())
            correct_length = len(typed)
            typed = hurigana.adjust_typed(typed)
            formatted = '<span foreground="#0066CC">' + typed + '</span>'
            if correct_length < len(self.engine.get_typed()):
                formatted += '<span foreground="#FF0000" background="#FFCCFF">' + \
                         self.engine.get_typed()[correct_length:] + \
                         '</span>'
                typed += self.engine.get_typed()[correct_length:]
            preedit = self.engine.get_preedit()
            if preedit[0] and 0 < preedit[2]:
                attr_list_preedit.splice(preedit[1],
                                         len(typed.encode()),
                                         len(preedit[0][:preedit[2]].encode()))
                formatted += '<span foreground="#0066FF">' + preedit[0][:preedit[2]] + '</span>'
                typed += preedit[0][:preedit[2]]
            layout.set_markup(formatted, -1)
            if preedit[0] and 0 < preedit[2]:
                attr_list = layout.get_attributes()
                attr_list.splice(attr_list_preedit, 0, 0)
                layout.set_attributes(attr_list)
            PangoCairo.update_layout(ctx, layout)
            PangoCairo.show_layout(ctx, layout)
            return layout, typed

    def _draw_practice(self, wid, ctx):
        ctx.select_font_face("Noto Sans Mono CJK JP", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(FONT_SIZE)

        x = MARGIN_LEFT
        y = MARGIN_TOP
        desc = Pango.font_description_from_string(DEFAULT_FONT)

        # Draw text for practicing.
        hurigana = HuriganaLayout(ctx)
        hurigana.set_font_description(desc)
        hurigana.set_width(WIDTH)
        hurigana.set_spacing(PRACTICE_LINE_SPACING)
        hurigana.set_text(self.engine.get_text())
        hurigana.draw(x, y)

        # Draw what has been typed.
        y += LINE_HEIGHT
        ctx.move_to(x, y)
        layout = PangoCairo.create_layout(ctx)
        layout.set_font_description(desc)
        layout.set_width(WIDTH * Pango.SCALE)
        layout.set_spacing(PRACTICE_LINE_SPACING * Pango.SCALE)
        (layout, current) = self._draw_typed(ctx, layout, hurigana)

        # Draw caret
        ctx.move_to(x, y)
        layout.set_text(current, -1)
        PangoCairo.update_layout(ctx, layout)
        self._draw_caret(ctx, layout, current, x, y)

        # Draw keyboard:
        if self.engine.get_show_keyboard():
            text = self.engine.get_text()
            current = get_prefix(text, self.engine.get_typed())
            if len(current) <= len(text):
                current = text[len(current):]
            pair = self.keyboard.draw(ctx, x + MARGIN_RIGHT / 2, WINDOW_HEIGHT - 256, current)
            if pair[0]:
                ctx.set_source_rgb(0, 0, 0)
                t = pair[0]
                if pair[0] != pair[1]:
                    t += ' [' + pair[1] + ']'
                self._show_centered_text(ctx, t, PRACTICE_CENTER, WINDOW_HEIGHT - MARGIN_BOTTOM - STOPWATCH_HEIGHT)

        # Show stopwatch
        ctx.set_source_rgb(0, 0, 0)
        elapsed = self.engine.get_duration()
        ctx.move_to(WINDOW_WIDTH - MARGIN_RIGHT - STOPWATCH_WIDTH,
                    WINDOW_HEIGHT - MARGIN_BOTTOM - STOPWATCH_HEIGHT)
        ctx.show_text("[{:4d}] {:02d}:{:04.1f}".format(
            self.engine.get_touch_count(),
            int(elapsed / 60),
            elapsed % 60))

        hint = self.engine.get_hint()
        if not hint:
            hint = "<kbd>Esc</kbd> メニューにもどる"
        self._draw_hints(wid, ctx, hint)

    def _draw_score(self, wid, ctx):
        ctx.select_font_face("Noto Sans Mono CJK JP", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        x = MARGIN_LEFT
        y = MARGIN_TOP + 2 * FONT_SIZE

        ctx.set_font_size(2 * FONT_SIZE)
        ctx.set_source_rgb(0xff / 255, 0xcc / 255, 0x33 / 255)
        ctx.move_to(x, y)
        score = self.engine.get_score()
        extra_score = 0
        if 6 < score:
            extra_score = score - 6
            score = 6
        ctx.show_text("★" * score + '☆' * (6 - score))
        if extra_score:
            ctx.set_source_rgb(0x00 / 255, 0xcc / 255, 0xff / 255)
            ctx.show_text("★" * extra_score)
        y += 2 * LINE_HEIGHT

        ctx.set_font_size(FONT_SIZE)
        ctx.set_source_rgb(0, 0, 0)
        duration = self.engine.get_duration()
        touch_count = self.engine.get_touch_count()
        correct_count = self.engine.get_correct_count()
        error_count = self.engine.get_error_count()
        text = ("￹練習時間￺れんしゅうじかん￻: {:02d}:{:04.1f}\n" +
                "タッチ￹数￺すう￻: {:d}\n" +
                "ミスタッチ￹数￺すう￻: {:d}\n" +
                "１￹分間￺ ぷんかん￻あたりのただしいタッチ￹数￺すう￻: {:.0f} [CPM] = {:d} [WPM]\n" +
                "１￹分間￺ ぷんかん￻あたりのただしい￹文字￺もじ￻￹数￺すう￻: {:.0f} [￹文字￺もじ￻/￹分￺ふん￻]\n" +
                "ミスタッチのわりあい: {:.1f} [%]").format(
            int(duration / 60), duration % 60,
            touch_count,
            error_count,
            self.engine.get_cpm(), self.engine.get_wpm(),
            len(self.engine.get_plain()) * 60 / duration,
            self.engine.get_error_ratio() * 100)
        hurigana = HuriganaLayout(ctx)
        hurigana.set_ruby_size(FONT_SIZE / 2.5)
        desc = Pango.font_description_from_string(DEFAULT_FONT)
        hurigana.set_font_description(desc)
        hurigana.set_width(WIDTH)
        hurigana.set_spacing(LINE_SPACING)
        hurigana.set_text(text)
        hurigana.draw(x, y)

        hint = "<kbd>Enter</kbd> つぎにすすむ\n<kbd>Backspace</kbd> もういちど\n<kbd>Esc</kbd> メニューにもどる"
        self._draw_hints(wid, ctx, hint)

    def _draw_stats(self, wid, ctx: cairo.Context):
        ctx.select_font_face("Noto Sans Mono CJK JP", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(FONT_SIZE)

        stats = self.engine.get_stats().get_stats()
        max_wpm = round(self.engine.get_stats().get_max_wpm() + 9, -1)
        today = date.today()
        period = 0
        if stats:
            first_day = stats[0][0]
            period = (today - first_day).days
        if period == 0:
            first_day = today
            period = 1

        x = MARGIN_LEFT + 50
        y = 2 * LINE_HEIGHT

        chart = Chart(ctx, x, y, CHART_WIDTH, CHART_HEIGHT)
        ctx.set_source_rgb(0xcc / 255, 0xcc / 255, 0xcc / 255)
        step = WIDTH / period
        while step < 10:
            step *= 10
        chart.axis(step, CHART_HEIGHT / max_wpm * 10)

        ctx.set_source_rgb(0xcc / 255, 0xcc / 255, 0xcc / 255)
        ctx.move_to(x, y + CHART_HEIGHT)
        self._show_aligned_text(ctx, first_day.strftime('%m/%d'), -0.5, 1)
        ctx.move_to(x + CHART_WIDTH, y + CHART_HEIGHT)
        self._show_aligned_text(ctx, today.strftime('%m/%d'), -0.5, 1)
        ctx.set_source_rgb(0x00 / 255, 0xCC / 255, 0x33 / 255)
        ctx.move_to(x, y)
        self._show_aligned_text(ctx, '100%', -1.2, 0.5)
        ctx.set_source_rgb(0xff / 255, 0x66 / 255, 0x00 / 255)
        ctx.move_to(x + CHART_WIDTH, y)
        self._show_aligned_text(ctx, str(max_wpm) + ' WPM', 0.2, 0.5)

        notes = ' <span foreground="#00CC33">ー ￹正確￺せいかく￻さ</span>\n <span foreground="#FF6600">ー WPM</span>'
        hurigana = HuriganaLayout(ctx)
        hurigana.set_ruby_size(FONT_SIZE / 2.5)
        desc = Pango.font_description_from_string(DEFAULT_FONT)
        hurigana.set_font_description(desc)
        hurigana.set_width(MARGIN_RIGHT)
        hurigana.set_spacing(LINE_SPACING)
        hurigana.set_markup(notes)
        hurigana.draw(x + CHART_WIDTH, y + CHART_HEIGHT - 3 * LINE_HEIGHT)

        # WPM
        ctx.set_source_rgb(0xff / 255, 0x66 / 255, 0x00 / 255)
        data = list(map(lambda x: ((x[0] - first_day).days, x[2]), stats))
        logger.info(data)
        chart.set_x_range(0, period)
        chart.set_y_range(0, max_wpm)
        chart.scatter_line(data)
        chart.scatter_dot(data, 5)

        # Accuracy
        ctx.set_source_rgb(0x00 / 255, 0xCC / 255, 0x33 / 255)
        data = list(map(lambda x: ((x[0] - first_day).days, x[3]), stats))
        logger.info(data)
        chart.set_x_range(0, period)
        chart.set_y_range(0, 1)
        chart.scatter_line(data)
        chart.scatter_dot(data, 5)

        self._draw_hints(wid, ctx, '<kbd>Esc</kbd> もどる\n<kbd>F2</kbd> きろくのリセット')

    def _show_aligned_text(self, ctx: cairo.Context, text, x, y):
        extents = ctx.text_extents(text)
        ctx.rel_move_to(x * extents.width, y * extents.height)
        ctx.show_text(text)

    def _show_centered_text(self, ctx: cairo.Context, text, x, y):
        extents = ctx.text_extents(text)
        ctx.move_to(x - extents.width / 2, y)
        ctx.show_text(text)

    def get_engine(self):
        return self.engine

    def on_commit(self, im, str):
        self.engine.append(str)
        self.queue_draw()

    def on_delete_surrounding(self, im, offset, n_chars):
        self.engine.delete(offset, n_chars, reset=False)
        self.queue_draw()
        return True

    def on_draw(self, wid, ctx: cairo.Context):
        if self.engine.run(self.keyboard):
            GLib.timeout_add(100, self.timeout)
        if self.engine.get_mode() == EngineMode.EXIT:
            self.get_toplevel().destroy()
            return

        title = self.engine.get_title()
        if title:
            title += " – " + get_title()
        else:
            title = get_title()
        self.get_toplevel().set_title(title)

        self._clear(wid, ctx)
        if self.engine.get_mode() == EngineMode.SCORE:
            self._draw_score(wid, ctx)
        elif self.engine.get_mode() == EngineMode.PRACTICE:
            self._draw_practice(wid, ctx)
        elif self.engine.get_mode() == EngineMode.MENU:
            self._draw_menu(wid, ctx)
        elif self.engine.get_mode() == EngineMode.STATS:
            self._draw_stats(wid, ctx)

    def on_focus_in(self, wid, event):
        ime.check_engine()
        ime.set_mode(self.get_engine().get_ime_mode())
        self.im_context.focus_in()
        return True

    def on_focus_out(self, wid, event):
        self.im_context.focus_out()
        ime.restore_engine()
        return True

    def on_key_press(self, wid, event):
        logger.info("'%s', %08x", Gdk.keyval_name(event.keyval), event.state)
        self.engine.inc_touch_count(event, self.keyboard)
        if self.engine.get_mode() == EngineMode.MENU:
            try:
                n = (Gdk.KEY_1, Gdk.KEY_2, Gdk.KEY_3, Gdk.KEY_4, Gdk.KEY_5,
                     Gdk.KEY_6, Gdk.KEY_7, Gdk.KEY_8, Gdk.KEY_9, Gdk.KEY_0).index(event.keyval)
                if self.engine.select(n):
                    self.queue_draw()
                return True
            except ValueError:
                pass
        if self.im_context.filter_keypress(event):
            return True
        if event.keyval == Gdk.KEY_Escape:
            self.engine.escape()
            self.queue_draw()
            return True
        if event.keyval == Gdk.KEY_BackSpace:
            self.engine.backspace()
            self.queue_draw()
            return True
        if event.keyval == Gdk.KEY_Return:
            self.engine.enter(self.keyboard)
            self.queue_draw()
            return True
        if event.keyval == Gdk.KEY_F5:
            if self.engine.get_mode() == EngineMode.MENU:
                self.engine.show_stats()
                self.queue_draw()
            return True
        if event.keyval == Gdk.KEY_F2:
            if self.engine.get_mode() == EngineMode.STATS:
                self.engine.get_stats().reset()
                self.queue_draw()
            return True
        return False

    def on_key_release(self, wid, event):
        if self.im_context.filter_keypress(event):
            return True
        return False

    def on_preedit_changed(self, im):
        self.engine.set_preedit(self.im_context.get_preedit_string())
        self.queue_draw()
        return False

    def on_preedit_end(self, im):
        self.engine.set_preedit(self.im_context.get_preedit_string())
        self.queue_draw()
        return False

    def on_preedit_start(self, im):
        self.engine.set_preedit(self.im_context.get_preedit_string())
        self.queue_draw()
        return False

    def on_retrieve_surrounding(self, im):
        if self.engine.is_practice_mode():
            typed = self.engine.get_typed()
            length = len(typed.encode())
            self.im_context.set_surrounding(typed, length, length)
        else:
            self.im_context.set_surrounding('', 0, 0)
        return True

    def timeout(self):
        self.queue_draw()
        if self.engine.is_practice_mode():
            return True
        self.im_context.reset()
        return False


class TypingWindow(Gtk.ApplicationWindow):

    def __init__(self, filename='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_icon_name(package.get_name())
        self.set_default_size(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)
        self.headerbar.props.title = get_title()
        self.headerbar.props.show_close_button = True
        self.set_titlebar(self.headerbar)

        # See https://gitlab.gnome.org/GNOME/Initiatives/-/wikis/App-Menu-Retirement
        self.menu_button = Gtk.MenuButton()
        hamburger_icon = Gio.ThemedIcon(name="open-menu-symbolic")
        image = Gtk.Image.new_from_gicon(hamburger_icon, Gtk.IconSize.BUTTON)
        self.menu_button.add(image)
        builder = Gtk.Builder()
        builder.set_translation_domain(package.get_name())
        builder.add_from_file(os.path.join(os.path.dirname(__file__), 'menu.ui'))
        self.menu_button.set_menu_model(builder.get_object('app-menu'))
        self.menu_button.set_can_focus(False)
        self.headerbar.pack_end(self.menu_button)

        action = Gio.SimpleAction.new("menu", None)
        action.connect("activate", self.menu_callback)
        self.add_action(action)

        self.view = View()
        self.engine = self.view.get_engine()
        self.add(self.view)
        if filename:
            self.open(filename)
        self.show_all()

    def __del__(self):
        logger.info('TypingWindow.__del__')
        self.quit()

    def menu_callback(self, *whatever):
        self.menu_button.set_active(not self.menu_button.get_active())

    def open(self, filename):
        self.engine.open(filename)

    def quit(self):
        logger.info('TypingWindow.quit')
        self.engine.quit()
