#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""Toast a message"""

__all__ = ["main"]


from notus import notify


def main():
    """
    parse arguments and run the application
    toaster.py -m "message" -t "title" -a "app"
    """

    import argparse

    parser = argparse.ArgumentParser(description="Toast a message")
    parser.add_argument("-m", "--message", required=True, type=str, help="Message to toast")
    parser.add_argument("-t", "--title", type=str, help="Title of toast")
    args = parser.parse_args()

    notify(msg=args.message, title=args.title)


if __name__ == "__main__":

    main()
