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

from hurigana import get_plain_text
import package

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gdk

import operator
from datetime import date, datetime
from enum import Enum
import logging
import os
import random
import time

import ime

logger = logging.getLogger(__name__)

DELAY_FINISH = 1.0    # [seconds]
MAX_STATS_DAYS = 366 / 2
TIME_OVER = 59 * 60   # [seconds]

ZENKAKU = ''.join(chr(i) for i in range(0xff01, 0xff5f)) + '　￥'
HANKAKU = ''.join(chr(i) for i in range(0x21, 0x7f)) + ' ¥'

TO_HANKAKU = str.maketrans(ZENKAKU, HANKAKU)
TO_ZENKAKU = str.maketrans(HANKAKU, ZENKAKU)


def to_zenkaku(s: str):
    return s.translate(TO_ZENKAKU)


def to_hankaku(s: str):
    return s.translate(TO_HANKAKU)


class EngineMode(Enum):
    RUN = 1
    MENU = 2
    TEXT = 3
    HINT = 4
    PRACTICE = 5
    SCORE = 6
    STATS = 7
    EXIT = 8


class Stats:
    def __init__(self):
        datadir = package.get_user_datadir()
        os.makedirs(datadir, 0o700, True)
        os.chmod(datadir, 0o700)
        self.filename = os.path.join(datadir, 'stats.txt')
        stats = dict()
        today = date.today()
        self._reset_stats()
        try:
            with open(self.filename, 'r') as f:
                for line in f:
                    record = line.strip().split(',')
                    try:
                        t = datetime.strptime(record[0], '%Y-%m-%d %H:%M:%S')
                        if MAX_STATS_DAYS <= (datetime.today() - t).days:
                            continue
                        ms = record[2].split(':')
                        if len(ms) != 2:
                            continue
                        duration = int(ms[0]) * 60 + float(ms[1])
                        correct_count = int(record[3])
                        touch_count = int(record[4])
                        if touch_count < correct_count:
                            touch_count = correct_count
                        key = t.strftime('%Y-%m-%d')
                        if key not in stats:
                            stats[key] = (duration, correct_count, touch_count)
                        else:
                            stats[key] = list(map(operator.add, stats[key], (duration, correct_count, touch_count)))
                    except ValueError:
                        continue
                logger.info(stats)
                for item in sorted(stats.items()):
                    logger.info(item)
                    t = datetime.strptime(item[0], '%Y-%m-%d').date()
                    self._update(t, item[1][0], item[1][1], item[1][2])
                    if t == today:
                        self.today_duration = item[1][0]
                        self.today_correct_count = item[1][1]
                        self.today_touch_count = item[1][2]
                logger.info(self.stats)
        except FileNotFoundError:
            # TODO: Print the version number of the file format
            pass
        self.file = open(self.filename, mode='a')

    def __del__(self):
        self.close()

    def _reset_stats(self):
        self.max_wpm = 0
        self.max_duration = 0
        self.today_duration = 0
        self.today_correct_count = 0
        self.today_touch_count = 0
        self.stats = list()

    def close(self):
        logger.info("Stats closed")
        self.file.close()

    def reset(self):
        self._reset_stats()
        self.file = open(self.filename, mode='w')

    def _update(self, date, duration, correct_count, touch_count):
        wpm = int(correct_count * 60 / duration / 5)
        accuracy = round(correct_count / touch_count, 2)
        self.stats.append((date, duration, wpm, accuracy))
        if self.max_duration < duration:
            self.max_duration = duration
        if self.max_wpm < wpm:
            self.max_wpm = wpm

    def append(self, engine):
        t = datetime.now()
        duration = engine.get_duration()
        touch_count = engine.get_touch_count()
        correct_count = engine.get_correct_count()
        line = '{},"{}",{:02d}:{:04.1f},{:d},{:d}\n'.format(
            t.strftime('%Y-%m-%d %H:%M:%S'),
            engine.get_filename(),
            int(duration / 60), duration % 60,
            correct_count,
            touch_count)
        self.file.write(line)
        self.file.flush()
        # Update self.stats
        today = t.date()
        if touch_count < correct_count:
            touch_count = correct_count
        if not self.stats or self.stats[-1][0] != today:
            self.today_duration = duration
            self.today_touch_count = touch_count
            self.today_correct_count = correct_count
        else:
            self.stats.pop(-1)
            self.today_duration += duration
            self.today_touch_count += touch_count
            self.today_correct_count += correct_count
        self._update(today, self.today_duration, self.today_correct_count, self.today_touch_count)

    def get_stats(self):
        return self.stats

    def get_max_duration(self):
        return self.max_duration

    def get_max_wpm(self):
        return self.max_wpm


class Engine:
    def __init__(self, roomazi):
        self.roomazi = roomazi
        self.ime_mode = 'A'
        self.dirname = ''
        self.filename = ''
        self.lines = list()
        self.lineno = 0
        self.title = ''
        self.text = ''      # source text
        self.reading = ''
        self.plain = ''
        self.hint = ''
        self.correct_count = 0
        self.repeat = 0
        self.ramdom_list = list()
        self.mode = EngineMode.RUN
        self.show_keyboard = False
        self.reset_practice()
        self.menu = list()
        self.up_list = list()
        self.min_accuracy = 0.85
        self.min_WPM = 5
        self.stats = Stats()
        self.ignore = [Gdk.KEY_BackSpace, Gdk.KEY_Caps_Lock,
                       Gdk.KEY_Henkan, Gdk.KEY_Hiragana_Katakana,
                       Gdk.KEY_Shift_L, Gdk.KEY_Shift_R]

    def __del__(self):
        self.quit()

    def quit(self):
        if self.mode != EngineMode.EXIT:
            self.stats.close()
        self.mode = EngineMode.EXIT

    """
    3rd: 15 wpm, 85% accuracy
    5th: 30 wpm
    """
    def get_score(self):
        wpm = self.get_wpm()
        accuracy = self.min_accuracy + self.get_accuracy()
        if 1 < accuracy:
            accuracy = 1
        wpm *= accuracy
        score = int(wpm / self.min_WPM)
        if 10 < score:
            score = 10
        return score

    def reset_practice(self):
        self.typed = ''
        self.preedit = ('', None, 0)
        self.start_time = self.finish_time = 0
        self.touch_count = 0

    def open(self, filename):
        try:
            dirname = os.path.dirname(filename)
            if not dirname:
                path = self.dirname + '/' + filename
            else:
                self.dirname = dirname
                path = filename
            with open(path, 'r') as file:
                self.lineno = 0
                self.lines = file.readlines()
                self.show_keyboard = False
                self.text = ''
                self.hint = ''
                self.zenkaku = False
                self.reset_practice()
                self.mode = EngineMode.RUN
                self.filename = filename
        except:
            logger.error('"%s" was not found.', filename)

    def up(self):
        if not self.up_list:
            return
        if self.up_list[-1] != self.filename:
            filename = self.up_list.pop(-1)
        elif 1 < len(self.up_list):
            self.up_list.pop(-1)
            filename = self.up_list.pop(-1)
        else:
            filename = self.filename
        self.open(filename)
        logger.info("up: %s", filename)
        return

    def finish_practice(self, keyboard):
        self.stats.append(self)
        if self.repeat == 0:
            self.mode = EngineMode.RUN
            return True
        self.reset_practice()
        self.pick_text(keyboard)
        return False

    def pick_text(self, keyboard):
        self.text = ''
        while 0 < self.repeat:
            self.text += self.ramdom_list.pop(random.randrange(0, len(self.ramdom_list)))
            self.text += ' '
            self.repeat -= 1
        self.text = self.text.strip()
        self.plain, self.reading = get_plain_text(self.text)
        self.correct_count = keyboard.get_key_count(self.reading)
        self.repeat = 0

    def run(self, keyboard):
        if not self.lines:
            return False
        if self.mode == EngineMode.PRACTICE:
            if self.is_timeup():
                self.reset_practice()
                return False
            if not self.is_finished():
                return False
            if not self.finish_practice(keyboard):
                return False
        text = ''
        while self.mode in (EngineMode.RUN, EngineMode.TEXT, EngineMode.HINT):
            if len(self.lines) <= self.lineno:
                self.lineno = 0
            line = self.lines[self.lineno]
            if line and line[0] == ':':
                line = line.rstrip()
            self.lineno += 1

            if self.mode in (EngineMode.TEXT, EngineMode.HINT):
                if not line.startswith(':'):
                    text += line
                    continue
                text = text.rstrip()
                if self.mode == EngineMode.TEXT:
                    self.text = text
                    self.plain, self.reading = get_plain_text(text)
                    self.correct_count = keyboard.get_key_count(self.reading)
                else:
                    self.hint = text
                text = ''
                self.mode = EngineMode.RUN

            if line.startswith(":title "):
                self.title = line[len(":title "):].strip()
            elif line.startswith(":text"):
                self.mode = EngineMode.TEXT
                self.text = ''
            elif line.startswith(":hint"):
                self.mode = EngineMode.HINT
                self.hint = ''
            elif line.startswith(":ime_mode"):
                self.ime_mode = line[len(":ime_mode"):].strip()
                ime.set_mode(self.ime_mode)
            elif line.startswith(":keyboard"):
                self.show_keyboard = True
            elif line.startswith(":random"):
                n = line[len(":random"):].strip()
                self.ramdom_list = self.text.splitlines(False)
                if n:
                    self.repeat = min(max(1, int(n)), len(self.ramdom_list))
                else:
                    self.repeat = len(self.ramdom_list)
                self.pick_text(keyboard)
                self.reset_practice()
                self.mode = EngineMode.PRACTICE
                return True
            elif line.startswith(":start"):
                self.reset_practice()
                self.mode = EngineMode.PRACTICE
                return True
            elif line.startswith(":show_score"):
                self.mode = EngineMode.SCORE
                break
            elif line.startswith(":up"):
                self.up()
            elif line.startswith(":next"):
                filename = line[len(":next"):].strip()
                if filename:
                    self.open(filename)
                else:
                    try:
                        index = self.menu.index(self.filename) + 1
                        if len(self.menu) <= index:
                            self.up()
                        else:
                            filename = self.menu[index]
                            self.open(filename)
                    except ValueError:
                        self.up()
            elif line.startswith(":menu"):
                self.up_list.append(self.filename)
                self.menu = line[len(":menu"):].split()
                logger.info(self.up_list)
                self.mode = EngineMode.MENU
                break
            elif line.startswith(":zenkaku"):
                self.zenkaku = True
        return False

    def get_mode(self):
        return self.mode

    def is_practice_mode(self):
        return self.mode == EngineMode.PRACTICE

    def start_test(self):
        self.start_time = self.finish_time = time.monotonic()

    def get_text(self):
        return self.text

    def get_plain(self):
        return self.plain

    def get_hint(self):
        return self.hint

    def get_ime_mode(self):
        return self.ime_mode

    def get_typed(self):
        return self.typed

    def get_filename(self):
        return self.filename

    def get_title(self):
        return self.title

    def get_show_keyboard(self):
        return self.show_keyboard

    def is_empty(self):
        return not self.typed and self.preedit[2] <= 0

    # Count the number of typed characters
    def key_press(self, event):
        if event.state & Gdk.ModifierType.MODIFIER_RESERVED_25_MASK:
            return
        if not self.is_practice_mode():
            return
        if event.keyval not in self.ignore:
            self.touch_count += 1

    def get_touch_count(self):
        return self.touch_count

    def get_correct_count(self):
        return self.correct_count

    def get_error_count(self):
        missed = self.get_touch_count() - self.get_correct_count()
        if missed < 0:
            return 0
        return missed

    # Return corrected Characters Per Minute
    def get_cpm(self):
        count = self.get_correct_count()
        if self.get_touch_count() < count:
            count = self.get_touch_count()
        return count * 60 / self.get_duration()

    # Return corrected Words Per Minute
    def get_wpm(self):
        return int(self.get_cpm() / 5)

    def get_error_ratio(self):
        return self.get_error_count() / self.get_touch_count()

    def get_accuracy(self):
        return 1 - self.get_error_ratio()

    def select(self, n):
        if self.mode == EngineMode.MENU and n < len(self.menu):
            next = self.menu[n]
            if next == 'stats':
                self.show_stats()
                return True
            if next == 'up':
                self.up()
                return True
            if next == 'quit':
                self.quit()
                return True
            self.open(next)
            return True
        return False

    def backspace(self):
        if self.is_practice_mode() and self.typed:
            self.typed = self.typed[:-1]
            if self.is_empty():
                self.reset_practice()

    def escape(self):
        if self.mode == EngineMode.STATS:
            self.mode = EngineMode.RUN
        else:
            self.up()

    def enter(self, keyboard):
        if self.mode in (EngineMode.SCORE, EngineMode.STATS):
            self.mode = EngineMode.RUN
        elif self.mode == EngineMode.PRACTICE:
            if self.is_finished(no_wait=True):
                self.finish_practice(keyboard)
                return
            was_empty = self.is_empty()
            self.typed += '\n'
            if was_empty and not self.is_empty():
                self.start_test()

    def append(self, str):
        if self.is_practice_mode():
            was_empty = self.is_empty()
            if self.zenkaku:
                str = to_zenkaku(str)
            self.typed += str
            if was_empty and not self.is_empty():
                self.start_test()

    def delete(self, offset, n_chars, reset=True):
        begin = len(self.typed) + offset
        if begin < 0:
            return False
        end = begin + n_chars
        if len(self.typed) < end:
            return False
        self.typed = self.typed[:begin] + self.typed[end:]
        if self.is_empty() and reset:
            self.reset_practice()
        return True

    def get_preedit(self):
        return self.preedit

    def set_preedit(self, preedit):
        if self.is_practice_mode():
            was_empty = self.is_empty()
            self.preedit = preedit
            if self.is_empty():
                if not was_empty:
                    self.reset_practice()
            else:
                if was_empty:
                    self.start_test()

    def get_duration(self):
        if self.start_time <= 0:
            return 0
        if self.plain == self.typed and self.preedit[2] <= 0:
            if self.finish_time <= self.start_time:
                self.finish_time = time.monotonic()
            t = self.finish_time - self.start_time
        else:
            self.finish_time = self.start_time    # Reset finished state
            t = time.monotonic() - self.start_time
        return t

    def is_finished(self, no_wait=False):
        self.get_duration()
        if self.finish_time <= self.start_time:
            return False
        if no_wait:
            return True
        # Wait a few more seconds
        t = time.monotonic() - self.finish_time
        return DELAY_FINISH <= t

    def is_timeup(self):
        return TIME_OVER <= self.get_duration()

    def show_stats(self):
        assert self.mode == EngineMode.MENU
        self.mode = EngineMode.STATS
        self.title = ''

    def get_stats(self):
        return self.stats

    def markup(self, s: str):
        s = s.replace('<kbd>', '<span background="#00cc99" foreground="#FFFFFF">')
        s = s.replace('</kbd>', '</span>')
        return s
