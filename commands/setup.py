import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler
from discord import Embed

@asyncio.coroutine
def role(Demobot, msg):
    yield from Demobot.send_message(msg.channel, "hi")
add_message_handler(role, r'make\s*(<@&[0-9]*>|@everyone)\s*a\s*(leader|president|judge|enforcer|rep(?:resentative)?)\s*role')
