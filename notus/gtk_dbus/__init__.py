#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 25-10-2020
           """


class Class:
    """
    Gtk Dbus Backend

    #TODO: NOT DONE!

    """

    def __init__(self):
        from notus.gtk_dbus.gtk_toaster import GtkToast

        self.toaster = GtkToast()

    def show(self, msg: str, threaded=None, **kwargs) -> None:
        """
        :param msg:
        :type msg:
        :param threaded:
        :type threaded:
        """
        from notus.gtk_dbus.gtk_toaster import init
        from notus import PROJECT_NAME

        init(PROJECT_NAME)
        self.toaster.show(msg, **kwargs)

    def __call__(self, msg: str, *, threaded: bool = True) -> None:
        """
        :param msg:
        :type msg:
        :param threaded:
        :type threaded:
        """
        pass


if __name__ == "__main__":
    print(Class.__doc__)

    Class().show("Hello World")
