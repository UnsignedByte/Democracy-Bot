import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, server_data
from discord import Embed

@asyncio.coroutine
def role(Demobot, msg, reg):
    perms = msg.channel.permissions_for(msg.author)
    if perms.manage_server:
        if msg.server.id not in server_data:
            server_data[msg.server.id] = 
        yield from Demobot.send_message(msg.channel, reg.group('name'))
add_message_handler(role, r'make\s*(<@&[0-9]*>|@everyone)\s*a\s*(?P<name>leader|president|judge|enforcer|rep(?:resentative)?)\s*role')
