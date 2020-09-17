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

import logging

logger = logging.getLogger(__name__)

KANA_TO_ROOMAZI = {
    "あ": "a",
    "い": "i",
    "う": "u",
    "え": "e",
    "お": "o",
    "か": "ka",
    "き": "ki",
    "きゃ": "kya",
    "きゅ": "kyu",
    "きょ": "kyo",
    "く": "ku",
    "け": "ke",
    "こ": "ko",
    "が": "ga",
    "ぎ": "gi",
    "ぎゃ": "gya",
    "ぎゅ": "gyu",
    "ぎょ": "gyo",
    "ぐ": "gu",
    "げ": "ge",
    "ご": "go",
    "さ": "sa",
    "し": "si",
    "しゃ": "sya",
    "しゅ": "syu",
    "しょ": "syo",
    "す": "su",
    "せ": "se",
    "そ": "so",
    "ざ": "za",
    "じ": "zi",
    "じゃ": "zya",
    "じゅ": "zyu",
    "じょ": "zyo",
    "ず": "zu",
    "ぜ": "ze",
    "ぞ": "zo",
    "た": "ta",
    "ち": "ti",
    "ちゃ": "tya",
    "ちゅ": "tyu",
    "ちょ": "tyo",
    "つ": "tu",
    "て": "te",
    "と": "to",
    "だ": "da",
    "ぢ": "di",
    "ぢゃ": "dya",
    "ぢゅ": "dyu",
    "ぢょ": "dyo",
    "づ": "du",
    "で": "de",
    "ど": "do",
    "な": "na",
    "に": "ni",
    "にゃ": "nya",
    "にゅ": "nyu",
    "にょ": "nyo",
    "ぬ": "nu",
    "ね": "ne",
    "の": "no",
    "は": "ha",
    "ひ": "hi",
    "ひゃ": "hya",
    "ひゅ": "hyu",
    "ひょ": "hyo",
    "ふ": "hu",
    "へ": "he",
    "ほ": "ho",
    "ば": "ba",
    "び": "bi",
    "びゃ": "bya",
    "びゅ": "byu",
    "びょ": "byo",
    "ぶ": "bu",
    "べ": "be",
    "ぼ": "bo",
    "ぱ": "pa",
    "ぴ": "pi",
    "ぴゃ": "pya",
    "ぴゅ": "pyu",
    "ぴょ": "pyo",
    "ぷ": "pu",
    "ぺ": "pe",
    "ぽ": "po",
    "ま": "ma",
    "み": "mi",
    "みゃ": "mya",
    "みゅ": "myu",
    "みょ": "myo",
    "む": "mu",
    "め": "me",
    "も": "mo",
    "や": "ya",
    "ゆ": "yu",
    "よ": "yo",
    "ら": "ra",
    "り": "ri",
    "りゃ": "rya",
    "ゆゅ": "ryu",
    "りょ": "ryo",
    "る": "ru",
    "れ": "re",
    "ろ": "ro",
    "わ": "wa",
    "を": "wo",
    "ん": "n",

    "んあ": "n'",
    "んい": "n'",
    "んう": "n'",
    "んえ": "n'",
    "んお": "n'",
    "んや": "n'",
    "んゆ": "n'",
    "んよ": "n'",

    "ぁ": "xa",
    "ぃ": "xi",
    "ぅ": "xu",
    "ぇ": "xe",
    "ぉ": "xo",
    "っ": "xtu",
    "ゃ": "xya",
    "ゅ": "xyu",
    "ょ": "xyo",

    "っか": "k",
    "っき": "k",
    "っく": "k",
    "っけ": "k",
    "っこ": "k",
    "っが": "g",
    "っぎ": "g",
    "っぐ": "g",
    "っげ": "g",
    "っご": "g",
    "っさ": "s",
    "っし": "s",
    "っす": "s",
    "っせ": "s",
    "っそ": "s",
    "っざ": "z",
    "っじ": "z",
    "っず": "z",
    "っぜ": "z",
    "っぞ": "z",
    "った": "t",
    "っち": "t",
    "っつ": "t",
    "って": "t",
    "っと": "t",
    "っだ": "d",
    "っぢ": "d",
    "っづ": "d",
    "っで": "d",
    "っど": "d",
    "っは": "h",
    "っひ": "h",
    "っふ": "h",
    "っへ": "h",
    "っほ": "h",
    "っば": "b",
    "っび": "b",
    "っぶ": "b",
    "っべ": "b",
    "っぼ": "b",
    "っぱ": "p",
    "っぴ": "p",
    "っぷ": "p",
    "っぺ": "p",
    "っぽ": "p",
    "っま": "m",
    "っみ": "m",
    "っむ": "m",
    "っめ": "m",
    "っも": "m",
    "っや": "y",
    "っゆ": "y",
    "っよ": "y",
    "っら": "r",
    "っり": "r",
    "っる": "r",
    "っれ": "r",
    "っろ": "r",
    "っわ": "w",
    "っを": "w",

    "ー": "-",
    "、": ",",
    "。": ".",
    "「": "[",
    "」": "]",
    "『": "{",
    "』": "}",
    "・": "/",
}

KANA_TO_ROOMAZI_X4063 = {
    "んな": "n'",
    "んに": "n'",
    "んぬ": "n'",
    "んね": "n'",
    "んの": "n'",
}

ZENKAKU = "".join(chr(0xff01 + i) for i in range(94))
HANKAKU = "".join(chr(0x21 + i) for i in range(94))

ZENKAKU_TO_HANKAKU = str.maketrans(ZENKAKU, HANKAKU)
HANKAKU_TO_ZENKAKU = str.maketrans(HANKAKU, ZENKAKU)
TO_TYOUON = str.maketrans('aiueo', 'âîûêô')
TO_PLAIN = str.maketrans('âîûêô', 'aiueo')


class Roomazi:
    def __init__(self):
        self.x4063 = True

    def get_roomazi(self, s):
        c, r = self.get_roomazi_without_tyouon(s)
        s = s[len(c):]
        if s and s[0] == 'ー' and r and r[-1] in 'aiueo':
            c += 'ー'
            r = r[:-1] + r[-1].translate(TO_TYOUON)
        return c, r

    def get_roomazi_without_tyouon(self, s):
        if not s:
            return '', ''
        p = ''
        c = ''
        roomazi = ''
        if 2 <= len(s):
            s = s[:2]
            if s in KANA_TO_ROOMAZI:
                roomazi = KANA_TO_ROOMAZI[s]
            elif self.x4063 and s in KANA_TO_ROOMAZI_X4063:
                roomazi = KANA_TO_ROOMAZI_X4063[s]
            if roomazi:
                if roomazi == "n'":
                    return 'ん', roomazi
                if s[0] == 'っ':
                    p = 'っ'
                    s = s[1:]
                else:
                    return s, roomazi
        c = s[0]
        if c in KANA_TO_ROOMAZI:
            roomazi += KANA_TO_ROOMAZI[c]
            if roomazi == 'n':
                next = self.get_roomazi(s[1:])
                c += next[0]
                roomazi += next[1]
            return p + c, roomazi
        if c in ZENKAKU:
            return c, c.translate(ZENKAKU_TO_HANKAKU)
        if c == '\n':
            return '⏎', '⏎'
        return c, c

    def hyphenize(self, roomazi):
        hyphenized = ''
        for c in roomazi:
            if c in 'âîûêô':
                c = c.translate(TO_PLAIN) + '-'
            hyphenized += c
        return hyphenized

    def romanize(self, s):
        r = ''
        while s:
            pair = self.get_roomazi(s)
            s = s[len(pair[0]):]
            r += pair[1]
        return r

    def set_x4063(self, value: bool):
        self.x4063 = value
        logger.info('x4063: %d', value)
