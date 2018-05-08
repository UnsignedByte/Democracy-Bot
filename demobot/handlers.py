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

print("\tLoaded files")

persistent_variables = {}

if not os.path.exists("data/data_backup/"):
    os.makedirs("data/data_backup/")

server_data = {}
if os.path.isfile("data/settings.txt"):
    with open("data/settings.txt", "rb") as f:
        server_data = pickle.load(f)
    copyfile("data/settings.txt", "data/data_backup/settings.txt")

def add_message_handler(handler, keyword):
    message_handlers[keyword] = handler
def add_private_message_handler(handler, keyword):
    private_message_handlers[keyword] = handler
def get_data():
    return [server_data]
#from https://stackoverflow.com/questions/13687924/setting-a-value-in-a-nested-python-dictionary-given-a-list-of-indices-and-value
def nested_set(value, *keys):
    dic = server_data
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value
def nested_get(*keys):
    dic = server_data
    for key in keys:
        dic=dic.setdefault( key, {} )
    return dic
print("Handler initialized")
print("Begin Command Initialization")
# Add modules here
from commands import *
import discord
print("Command Initialization Finished")

import asyncio
import re
from datetime import datetime, timedelta

async def on_message(Demobot, msg):
    if not msg.author.bot:
        if msg.author.status == discord.Status.offline:
            await Demobot.delete_message(msg)
            outm = await Demobot.send_message(msg.channel, "Hey! You shouldn't be speaking while invisible.")
            await asyncio.sleep(1)
            await Demobot.delete_message(outm)
        try:
            if msg.channel.is_private:
                await Demobot.send_message(msg.channel, "Demobot doesn't work in private channels")
            for a in message_handlers:
                reg = re.compile(a, re.I).search(msg.content)
                if reg:
                    await message_handlers[a](Demobot, msg, reg)
        except IndexError:
            em = discord.Embed(title="Missing Inputs", description="Not enough inputs provided.", colour=0xd32323)
            await send_embed(Demobot, msg, em)
        except (TypeError, ValueError):
            em = discord.Embed(title="Invalid Inputs", description="Invalid inputs provided.", colour=0xd32323)
            await send_embed(Demobot, msg, em)
        except discord.Forbidden:
            em = discord.Embed(title="Missing Permissions", description="Demobot is missing permissions to perform this task.", colour=0xd32323)
            await send_embed(Demobot, msg, em)
        except Exception as e:
            em = discord.Embed(title="Unknown Error", description="An unknown error occurred. Trace:\n%s" % e, colour=0xd32323)
            await send_embed(Demobot, msg, em)

async def timed_message(Demobot):
    currt = datetime.utcnow()
    nextelection = currt + timedelta( (2-currt.weekday()) % 7 + 1 )
    nextelection = nextelection.replace(hour=0, minute=0, second=0, microsecond=0)
    await asyncio.sleep((nextelection-currt).total_seconds())
    for a in server_data:
        chann = nested_get(a, "channels", "announcements")
        if chann:
            electionmsg = await Demobot.send_message(chann, "Hey @everyone! You may now run for positions in government!\nTo do so, type `I am running for (position)`. Remove the parentheses!")
        nested_set(electionmsg, a, "elections", "runnable")
    await asyncio.sleep(86400)
    for a in server_data:
        chann = nested_get(a, "channels", "announcements")
        if chann:
            electionmsg = await Demobot.send_message(chann, "Elections have started.")
        nested_set(electionmsg, a, "elections", "runnable")
