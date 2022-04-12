#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

            WIP: IS A BUGGY IMPLEMENTATION, IT GENERATES GARBAGE ICONS IN THE NOTIFICATION BAR!

           Created on 25-10-2020
           """

__all__ = ["Win10Toaster"]

import logging
from os import path, remove
from pathlib import Path
from random import randint
from threading import Thread
from time import sleep
from typing import Optional

from pkg_resources import Requirement, resource_filename

from notus import PROJECT_NAME
from notus.win10.extra_magic_windows_flags import PARAM_CLICKED, PARAM_DESTROY

try:
    from PIL import Image
except ImportError:
    Image = None

"""
CW_USEDEFAULT = -0x80000000
IDI_APPLICATION = 0x7f00
IMAGE_ICON = 0x1
LR_LOADFROMFILE = 0x16
LR_DEFAULTSIZE = 0x40
NIM_ADD = 0x0
NIM_MODIFY = 0x1
NIM_DELETE = 0x2
NIF_MESSAGE = 0x1
NIF_ICON = 0x2
NIF_TIP = 0x4
NIF_INFO = 0x10
WM_USER = 0x400
WS_OVERLAPPED = 0x0
WS_SYSMENU = 0x80000
"""

from winsound import SND_FILENAME, PlaySound

from win32api import (
    GetModuleHandle,
    PostQuitMessage,
)
from win32con import (
    BS_DEFPUSHBUTTON,
    CW_USEDEFAULT,
    IDI_APPLICATION,
    IMAGE_ICON,
    LR_DEFAULTSIZE,
    LR_LOADFROMFILE,
    WM_USER,
    WS_CHILD,
    WS_OVERLAPPED,
    WS_SYSMENU,
    WS_TABSTOP,
    WS_VISIBLE,
)
from win32gui import (
    CreateWindow,
    DestroyWindow,
    LoadIcon,
    LoadImage,
    NIF_ICON,
    NIF_INFO,
    NIF_MESSAGE,
    NIF_TIP,
    NIM_ADD,
    NIM_DELETE,
    NIIF_NOSOUND,
    NIM_MODIFY,
    RegisterClass,
    UnregisterClass,
    Shell_NotifyIcon,
    UpdateWindow,
    WNDCLASS,
    PumpMessages,
)
from pywintypes import error as WinTypesException


# Class


class Win10Toaster(object):
    """Create a Windows 10 toast notification.

    #TODO: Add progress bar notification type

    """

    def __init__(self):
        self._thread = None

    @staticmethod
    def _decorator(func: callable, callback: callable = None):
        """

        :param func:     callable to decorate
        :param callback: callable to run on mouse click within notification window
        :return:         callable
        """

        def inner(*args, **kwargs):
            """

            :param args:
            :param kwargs:
            """
            kwargs.update({"callback": callback})
            func(*args, **kwargs)

        return inner

    def _show_toast(
        self,
        title: str,
        msg: str = "No msg",
        icon_path: Path = None,
        duration: float = None,
        sound_path=None,
        callback_on_click: callable = None,
        tooltip: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Notification settings.

        :param title:     notification title
        :param msg:       notification message
        :param icon_path: path to the .ico file to custom notification
        :param duration:  delay in seconds before notification self-destruction, None for no-self-destruction
        :param sound_path: path to the .wav file to custom notification
        """

        self.duration = duration

        def callback():
            """description"""
            self.duration = 0

            if callback_on_click is not None:
                callback_on_click()

        if tooltip is None:
            tooltip = PROJECT_NAME

        # Register the window class.
        self.window_class = WNDCLASS()
        self.instance_handle = self.window_class.hInstance = GetModuleHandle(None)
        self.window_class.lpszClassName = f"{PROJECT_NAME}-{title}"  # must be a string
        self.window_class.lpfnWndProc = self._decorator(
            self.wnd_proc, callback
        )  # could instead specify simple mapping
        try:
            self.classAtom = RegisterClass(self.window_class)
        except Exception as e:
            logging.error("Some trouble with classAtom (%s)", e)
        style = WS_OVERLAPPED | WS_SYSMENU
        button_style = WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON  # TODO: Unused for now
        self.window_handle = CreateWindow(
            self.classAtom,
            "Taskbar",
            style,
            0,
            0,
            CW_USEDEFAULT,
            CW_USEDEFAULT,
            0,
            0,
            self.instance_handle,
            None,
        )
        UpdateWindow(self.window_handle)

        # icon
        new_name = ""
        if icon_path is not None:
            icon_path = path.realpath(icon_path)
            converted = False
            if Image is not None and icon_path.split(".")[-1] != ".ico":
                img = Image.open(icon_path)
                new_name = f'{str(icon_path.split(".")[:-1])}.ico'
                img.save(new_name)
                icon_path = new_name
                converted = True
        else:
            icon_path = resource_filename(
                Requirement.parse(PROJECT_NAME),
                str(Path(PROJECT_NAME) / "data" / "python.ico"),
            )
            converted = False
        try:
            hicon = LoadImage(
                self.instance_handle,
                icon_path,
                IMAGE_ICON,
                0,
                0,
                LR_LOADFROMFILE | LR_DEFAULTSIZE,
            )
            if Image and path.exists(new_name and converted):
                remove(new_name)
        except Exception as e:
            logging.error("Some trouble with the icon (%s): %s", icon_path, e)
            hicon = LoadIcon(0, IDI_APPLICATION)

        # Set the duration
        """
buff = create_unicode_buffer(10)
windll.user32.SystemParametersInfoW(SPI_GETMESSAGEDURATION, 0, buff, 0)
try:
oldlength = int(buff.value.encode("unicode_escape").decode().replace("\\", "0"), 16)
except ValueError:
oldlength = 5  # Default notification length

duration_output = windll.user32.SystemParametersInfoW(SPI_SETMESSAGEDURATION, 0, self.duration, SPIF_SENDCHANGE)
windll.user32.SystemParametersInfoW(SPI_GETMESSAGEDURATION, 0, buff, 0)

duration_error = False
try:
int(buff.value.encode("unicode_escape").decode().replace("\\", "0"), 16)
except ValueError:
duration_error = True

if duration_output == 0 or self.duration > 255 or duration_error:
windll.user32.SystemParametersInfoW(SPI_SETMESSAGEDURATION, 0, oldlength, SPIF_SENDCHANGE)
self.active = False
raise RuntimeError(f"Some trouble with the duration ({self.duration})"          ": Invalid duration length")
"""

        title += " " * randint(0, 63 - len(title))
        msg += " " * randint(0, 128 - len(msg))

        Shell_NotifyIcon(
            NIM_ADD,
            (
                self.window_handle,
                0,
                NIF_ICON | NIF_MESSAGE | NIF_TIP,
                WM_USER + 20,
                hicon,
                tooltip,
            ),
        )
        Shell_NotifyIcon(
            NIM_MODIFY,
            (
                self.window_handle,
                0,
                NIF_INFO,
                WM_USER + 20,
                hicon,
                tooltip,
                msg,
                200,
                title,
                0 if sound_path is None else NIIF_NOSOUND,
            ),
        )

        if sound_path is not None:  # play the custom sound
            sound_path = path.realpath(sound_path)
            if not path.exists(sound_path):
                logging.error(f"Some trouble with the sound file ({sound_path}): [Errno 2] No such file")

            try:
                PlaySound(sound_path, SND_FILENAME)
            except Exception as e:
                logging.error(f"Some trouble with the sound file ({sound_path}): {e}")

        PumpMessages()
        """
# Put the notification duration back to normal
SystemParametersInfoW(SPI_SETMESSAGEDURATION, 0, oldlength, SPIF_SENDCHANGE)
"""

        if duration is not None:  # take a rest then destroy
            # sleep(duration)
            while self.duration > 0:
                sleep(0.1)
                self.duration -= 0.1

            self.destroy_instance()
        self.active = False

    def destroy_instance(self):
        """description"""
        DestroyWindow(self.window_handle)
        UnregisterClass(self.window_class.lpszClassName, self.instance_handle)

        try:  # Sometimes the try icon sticks around until you click it - this should stop that
            Shell_NotifyIcon(NIM_DELETE, (self.window_handle, 0))
        except WinTypesException:
            pass

    def show(
        self,
        title: str,
        message: str = "No msg",
        *,
        icon_path: Optional[Path] = None,
        duration: Optional[float] = None,
        threaded: bool = False,
        callback_on_click: Optional[callable] = None,
        wait_for_active_notification: bool = True,
        tooltip: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Notification settings.

        :param tooltip:
        :param wait_for_active_notification:
        :param threaded:
        :param callback_on_click:
        :param title:     notification title
        :param message:       notification message
        :param icon_path: path to the .ico file to custom notification
        :param duration:  delay in seconds before notification self-destruction, None for no-self-destruction
        """
        args = title, message, icon_path, duration, None, callback_on_click, tooltip

        if not threaded:
            self._show_toast(*args)
        else:
            if (
                self.notification_active and wait_for_active_notification
            ):  # We have an active notification, let it finish we are not spamming
                # TODO: FIGURE OUT if sleeping here is a better solution
                return False

            self._thread = Thread(target=self._show_toast, args=args)
            self._thread.start()
        return True

    @property
    def notification_active(self) -> bool:
        """See if we have an active notification showing"""
        if self._thread is not None:
            if self._thread.is_alive():
                return True
            else:
                self.destroy_instance()
                self._thread.join()
                del self._thread
                self._thread = None
        return False

    def wnd_proc(self, hwnd, msg, wparam, lparam, **kwargs) -> None:
        """Messages handler method"""
        if lparam == PARAM_CLICKED:
            if kwargs.get("callback"):
                kwargs.pop("callback")()
            self.on_destroy(hwnd, msg, wparam, lparam)
        elif lparam == PARAM_DESTROY:
            self.on_destroy(hwnd, msg, wparam, lparam)

    def on_destroy(self, hwnd, msg, wparam, lparam) -> None:
        """Clean after notification ended."""
        self.destroy_instance()
        PostQuitMessage(0)


if __name__ == "__main__":

    def main():
        """description"""
        import time

        def p_callback():
            """description"""
            print("clicked toast")

        toaster = Win10Toaster()
        toaster.show("Hello World", "Python Here!", callback_on_click=p_callback, duration=3)
        toaster.show("Buh", "DOUBLE TROUBLE", duration=2)
        toaster.show(
            "Example two",
            "This notification is in it's own thread!",
            icon_path=None,
            duration=5,
            threaded=True,
        )
        toaster.show("Do it", "Good!", icon_path=None, duration=5, threaded=True)  # TODO: MAKE THIS APPEAR!

        while toaster.notification_active:  # Wait for threaded notification to finish
            time.sleep(0.1)

    main()
