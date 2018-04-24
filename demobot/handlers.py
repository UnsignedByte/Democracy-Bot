from random import randint
import os
import pickle
from demobot.utils import *
from datetime import date
from shutil import copyfile

print("Begin Handler Initialization")

message_handlers = {}
private_message_handlers = {}

print("\tBegin Loading Files")
closing = False


print("\tLoaded files")

persistent_variables = {}

def add_message_handler(handler, keyword):
    message_handlers[keyword] = handler
def add_private_message_handler(handler, keyword):
    private_message_handlers[keyword] = handler

print("Handler initialized")
print("Begin Command Initialization")
# Add modules here
from commands import *
import discord
print("Command Initialization Finished")

import asyncio
import re

whitespace = [' ', '\t', '\n']

@asyncio.coroutine
def on_message(Demobot, msg):
    if not msg.author.bot:
        try:
            if msg.channel.is_private:
                yield from Demobot.send_message(msg.channel, "Demobot doesn't work in private channels")
            for a in message_handlers:
                if re.compile(a, re.I).match(msg.content):
                    yield from Demobot.send_message(msg.channel, '`'+msg.content+'`')
        except IndexError:
            em = discord.Embed(title="Missing Inputs", description="Not enough inputs provided for **%s**." % parse_command(msg.content)[0], colour=0xd32323)
            yield from send_embed(Demobot, msg, em)
        except (TypeError, ValueError):
            em = discord.Embed(title="Invalid Inputs", description="Invalid inputs provided for **%s**." % parse_command(msg.content)[0], colour=0xd32323)
            yield from send_embed(Demobot, msg, em)
        except discord.Forbidden:
            em = discord.Embed(title="Missing Permissions", description="Demobot is missing permissions to perform this task.", colour=0xd32323)
            yield from send_embed(Demobot, msg, em)
        except Exception as e:
            em = discord.Embed(title="Unknown Error", description="An unknown error occurred. Trace:\n%s" % (parse_command(msg.content)[0], e), colour=0xd32323)
            yield from send_embed(Demobot, msg, em)
