#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 26-12-2020
           """

__all__ = ["notify", "JobNotificationSession"]

from warg import AlsoDecorator


def notify(msg: str, *, instance: callable = None, threaded: bool = True, **kwargs) -> None:
    """

    :param instance:
    :type instance:
    :param msg:
    :type msg:
    :param threaded:
    :type threaded:
    """
    if instance:
        instance.show(msg, threaded=threaded, **kwargs)
    else:
        notify_new_instance(msg, **kwargs)


def notify_new_instance(msg: str, *, threaded: bool = True, **kwargs) -> None:
    """

    :param msg:
    :type msg:
    :param threaded:
    :type threaded:
    """

    try:
        from .backend_selection import Class

        Class().show(msg, threaded=threaded, **kwargs)
    except Exception as e1:
        print(e1)
    finally:
        pass


class JobNotificationSession(AlsoDecorator):
    """
    # speed up evaluating after training finished
    """

    def __init__(self, job_id: str, instanced: bool = True, threaded: bool = False):
        self.job_id = job_id

        if not instanced:

            try:
                from notus.win10 import win10_toaster

                self.instance = win10_toaster.Win10Toaster()
            except Exception as e:
                try:
                    from notus.gtk_dbus import gtk_toaster

                    self.instance = gtk_toaster.GtkToast()
                except Exception as e1:
                    print(e, e1)
        else:
            self.instance = None
        self.threaded = threaded

    def __enter__(self):
        notify(f"{self.job_id} Started", instance=self.instance, threaded=self.threaded)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        notify(f"{self.job_id} Ended", instance=self.instance, threaded=self.threaded)
        del self.instance

    def __call__(self, *args, **kwargs):
        notify(
            f'{self.job_id} {"".join(args)} {"".join(kwargs.items())}',
            instance=self.instance,
            threaded=self.threaded,
        )


if __name__ == "__main__":
    notify("test")

    with JobNotificationSession("test2") as notifier:
        notifier("ass")
