import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, nested_get
from discord import Embed


async def running(Demobot, msg, reg):
    if nested_get(msg.server.id, "elections", "runnable"):
        print("yes")
    else:
        await Demobot.send_message(msg.channel, "You cannot run for positions right now! Wait until the next campaign phase before running.")

add_message_handler(running, r'I\s*(?:(?:want|would\s*like)\s*to\s*run|am\s*running)\s*for\s*(pres(?:ident)?|leader|rep(?:resentative)?)$')
