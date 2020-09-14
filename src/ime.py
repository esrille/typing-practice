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

from gi import require_version
require_version('IBus', '1.0')
from gi.repository import IBus


logger = logging.getLogger(__name__)

default_engine = ''


def check_engine():
    global default_engine
    try:
        bus = IBus.Bus()
        engine = bus.get_global_engine()
        default_engine = engine.get_name()
        logger.info("check_engine %s", default_engine)
        if default_engine == 'hiragana':
            return
        bus.set_global_engine('hiragana')
    except Exception as e:
        logger.error(str(e))


def restore_engine():
    global default_engine
    if default_engine == 'hiragana':
        return
    try:
        logger.info("restore_engine %s", default_engine)
        bus = IBus.Bus()
        bus.set_global_engine(default_engine)
    except Exception as e:
        logger.error(str(e))
