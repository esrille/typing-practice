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
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, Gdk

from window import TypingWindow

import gettext
import logging
import os


logger = logging.getLogger(__name__)
_ = lambda a : gettext.dgettext(package.get_name(), a)


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="com.esrille.typing",
            **kwargs
        )
        self.window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("help", None)
        action.connect("activate", self.on_help)
        self.add_action(action)
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)
        self.set_accels_for_action("app.help", ["F1"])
        self.set_accels_for_action("app.quit", ["<Primary>q"])

    def do_activate(self):
        if not self.window:
            filename = os.path.join(package.get_datadir(), 'lessons/menu.txt')
            self.window = TypingWindow(application=self, filename=filename)
            self.cursor = Gdk.Cursor.new_from_name(self.window.get_display(), "default")
        self.window.present()

    def do_window_removed(self, window):
        logger.info('do_window_removed')
        window.quit()
        self.quit()

    def on_help(self, *args):
        url = "file://" + os.path.join(package.get_datadir(), "help/index.html")
        Gtk.show_uri_on_window(self.window, url, Gdk.CURRENT_TIME)
        if self.window:
            # see https://gitlab.gnome.org/GNOME/gtk/-/issues/1211
            self.window.get_window().set_cursor(self.cursor)

    def on_about(self, action, param):
        dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        dialog.set_program_name(_("Typing Practice"))
        dialog.set_copyright("Copyright 2020 Esrille Inc.")
        dialog.set_authors(["Esrille Inc."])
        dialog.set_documenters(["Esrille Inc."])
        dialog.set_website("file://" + os.path.join(package.get_datadir(), "help/index.html"))
        dialog.set_website_label(_("Introduction to Typing Practice"))
        dialog.set_logo_icon_name(package.get_name())
        dialog.set_version(package.get_version())
        dialog.present()
        # To close the dialog when "close" is clicked, e.g. on Raspberry Pi OS,
        # the "response" signal needs to be connected about_response_callback
        dialog.connect("response", self.about_response_callback)
        dialog.show()

    def about_response_callback(self, dialog, response):
        dialog.destroy()

    def on_quit(self, *args):
        if self.window:
            self.window.quit()
        self.quit()
