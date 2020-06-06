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
import math

logger = logging.getLogger(__name__)


class Chart:

    def __init__(self, context: cairo.Context, x, y, width, height):
        self.ctx = context
        self.orig_x = x
        self.orig_y = y
        self.width = width
        self.height = height
        self.set_x_range(0, width)
        self.set_y_range(0, height)

    def set_x_range(self, min, max):
        self.x_min = min
        self.x_max = max
        self.x_mag = self.width / (max - min)

    def set_y_range(self, min, max):
        self.y_min = min
        self.y_max = max
        self.y_mag = self.height / (max - min)

    def _plot_x(self, x):
        return self.x_mag * (x - self.x_min)

    def _plot_y(self, y):
        return self.y_mag * (y - self.y_min)

    def _begin_plot(self):
        self.ctx.save()
        self.ctx.translate(self.orig_x, self.orig_y + self.height)
        self.ctx.scale(1, -1)
        self.ctx.new_path()

    def _end_plot(self):
        self.ctx.restore()

    def axis(self, step_x=0, step_y=0):
        self._begin_plot()
        if step_y <= 0:
            step_y = self.height
        if step_x <= 0:
            step_x = self.width
        y = 0
        while y <= self.height + step_y / 2:
            self.ctx.move_to(0, y)
            self.ctx.rel_line_to(self.width, 0)
            self.ctx.stroke()
            y += step_y
        x = 0
        while x <= self.width + step_x / 2:
            self.ctx.move_to(x, 0)
            self.ctx.rel_line_to(0, self.height)
            self.ctx.stroke()
            x += step_x
        self._end_plot()

    def line(self, data: list):
        self._begin_plot()
        if 1 < len(data):
            step = self.width / (len(data) - 1)
        else:
            step = self.width
        x = 0
        for y in data:
            self.ctx.line_to(x, self._plot_y(y))
            x += step
        self.ctx.stroke()
        self._end_plot()

    def dot(self, data: list, r):
        self._begin_plot()
        if 1 < len(data):
            step = self.width / (len(data) - 1)
        else:
            step = self.width
        x = 0
        for y in data:
            self.ctx.arc(x, self._plot_y(y), r, 0, 2 * math.pi)
            self.ctx.fill()
            x += step
        self._end_plot()

    def bar(self, data: list):
        self._begin_plot()
        width = self.width / len(data)
        self.ctx.save()
        self.ctx.set_line_width(width)
        x = 0
        for y in data:
            self.ctx.move_to(x + width / 2, 0)
            self.ctx.rel_line_to(0, self._plot_y(y))
            self.ctx.stroke()
            x += width
        self.ctx.restore()
        self._end_plot()

    def scatter_line(self, data: list):
        self._begin_plot()
        for (x, y) in data:
            self.ctx.line_to(self._plot_x(x), self._plot_y(y))
        self.ctx.stroke()
        self._end_plot()

    def scatter_dot(self, data: list, r):
        self._begin_plot()
        for (x, y) in data:
            self.ctx.arc(self._plot_x(x), self._plot_y(y), r, 0, 2 * math.pi)
            self.ctx.fill()
        self._end_plot()
