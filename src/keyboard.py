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

from roomazi import Roomazi

import cairo
import json
import logging
import math

from gi import require_version
from gi.repository import Gdk, Gio


logger = logging.getLogger(__name__)

BASE_KEY = "org.freedesktop.ibus.engine.hiragana"

"""
LAYOUT_104 = ((100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200),
              (150, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 150),
              (175, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 225),
              (225, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 275),
              (125, 125, 125, 625, 125, 125, 125, 125))
LAYOUT_109 = ((100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100),
              (150, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 150),
              (175, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 125),
              (225, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 175),
              (150, 125, 125, 150, 250, 150, 125, 100, 100, 100, 125))
"""

DAKU = 'がぎぐげござじずぜぞだぢづでどばびぶべぼゔ'
NON_DAKU = 'かきくけこさしすせそたちつてとはひふへほう'

HANDAKU = 'ぱぴぷぺぽ'
NON_HANDALU = 'はひふへほ'

KOGAKI = 'ぁぃぅぇぉゃゅょっ'
NON_KOGAKI = 'あいうえおやゆよつ'

DAKU_TO_NON_DAKU = str.maketrans(DAKU, NON_DAKU)
HANDAKU_TO_NON_HANDAKU = str.maketrans(HANDAKU, NON_HANDALU)
KOGAKI_TO_NON_KOGAKI = str.maketrans(KOGAKI, NON_KOGAKI)


class Keyboard:
    LAYOUT_104 = \
        (((100, '`', '~'), (100, '1', '!'), (100, '2', '@'), (100, '3', '#'), (100, '4', '$'), (100, '5', '%'),
          (100, '6', '^'), (100, '7', '&'), (100, '8', '*'), (100, '9', '('), (100, '0', ')'), (100, '-', '_'),
          (100, '=', '+'), (200, '⌫', '')),
         ((150, '⇥', ''), (100, 'q', 'Q'), (100, 'w', 'W'), (100, 'e', 'E'), (100, 'r', 'R'), (100, 't', 'T'),
          (100, 'y', 'Y'), (100, 'u', 'U'), (100, 'i', 'I'), (100, 'o', 'O'), (100, 'p', 'P'),
          (100, '[', '{'), (100, ']', '}'), (150, '\\', '|')),
         ((175, '⇪', ''), (100, 'a', 'A'), (100, 's', 'S'), (100, 'd', 'D'), (100, 'f', 'F'), (100, 'g', 'G'),
          (100, 'h', 'H'), (100, 'j', 'J'), (100, 'k', 'K'), (100, 'l', 'L'), (100, ';', ':'),
          (100, '\'', '"'), (225, '⏎', '')),
         ((225, '⇧', ''), (100, 'z', 'Z'), (100, 'x', 'X'), (100, 'c', 'C'), (100, 'v', 'V'), (100, 'b', 'B'),
          (100, 'n', 'N'), (100, 'm', 'M'), (100, ',', '<'), (100, '.', '>'), (100, '/', '?'), (275, '⇧', '')),
         ((125, '⌃', ''), (125, '❖', ''), (125, '⌥', ''), (625, ' ', ''),
          (125, '⌥', ''), (125, '❖', ''), (125, '☰', ''), (125, '⌃', '')))
    LAYOUT_109 = \
        (((100, '🌍', ''), (100, '1', '!'), (100, '2', '"'), (100, '3', '#'), (100, '4', '$'), (100, '5', '%'),
          (100, '6', '&'), (100, '7', '\''), (100, '8', '('), (100, '9', ')'), (100, '0', '_'), (100, '-', '='),
          (100, '^', '~'), (100, '¥', '|'), (100, '⌫', '')),
         ((150, '⇥', ''), (100, 'q', 'Q'), (100, 'w', 'W'), (100, 'e', 'E'), (100, 'r', 'R'), (100, 't', 'T'),
          (100, 'y', 'Y'), (100, 'u', 'U'), (100, 'i', 'I'), (100, 'o', 'O'), (100, 'p', 'P'),
          (100, '@', '`'), (100, '[', '{'), (150, '⏎', '')),
         ((175, '⇪', ''), (100, 'a', 'A'), (100, 's', 'S'), (100, 'd', 'D'), (100, 'f', 'F'), (100, 'g', 'G'),
          (100, 'h', 'H'), (100, 'j', 'J'), (100, 'k', 'K'), (100, 'l', 'L'), (100, ';', '+'),
          (100, ':', '*'), (100, ']', '}')),
         ((225, '⇧', ''), (100, 'z', 'Z'), (100, 'x', 'X'), (100, 'c', 'C'), (100, 'v', 'V'), (100, 'b', 'B'),
          (100, 'n', 'N'), (100, 'm', 'M'), (100, ',', '<'), (100, '.', '>'), (100, '/', '?'), (100, '\\', '_'),
          (175, '⇧', '')),
         ((150, '⌃', ''), (125, '❖', ''), (125, '⌥', ''), (150, '無変換', ''), (250, ' ', ''),
          (150, '変換', ''), (125, 'カタカナ', ''),
          (100, '⌥', ''), (100, '❖', ''), (100, '☰', ''), (125, '⌃', '')))
    KEYVAL_MAP = {
        '⌃': 'Control_',
        '❖': 'Super_',
        '⌥': 'Alt_',
        '⇧': 'Shift_',
    }
    R = 8
    L = 100
    S = 5
    DEG = math.pi / 180

    def __init__(self, roomazi: Roomazi):
        self.roomazi = roomazi
        self.config = Gio.Settings.new(BASE_KEY)
        self.load_keyboard_layout()
        self.roomazi.set_x4063(self.config.get_boolean('nn-as-jis-x-4063'))

    def _draw_key(self, ctx, x, y, w, h, s, r, legend=''):
        self.round_rect(ctx, x + s, y + s, w - 2 * s, h - 2 * s, r)
        ctx.fill()
        if legend:
            ext = ctx.text_extents(legend)
            ctx.move_to(x + (w - ext[4]) / 2, y + (h + ext[3]) / 2)
            ctx.save()
            ctx.set_source_rgb(255, 255, 255)
            ctx.show_text(legend.upper())
            ctx.restore()

    # Is column the [Enter] key that spans two rows?
    def _is_uk_enter(self, column):
        return column[1] == '⏎' and column[0] == 150

    def _load_kana_layout(self, path):
        try:
            with open(path) as f:
                ime_layout = json.load(f)
            space = ime_layout.get('Space')
            prefix = ime_layout.get('Prefix', False)
            if prefix:
                self.ignore.append(Gdk.KEY_space)
            henkan = ime_layout.get('Henkan')
            if henkan:
                henkan = Gdk.keyval_from_name(henkan)
                self.ignore.append(henkan)
                henkan = chr(henkan)
            muhenkan = ime_layout.get('Muhenkan')
            if muhenkan:
                muhenkan = chr(Gdk.keyval_from_name(muhenkan))
            underscore = ''
            if ime_layout.get('Type') == 'Kana':
                for r in self.layout:
                    row = list()
                    index = 0
                    for c in r:
                        n = c[1]
                        s = c[2].lower()
                        keyval = Keyboard.KEYVAL_MAP.get(n, '')
                        if keyval:
                            if 4 <= index:
                                keyval += 'R'
                            else:
                                keyval += 'L'
                        if s == '_':
                            # Ignore the 2nd underscore
                            if underscore:
                                s = ''
                            else:
                                underscore = '_'
                        if space == keyval:
                            n = '\u3000'
                        if n == ' ' and prefix:
                            n = '⇧'
                            s = ''
                        elif n == '⇧' and prefix:
                            n = ''
                        elif n in (henkan, muhenkan):
                            n = ''
                        elif n in ime_layout['Normal']:
                            n = ime_layout['Normal'][n]
                        if s in (henkan, muhenkan):
                            s = ''
                        elif s in ime_layout['Shift']:
                            s = ime_layout['Shift'][s]
                        self.kogaki = self.kogaki.replace(n, '')
                        self.kogaki = self.kogaki.replace(s, '')
                        row.append((c[0], n, s))
                        index += 1
                    self.kana_layout.append(row)
        except:
            logger.error('Could not load:', path)
            self.kana_layout = list()
            self.kogaki = KOGAKI

    def _load_roomazi_layout(self, path):
        try:
            with open(path) as f:
                ime_layout = json.load(f)
                layout = list()
                space = ime_layout.get('Space')
                henkan = ime_layout.get('Henkan')
                if henkan:
                    henkan = Gdk.keyval_from_name(henkan)
                    self.ignore.append(henkan)
                    henkan = chr(henkan)
                for r in self.layout:
                    row = list()
                    index = 0
                    for c in r:
                        n = c[1]
                        s = c[2].lower()
                        keyval = Keyboard.KEYVAL_MAP.get(n, '')
                        if keyval:
                            if 4 <= index:
                                keyval += 'R'
                            else:
                                keyval += 'L'
                        if n == henkan:
                            n = ''
                        if space == keyval:
                            n = ' '
                        if ime_layout['Roomazi'].get(n, '') == '\u3000':
                            n = ' '
                        row.append((c[0], n, s))
                        index += 1
                    layout.append(row)
                self.roomazi_layout = layout
        except:
            logger.error('Could not load:', path)

    def draw(self, ctx: cairo.Context, x, y, next: str):
        self.load_keyboard_layout()
        if next and next[0].isascii():
            self.draw_with_hint(ctx, x, y, self.layout, next[0])
            pair = (next[0], next[0])
        elif self.is_roomazi():
            pair = self.roomazi.get_roomazi(next)
            hint = pair[1]
            hint = hint.replace('\u3000', ' ')
            self.draw_with_hint(ctx, x, y, self.roomazi_layout, hint)
        else:
            pair = self.get_kana(next)
            self.draw_with_hint(ctx, x, y, self.kana_layout, pair[1])
        return pair

    def draw_with_hint(self, ctx: cairo.Context, x, y, layout, hint=''):
        if self.is_roomazi():
            hint = self.roomazi.hyphenize(hint)
        ctx.move_to(x, y)
        ctx.set_line_width(1)
        ctx.set_line_join(cairo.LineJoin.ROUND)
        scale = 0.4
        orig_x = x
        orig_y = y
        h = Keyboard.L * scale
        r = Keyboard.R * scale
        s = Keyboard.S * scale
        shift = list()
        shift_left = False
        shift_right = False
        alt = list()
        index_raw = 0
        fingers = list()
        for raw in layout:
            index_column = 0
            for column in raw:
                if column[1] == '⇧':
                    shift.append((x, y, column))
                if column[1] == '⌥':
                    alt.append((x, y, column))
                w = column[0] * scale
                color = self.get_key_color(index_column)
                if index_raw <= 0 or 4 <= index_raw:
                    color = (0x99, 0x99, 0x99)
                ctx.set_source_rgb(*[c / 255 for c in color])
                if self._is_uk_enter(column):
                    self.uk_enter(ctx, x, y, w, h, s, r)
                else:
                    self.round_rect(ctx, x + s, y + s, w - 2 * s, h - 2 * s, r)
                ctx.stroke()
                for c in hint:
                    if c in column[1]:
                        if index_raw < 4:
                            fingers.append(index_column)
                        if c == '\u3000':
                            c = "空白"
                        self._draw_key(ctx, x, y, w, h, s, r, c)
                    elif c in column[2]:
                        if index_raw < 4:
                            fingers.append(index_column)
                        self._draw_key(ctx, x, y, w, h, s, r, c)
                        if index_column <= 5:
                            shift_right = True
                        else:
                            shift_left = True
                x += w
                index_column += 1
            index_raw += 1
            x = orig_x
            y += h
        if shift_right:
            if 2 <= len(shift):
                self._draw_key(ctx, shift[1][0], shift[1][1], shift[1][2][0] * scale, h, s, r, 'シフト')
            else:
                self._draw_key(ctx, shift[0][0], shift[0][1], shift[0][2][0] * scale, h, s, r, 'シフト')
        if shift_left:
            self._draw_key(ctx, shift[0][0], shift[0][1], shift[0][2][0] * scale, h, s, r, 'シフト')

        # draw fingers
        if 5 in fingers:
            fingers.append(4)
        if 6 in fingers:
            fingers.append(7)
        metrics = [(1, 25, 8), (2, 45, 10), (3, 60, 10), (4, 45, 10), (7, 45, 10), (8, 60, 10), (9, 45, 10), (10, 25, 8)]
        x = orig_x - 100
        y = orig_y + 4.5 * Keyboard.L * scale
        for m in metrics:
            r = m[2]
            ctx.set_source_rgb(*[c / 255 for c in (0x99, 0x99, 0x99)])
            ctx.move_to(x, y)
            y -= m[1]
            ctx.line_to(x, y)
            ctx.arc(x + r, y, r, -180 * Keyboard.DEG, 0 * Keyboard.DEG)
            y += m[1]
            x += 2 * r
            ctx.line_to(x, y)
            ctx.stroke()
            if m[0] in fingers:
                color = self.get_key_color(m[0])
                ctx.set_source_rgb(*[c / 255 for c in color])
                ctx.arc(x - r, y - m[1] + 1, r * 0.8, 0 * Keyboard.DEG, 360 * Keyboard.DEG)
                ctx.fill()
            if m[0] != 4:
                x += 5
            else:
                ctx.set_source_rgb(*[c / 255 for c in (0x99, 0x99, 0x99)])
                # draw thumbs
                ctx.move_to(x, y)
                y += 30
                ctx.line_to(x, y)
                x += 20
                y -= 5
                ctx.line_to(x, y)
                ctx.arc(x, y + r, r, -90 * Keyboard.DEG, 90 * Keyboard.DEG)
                y += 2 * r
                x -= 20
                y += 5
                ctx.line_to(x, y)

                x = orig_x + 1500 * scale + 7
                y = orig_y + 4.5 * Keyboard.L * scale

                ctx.move_to(x, y)
                y += 30
                ctx.line_to(x, y)
                x -= 20
                y -= 5
                ctx.line_to(x, y)
                ctx.arc_negative(x, y + r, r, -90 * Keyboard.DEG, 90 * Keyboard.DEG)
                y += 2 * r
                x += 20
                y += 5
                ctx.line_to(x, y)

                x = orig_x + 1500 * scale + 7

            y = orig_y + 4.5 * Keyboard.L * scale

    def get_kana(self, s):
        if not s:
            return '', ''
        c = s[0]
        if c == '\n':
            return '⏎', '⏎'
        elif c in DAKU:
            c = c.translate(DAKU_TO_NON_DAKU)
            c += '゛'
        elif c in HANDAKU:
            c = c.translate(HANDAKU_TO_NON_HANDAKU)
            c += '゜'
        elif c in self.kogaki:
            c = c.translate(KOGAKI_TO_NON_KOGAKI)
            c += '゛'
        return s[0], c

    def get_key_color(self, column):
        return {
            1: (0x00, 0x66, 0xff),
            2: (0x99, 0xcc, 0x33),
            3: (0xff, 0x99, 0x33),
            4: (0xff, 0x33, 0x33),
            5: (0xff, 0x33, 0x33),
            6: (0xff, 0x33, 0x33),
            7: (0xff, 0x33, 0x33),
            8: (0xff, 0x99, 0x33),
            9: (0x99, 0xcc, 0x33),
            10: (0x00, 0x66, 0xff),
        }.get(column, (0x99, 0x99, 0x99))

    def get_key_count(self, reading: str):
        if self.is_roomazi():
            reading = self.roomazi.hyphenize(self.roomazi.romanize(reading))
            count = len(reading)
            if reading and reading[-1] == 'n':
                count += 1
        else:
            r = ''
            while reading:
                pair = self.get_kana(reading)
                reading = reading[len(pair[0]):]
                r += pair[1]
            count = len(r)
        return count

    def is_ignore(self, event):
        if event.keyval in self.ignore:
            return True
        return False

    def is_roomazi(self):
        return not self.kana_layout

    def load_keyboard_layout(self):
        path = self.config.get_string('layout')
        if path.endswith('.109.json'):
            self.layout = Keyboard.LAYOUT_109
        else:
            self.layout = Keyboard.LAYOUT_104
        self.roomazi_layout = list()
        self.kana_layout = list()
        self.kogaki = KOGAKI
        self.ignore = [Gdk.KEY_VoidSymbol]
        if "roomazi" in path:
            self._load_roomazi_layout(path)
        else:
            self._load_kana_layout(path)

    def round_rect(self, ctx, x, y, w, h, r):
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -90 * Keyboard.DEG, 0 * Keyboard.DEG)
        ctx.arc(x + w - r, y + h - r, r, 0 * Keyboard.DEG, 90 * Keyboard.DEG)
        ctx.arc(x + r, y + h - r, r, 90 * Keyboard.DEG, 180 * Keyboard.DEG)
        ctx.arc(x + r, y + r, r, 180 * Keyboard.DEG, 270 * Keyboard.DEG)
        ctx.close_path()

    def uk_enter(self, ctx, x, y, w, h, s, r):
        x1 = x + s
        y1 = y + s
        w1 = w - 2 * s
        h1 = h - 2 * s
        x2 = x + w * (25 / 150) + s
        h2 = h1 + h
        ctx.new_path()
        ctx.arc(x1 + w1 - r, y1 + r, r, -90 * Keyboard.DEG, 0 * Keyboard.DEG)
        ctx.arc(x1 + w1 - r, y1 + h2 - r, r, 0 * Keyboard.DEG, 90 * Keyboard.DEG)
        ctx.arc(x2 + r, y1 + h2 - r, r, 90 * Keyboard.DEG, 180 * Keyboard.DEG)
        ctx.arc_negative(x2 - r, y1 + h1 + r, r, 0 * Keyboard.DEG, -90 * Keyboard.DEG)
        ctx.arc(x1 + r, y1 + h1 - r, r, 90 * Keyboard.DEG, 180 * Keyboard.DEG)
        ctx.arc(x1 + r, y1 + r, r, 180 * Keyboard.DEG, 270 * Keyboard.DEG)
        ctx.close_path()
