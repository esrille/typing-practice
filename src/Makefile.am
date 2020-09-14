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

typing_practice_PYTHON = \
	application.py \
	chart.py \
	engine.py \
	hurigana.py \
	ime.py \
	keyboard.py \
	roomazi.py \
	main.py \
	window.py \
	menu.ui \
	$(NULL)
BUILT_SOURCES = package.py
nodist_typing_practice_PYTHON = package.py
typing_practice_DATA = \
	menu.ui \
	$(NULL)
typing_practicedir = $(pkgdatadir)/src

bin_SCRIPTS = esrille-typing-practice

desktop_DATA = esrille-typing-practice.desktop
desktopdir = $(datadir)/applications

CLEANFILES = \
	esrille-typing-practice \
	esrille-typing-practice.desktop \
	esrille-typing-practice.in \
	package.py \
	package.py.in \
	$(NULL)

EXTRA_DIST = \
	esrille-typing-practice.desktop.in \
	esrille-typing-practice.in.in \
	package.py.in.in \
	$(NULL)

package.py: package.py.in
	$(AM_V_GEN) \
	( \
		pkgdatadir=${pkgdatadir}; \
		localedir=${localedir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

esrille-typing-practice: esrille-typing-practice.in
	$(AM_V_GEN) \
	( \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

esrille-typing-practice.desktop: esrille-typing-practice.desktop.in
	$(AM_V_GEN) \
	( \
		libexecdir=${libexecdir}; \
		pkgdatadir=${pkgdatadir}; \
		s=`cat $<`; \
		eval "echo \"$${s}\""; \
	) > $@

uninstall-hook:
	-rmdir $(typing_practicedir)/__pycache__
	-rmdir $(typing_practicedir)
