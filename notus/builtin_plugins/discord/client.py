#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 16-04-2021
           """

import discord


class MyClient(discord.Client):
    async def on_ready(self):
        """description"""
        print("Logged on as", self.user)

    async def on_message(self, message):
        """

        :param message:
        :type message:
        :return:
        :rtype:
        """
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == "ping":
            await message.channel.send("pong")


client = MyClient()
client.run("token")
