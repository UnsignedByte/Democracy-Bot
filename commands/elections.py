import asyncio
import pickle
from demobot.utils import *
from demobot.handlers import add_message_handler, get_data
from discord import Embed


async def running(Demobot, msg, reg):
    await Demobot.send_message(msg.channel, "OKAY")

add_message_handler(running, r'I am running for (pres(?:ident)?|leader|rep(?:resentative)?)')
