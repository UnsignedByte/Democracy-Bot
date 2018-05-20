import asyncio
import pickle
from demobot.utils import *
from demobot.handlers import add_message_handler, nested_get
from discord import Embed


async def running(Demobot, msg, reg):
    if nested_get(msg.server.id, "elections", "runnable"):
        print("yes")
    else:
        await Demobot.send_message(msg.channel, "You cannot run for positions right now! Wait until the next campaign phase before running.")

add_message_handler(running, r'I (?:(?:want|would like) to run|am running) for (pres(?:ident)?|leader|rep(?:resentative)?)$')
