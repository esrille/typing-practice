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

import package

import gi
from gi.repository import GLib

GLib.set_prgname(package.get_name())

from application import Application

import gettext
import locale
import logging
import os
import sys


logger = logging.getLogger(__name__)
_ = lambda a : gettext.dgettext(package.get_name(), a)


if __name__ == '__main__':
    os.umask(0o077)
    try:
        locale.bindtextdomain(package.get_name(), package.get_localedir())
    except Exception:
        pass
    gettext.bindtextdomain(package.get_name(), package.get_localedir())
    logging.basicConfig(level=logging.DEBUG)
    app = Application()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
