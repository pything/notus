#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = """
Created on 27/04/2019

@author: cnheider
"""

import unittest

from warg import is_linux

if is_linux():
    from notus.gtk_dbus import gtk_toaster

    class ModuleTests(unittest.TestCase):
        """Test module level functions."""

        def setUp(self):
            """description"""
            gtk_toaster.init("toaster test suite")

        def test_init_uninit(self):
            assert gtk_toaster.is_initted()
            self.assertEqual(gtk_toaster.get_app_name(), "toaster test suite")

            gtk_toaster.de_init()
            assert not gtk_toaster.is_initted()

        def test_get_server_info(self):
            r = gtk_toaster.get_server_info()
            assert isinstance(r, dict), type(r)

        def test_get_server_caps(self):
            r = gtk_toaster.get_server_caps()
            assert isinstance(r, list), type(r)

    class NotificationTests(unittest.TestCase):
        """Test notifications."""

        def setUp(self):
            """description"""
            gtk_toaster.init("toaster test suite")

        def test_basic(self):
            n = gtk_toaster.GtkToast("Title", "Body")
            n.show()
            n.close()

        def test_icon(self):
            n = gtk_toaster.GtkToast("Title", "Body", icon="notification-message-im")
            n.show()
            n.close()

        def test_icon_only(self):
            if "x-canonical-private-icon-only" in gtk_toaster.get_server_caps():
                n = gtk_toaster.GtkToast("", "", icon="notification-device-eject")
                n.set_hint_string("x-canonical-private-icon-only", "true")
                n.show()

        def test_urgency(self):
            nl = gtk_toaster.GtkToast("Low", "")
            nl.set_urgency(gtk_toaster.URGENCY_LOW)
            nl.show()
            nl.close()

            nn = gtk_toaster.GtkToast("Normal", "")
            nn.set_urgency(gtk_toaster.URGENCY_NORMAL)
            nn.show()
            nn.close()

            nu = gtk_toaster.GtkToast("Urgent", "")
            nu.set_urgency(gtk_toaster.URGENCY_CRITICAL)
            nu.show()
            nu.close()

        def test_update(self):
            n = gtk_toaster.GtkToast("First message", "Some text", icon="notification-message-im")
            n.show()

            # The icon should stay the same with this
            n.update("Second message", "Some more text")
            n.show()

            # But this should replace the icon
            n.update(
                "Third message",
                "Yet more text, new icon.",
                icon="notification-message-email",
            )
            n.show()
            n.close()

        def test_category(self):
            n = gtk_toaster.GtkToast("Plain")
            n.set_category("im.received")
            n.show()
            n.close()

        def test_timeout(self):
            n = gtk_toaster.GtkToast("Plain")
            self.assertEqual(n.get_timeout(), gtk_toaster.EXPIRES_DEFAULT)
            n.set_timeout(gtk_toaster.EXPIRES_NEVER)
            self.assertEqual(n.get_timeout(), gtk_toaster.EXPIRES_NEVER)
            n.set_timeout(5000)
            self.assertEqual(n.get_timeout(), 5000)
            n.show()
            n.close()

        def test_data(self):
            n = gtk_toaster.GtkToast("Plain")
            n._data["a"] = 1
            n.set_data("b", 2)  # pynotify API
            n.show()
            self.assertEqual(n.get_data("a"), 1)  # pynotify API
            self.assertEqual(n._data["b"], 2)
            n.close()

        def test_icon_from_pixbuf(self):
            import gi

            gi.require_version("Gtk", "3.0")
            from gi.repository import Gtk

            helper = Gtk.Button()
            pb = helper.render_icon(Gtk.STOCK_DIALOG_INFO, Gtk.IconSize.DIALOG)

            # pb = GdkPixbuf.Pixbuf.new_from_file("examples/applet-critical.png")
            n = gtk_toaster.GtkToast("Icon", "Testing icon from pixbuf")
            n.set_icon_from_pixbuf(pb)
            n.show()
            n.close()

        def test_set_location(self):
            n = gtk_toaster.GtkToast("Location", "Test setting location")
            n.set_location(320, 240)
            n.show()
            n.close()


if __name__ == "__main__":
    unittest.main()
