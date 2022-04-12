#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 16-04-2021
           """

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix=">")


@bot.command()
# discord.py reads the typehints and converts the arguments accordingly
async def reply(ctx, member: discord.Member, *, text: str):  # ctx is always passed
    """

    :param ctx:
    :type ctx:
    :param member:
    :type member:
    :param text:
    :type text:
    """
    await ctx.send(f"{member.mention}! {text}")


bot.run("token")
