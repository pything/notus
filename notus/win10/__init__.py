#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 04-12-2020
           """


class Class:
    """
    Windows 10 Backend

    #TODO: NOT DONE!

    """

    def __init__(self):
        from notus.win10.win10_toaster import Win10Toaster

        self.toaster = Win10Toaster()

    def show(self, msg: str, **kwargs) -> None:
        """
        :param msg:
        :type msg:
        :param threaded:
        :type threaded:
        """
        self.toaster.show(msg, **kwargs)

    def __call__(self, msg: str, *, threaded: bool = True) -> None:
        """
        :param msg:
        :type msg:
        :param threaded:
        :type threaded:
        """
        pass

    def __repr__(self):
        return "Windows 10 Backend"

    def __str__(self):
        return "Windows 10 Backend"

    def __bool__(self):
        return True

    def __len__(self):
        return 1
