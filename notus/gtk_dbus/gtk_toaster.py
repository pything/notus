#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""Based on the notifications spec at: http://developer.gnome.org/notification-spec/ 
         
            Created on 25-10-2020
           """
__all__ = ["GtkToast"]

import time
from typing import Optional, Union, MutableMapping

from warg import sink, is_linux

try:
    if is_linux():
        import gi

        gi.require_version("Gtk", "3.0")
        gi.require_version("GdkPixbuf", "2.0")
        from gi.repository import GdkPixbuf

        import dbus
    else:
        raise ImportError("Notus is not running on Linux, so it cannot use the GTK D-Bus interface.")
except ModuleNotFoundError as e:
    import sys
    from warnings import warn

    warn(f"gi not found, maybe use another implementation fitting for your system: {sys.platform}")
    raise e

EXPIRES_DEFAULT = -1
EXPIRES_NEVER = 0

URGENCY_LOW = 0
URGENCY_NORMAL = 1
URGENCY_CRITICAL = 2
urgency_levels = [URGENCY_LOW, URGENCY_NORMAL, URGENCY_CRITICAL]

IS_SETUP = False
APP_NAME = f"unnamed_app_{time.time()}"
HAVE_MAINLOOP = False

NOTIFICATIONS_REGISTRY = {}


def action_callback(nid, action, notifications_registry) -> None:
    """

    callback for when a notification action is invoked.

    :param nid:
    :type nid:
    :param action:
    :type action:
    :param notifications_registry:
    :type notifications_registry:
    :return:
    :rtype:
    """
    nid, action = int(nid), str(action)
    try:
        n = notifications_registry[nid]
    except KeyError:  # this message was created through some other program.
        return
    n.action_callback(action, notifications_registry)


def closed_callback(nid, reason, notifications_registry) -> None:
    """
    callback for when a notification is closed.

    :param nid:
    :type nid:
    :param reason:
    :type reason:
    :param notifications_registry:
    :type notifications_registry:
    :return:
    :rtype:
    """
    nid, reason = int(nid), int(reason)
    try:
        n = notifications_registry[nid]
    except KeyError:  # this message was created through some other program.
        return
    n.closed_callback(n)
    del notifications_registry[nid]


# TODO: Object orient globals!
class UnconstructedDbusObject(object):
    """A dummy object to represent the D-Bus interface."""

    class NotSetupError(RuntimeError):
        """Error raised if you try to communicate with the server before calling
        :func:`init`."""

        pass

    def __getattr__(self, name):
        raise UnconstructedDbusObject.NotSetupError("You must call toaster.init() first")


dbus_interface = UnconstructedDbusObject()  # For when init has not been called yet.


def init(app_name, mainloop=None):
    """Initialise the D-Bus connection. Must be called before you send any
    notifications, or retrieve server info or capabilities.

    To get callbacks from notifications, DBus must be integrated with a mainloop.
    There are three ways to achieve this:

    - Set a default mainloop (dbus.set_default_main_loop) before calling init()
    - Pass the mainloop parameter as a string 'glib' or 'qt' to integrate with
    those main loops. (N.B. passing 'qt' currently makes that the default dbus
    mainloop, because that's the only way it seems to work.)
    - Pass the mainloop parameter a DBus compatible mainloop instance, such as
    dbus.mainloop.glib.DBusGMainLoop().

    If you only want to display notifications, without receiving information
    back from them, you can safely omit mainloop."""
    global APP_NAME, IS_SETUP, dbus_interface, HAVE_MAINLOOP

    if mainloop == "glib":
        from dbus.mainloop.glib import DBusGMainLoop

        mainloop = DBusGMainLoop()
    elif mainloop == "qt":
        from dbus.mainloop.qt import DBusQtMainLoop

        # For some reason, this only works if we make it the default mainloop
        # for dbus. That might make life tricky for anyone trying to juggle two
        # event loops, but I can't see any way round it.
        mainloop = DBusQtMainLoop(set_as_default=True)

    bus = dbus.SessionBus(mainloop=mainloop)

    dbus_obj = bus.get_object("org.freedesktop.Notifications", "/org/freedesktop/Notifications")
    dbus_interface = dbus.Interface(dbus_obj, dbus_interface="org.freedesktop.Notifications")
    APP_NAME = app_name
    IS_SETUP = True

    if mainloop or dbus.get_default_main_loop():
        HAVE_MAINLOOP = True
        dbus_interface.connect_to_signal("ActionInvoked", action_callback)
        dbus_interface.connect_to_signal("NotificationClosed", closed_callback)

    return True


def is_initted():
    """Has init() been called? Only exists for compatibility with pynotify."""
    return IS_SETUP


def get_app_name():
    """Return appname. Only exists for compatibility with pynotify."""
    return APP_NAME


def de_init():
    """Undo what init() does."""
    global IS_SETUP, dbus_interface, HAVE_MAINLOOP
    IS_SETUP = False
    HAVE_MAINLOOP = False
    dbus_interface = UnconstructedDbusObject()


# Retrieve basic server information --------------------------------------------


def get_server_caps():
    """Get a list of server capabilities.

    These are short strings, listed `in the spec
    <http://people.gnome.org/~mccann/docs/notification-spec/notification-spec-latest.html#commands>`_.
    Vendors may also list extra capabilities with an 'x-' prefix, e.g. 'x-canonical-append'."""
    return [str(x) for x in dbus_interface.GetCapabilities()]


def get_server_info():
    """Get basic information about the server."""
    res = dbus_interface.GetServerInformation()
    return {
        "name": str(res[0]),
        "vendor": str(res[1]),
        "version": str(res[2]),
        "spec-version": str(res[3]),
    }


class GtkToast(object):
    """A notification object.

    summary : str
    The title text
    message : str
    The body text, if the server has the 'body' capability.
    icon : str
    Path to an icon image, or the name of a stock icon. Stock icons available
    in Ubuntu are `listed here <https://wiki.ubuntu.com/NotificationDevelopmentGuidelines
    #How_do_I_get_these_slick_icons>`_.
    You can also set an icon from data in your application - see
    :meth:`set_icon_from_pixbuf`."""

    notification_id = 0
    _timeout = -1  # -1 = server default settings
    _closed_callback = sink

    def __init__(
        self,
        title: str = "No title",
        body: Optional[str] = "No msg",
        *,
        icon: Optional[Union[str, GdkPixbuf.Pixbuf]] = "",
        **kwargs,
    ):
        self.title = title
        self.body = body
        self._hints = {}

        if isinstance(icon, GdkPixbuf.Pixbuf):
            self.icon = ""
            self.set_hint("icon_data", icon)
        else:
            self.icon = icon

        self._actions = {}
        self._data = {}  # Any data the user wants to attach

    def show(self, msg: Optional[str] = None, title: Optional[str] = None, **kwargs: MutableMapping):
        """Ask the server to show the notification.

        Call this after you have finished setting any parameters of the
        notification that you want."""

        self.update(body=msg, title=title, **kwargs)

        nid = dbus_interface.Notify(
            APP_NAME,  # app_name       (spec names)
            self.notification_id,  # replaces_id
            self.icon,  # app_icon
            self.title,  # summary
            self.body,  # body
            self._make_actions_array(),  # actions
            self._hints,  # hints
            self._timeout,  # expire_timeout
        )

        self.notification_id = int(nid)

        if HAVE_MAINLOOP:
            NOTIFICATIONS_REGISTRY[self.notification_id] = self
        return True

    def update(
        self,
        title: str = None,
        body: Optional[str] = None,
        *,
        icon: Optional[Union[str, GdkPixbuf.Pixbuf]] = None,
    ):
        """Replace the summary and body of the notification, and optionally its
        icon. You should call :meth:`show` again after this to display the
        updated notification."""
        if title is not None:
            self.title = title
        if body is not None:
            self.body = body
        if icon is not None:
            self.icon = icon

    def close(self):
        """Ask the server to close this notification."""
        if self.notification_id != 0:
            dbus_interface.CloseNotification(self.notification_id)

    def set_hint(self, key, value):
        """n.set_hint(key, value) <--> n.hints[key] = value

        See `hints in the spec <http://people.gnome.org/~mccann/docs/notification-spec/notification-spec-latest
        .html#hints>`_.

        Only exists for compatibility with pynotify."""
        self._hints[key] = value

    set_hint_string = set_hint_int32 = set_hint_double = set_hint

    def set_hint_byte(self, key, value):
        """Set a hint with a dbus byte value. The input value can be an
        integer or a bytes string of length 1."""
        self._hints[key] = dbus.Byte(value)

    def set_urgency(self, level):
        """Set the urgency level to one of URGENCY_LOW, URGENCY_NORMAL or
        URGENCY_CRITICAL."""
        if level not in urgency_levels:
            raise ValueError("Unknown urgency level specified", level)
        self.set_hint_byte("urgency", level)

    def set_category(self, category):
        """Set the 'category' hint for this notification.

        See `categories in the spec <http://people.gnome.org/~mccann/docs/notification-spec/notification-spec
        -latest.html#categories>`_."""
        self._hints["category"] = category

    def set_timeout(self, timeout):
        """Set the display duration in milliseconds, or one of the special
        values EXPIRES_DEFAULT or EXPIRES_NEVER. This is a request, which the
        server might ignore.

        Only exists for compatibility with pynotify; you can simply set::

        n.timeout = 5000"""
        if not isinstance(timeout, int):
            raise TypeError("timeout value was not int", timeout)
        self._timeout = timeout

    def get_timeout(self):
        """Return the timeout value for this notification.

        Only exists for compatibility with pynotify; you can inspect the
        timeout attribute directly."""
        return self._timeout

    def add_action(self, action, label, callback, user_data=None):
        """Add an action to the notification.

        Check for the 'actions' server capability before using this.

        action : str
        A brief key.
        label : str
        The text displayed on the action button
        callback : callable
        A function taking at 2-3 parameters: the Notification object, the
        action key and (if specified) the user_data.
        user_data :
        An extra argument to pass to the callback."""
        self._actions[action] = (label, callback, user_data)

    def _make_actions_array(self):
        """Make the actions array to send over DBus."""
        arr = []
        for action, (label, callback, user_data) in self._actions.items():
            arr.append(action)
            arr.append(label)
        return arr

    def _action_callback(self, action):
        """Called when the user selects an action on the notification, to
        dispatch it to the relevant user-specified callback."""
        try:
            label, callback, user_data = self._actions[action]
        except KeyError:
            return

        if user_data is None:
            callback(self, action)
        else:
            callback(self, action, user_data)

    def connect(self, event, callback):
        """Set the callback for the notification closing; the only valid value
        for event is 'closed' (the parameter is kept for compatibility with pynotify).

        The callback will be called with the :class:`Notification` instance."""
        if event != "closed":
            raise ValueError("'closed' is the only valid value for event", event)
        self._closed_callback = callback

    def set_data(self, key, value):
        """n.set_data(key, value) <--> n.data[key] = value

        Only exists for compatibility with pynotify."""
        self._data[key] = value

    def get_data(self, key):
        """n.get_data(key) <--> n.data[key]

        Only exists for compatibility with pynotify."""
        return self._data[key]

    def set_icon_from_pixbuf(self, icon):
        """Set a custom icon from a GdkPixbuf."""
        self._hints["icon_data"] = self._get_icon_struct(icon)

    @staticmethod
    def _get_icon_struct(icon):
        return (
            icon.get_width(),
            icon.get_height(),
            icon.get_rowstride(),
            icon.get_has_alpha(),
            icon.get_bits_per_sample(),
            icon.get_n_channels(),
            dbus.ByteArray(icon.get_pixels()),
        )

    def set_location(self, x, y):
        """Set the notification location as (x, y), if the server supports it."""
        if (not isinstance(x, int)) or (not isinstance(y, int)):
            raise TypeError("x and y must both be ints", (x, y))
        self._hints["x"] = x
        self._hints["y"] = y


if __name__ == "__main__":

    def main():
        """description"""
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        init("Test")

        helper = Gtk.Button()
        a_icon = helper.render_icon(Gtk.STOCK_DIALOG_INFO, Gtk.IconSize.DIALOG)

        t = GtkToast("Title", "Body")
        t.set_icon_from_pixbuf(a_icon)
        for i in range(10):
            t.title = f"Title{i}"
            t.body = f"Body{i}"
            t.show()
            time.sleep(0.1)
            if i == 4:
                a_icon = helper.render_icon(Gtk.STOCK_DIALOG_QUESTION, Gtk.IconSize.DIALOG)
                t.set_icon_from_pixbuf(a_icon)

    main()
