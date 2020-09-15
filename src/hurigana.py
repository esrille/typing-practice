# typing-practice - Typing Practice
#
# Copyright (c) 2020 Esrille Inc.
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

import cairo
import logging
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, GLib, GObject, Pango, PangoCairo
import re


logger = logging.getLogger(__name__)

IAA = '\uFFF9'  # IAA (INTERLINEAR ANNOTATION ANCHOR)
IAS = '\uFFFA'  # IAS (INTERLINEAR ANNOTATION SEPARATOR)
IAT = '\uFFFB'  # IAT (INTERLINEAR ANNOTATION TERMINATOR)

PLAIN = 0
BASE = 1
RUBY = 2

HIRAGANA = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんゔがぎぐげござじずぜぞだぢづでどばびぶべぼぁぃぅぇぉゃゅょっぱぴぷぺぽゎゐゑ・ーゝゞ"
KATAKANA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンヴガギグゲゴザジズゼゾダヂヅデドバビブベボァィゥェォャュョッパピプペポヮヰヱ・ーヽヾ"
TO_HIRAGANA = str.maketrans(KATAKANA, HIRAGANA)


def get_plain_text(text: str):
    plain = ''
    reading = ''
    mode = PLAIN
    for c in text:
        if c == IAA:
            mode = BASE
        elif c == IAS:
            mode = RUBY
        elif c == IAT:
            mode = PLAIN
        elif mode == BASE:
            plain += c
        elif mode == RUBY:
            reading += c
        else:
            plain += c
            reading += c
    return plain, reading.translate(TO_HIRAGANA)


class HuriganaLayout:
    def __init__(self, ctx: cairo.Context):
        self.ctx = ctx
        self.layout = PangoCairo.create_layout(ctx)
        self.text = ''      # including rubies
        self.markup = ''    # including tags
        self.plain = ''
        self.rubies = list()
        self.ruby_size = 8

    def set_font_description(self, desc):
        self.font_description = desc
        self.layout.set_font_description(desc)

    def set_width(self, width):
        self.width = width
        self.layout.set_width(self.width * Pango.SCALE)

    def set_spacing(self, spacing):
        self.layout.set_spacing(spacing * Pango.SCALE)

    def set_text(self, text):
        self.text = text
        self.markup = ''
        self.plain = ''
        self.rubies.clear()
        mode = PLAIN
        i = pos = len = 0
        ruby = ''
        for c in self.text:
            if c == IAA:
                mode = BASE
                pos = i
            elif c == IAS:
                mode = RUBY
                len = i - pos
            elif c == IAT:
                mode = PLAIN
                self.rubies.append([pos, len, ruby, ''])
                ruby = ''
            elif mode == RUBY:
                ruby += c
            else:
                self.plain += c
                i += 1
        self.layout.set_text(self.plain, -1)

    def set_markup(self, text):
        self.text = text
        self.markup = ''
        self.plain = ''
        self.rubies.clear()
        mode = PLAIN
        i = pos = len = 0
        ruby = ''
        tag = ''
        in_open_tag = False
        in_close_tag = False
        for c in self.text:
            if c == IAA:
                mode = BASE
                pos = i
            elif c == IAS:
                mode = RUBY
                len = i - pos
            elif c == IAT:
                mode = PLAIN
                self.rubies.append([pos, len, ruby, tag])
                ruby = ''
            elif mode == RUBY:
                ruby += c
            else:
                self.markup += c
                if in_open_tag:
                    tag += c
                    if c == '>':
                        in_open_tag = False
                elif in_close_tag:
                    if c == '>':
                        in_close_tag = False
                elif c == '<':
                    if not tag:
                        in_open_tag = True
                        tag += c
                    else:
                        in_close_tag = True
                        tag = ''
                else:
                    self.plain += c
                    i += 1
        self.layout.set_markup(self.markup, -1)

    def set_ruby_size(self, size):
        self.ruby_size = size

    def _draw_rubies(self, offset_x, offset_y):
        lt = PangoCairo.create_layout(self.ctx)
        desc = self.font_description.copy_static()
        desc.set_size(self.ruby_size * Pango.SCALE)
        lt.set_font_description(desc)
        for pos, length, ruby, tag in self.rubies:
            text = self.plain[:pos]
            left = self.layout.index_to_pos(len(text.encode()))
            text = self.plain[:pos + length - 1]
            right = self.layout.index_to_pos(len(text.encode()))
            left.x /= Pango.SCALE
            left.y /= Pango.SCALE
            right.x += right.width
            right.x /= Pango.SCALE
            right.y /= Pango.SCALE
            if left.y == right.y:
                self.ctx.save()
                if tag:
                    ruby = tag + ruby + '</span>'
                lt.set_markup(ruby, -1)
                PangoCairo.update_layout(self.ctx, lt)
                w, h = lt.get_pixel_size()
                x = (left.x + right.x - w) / 2
                if x < 0:
                    x = 0
                elif self.width < x + w:
                    x = self.width - w
                y = left.y - h * 3 / 4
                self.ctx.move_to(offset_x + x, offset_y + y)
                PangoCairo.show_layout(self.ctx, lt)
                self.ctx.restore()
            else:
                ruby_width = (self.width - left.x) + right.x
                left_length = round(len(ruby) * (self.width - left.x) / ruby_width)
                if 0 < left_length:
                    text = ruby[:left_length]
                    self.ctx.save()
                    if tag:
                        text = tag + text + '</span>'
                    lt.set_markup(text, -1)
                    PangoCairo.update_layout(self.ctx, lt)
                    w, h = lt.get_pixel_size()
                    x = self.width - w
                    y = left.y - h * 3 / 4
                    self.ctx.move_to(offset_x + x, offset_y + y)
                    PangoCairo.show_layout(self.ctx, lt)
                    self.ctx.restore()
                if left_length < len(ruby):
                    text = ruby[left_length:]
                    self.ctx.save()
                    if tag:
                        text = tag + text + '</span>'
                    lt.set_markup(text, -1)
                    PangoCairo.update_layout(self.ctx, lt)
                    w, h = lt.get_pixel_size()
                    x = 0
                    y = right.y - h * 3 / 4
                    self.ctx.move_to(offset_x + x, offset_y + y)
                    PangoCairo.show_layout(self.ctx, lt)
                    self.ctx.restore()

    def draw(self, x, y):
        self.ctx.move_to(x, y)
        PangoCairo.update_layout(self.ctx, self.layout)
        PangoCairo.show_layout(self.ctx, self.layout)
        self._draw_rubies(x, y)

    def adjust_typed(self, typed):
        current = 0
        length = len(typed)
        if length < len(self.plain):
            length += 1
        adjusted = ''
        for i in range(length):
            index = len(self.plain[:i].encode())
            (line, x) = self.layout.index_to_line_x(index, False)
            if line != current and adjusted[-1] != '\n':
                adjusted += '\n' + self.plain[i]
            else:
                adjusted += self.plain[i]
            current = line
        if len(typed) < len(self.plain):
            adjusted = adjusted[:-1]
        return adjusted
