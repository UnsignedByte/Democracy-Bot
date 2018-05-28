import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, nested_get, nested_pop, nested_remove
from commands.utilities import save
from discord import Embed

async def delete_data(Demobot, msg, reg):
    if msg.author.id == (await get_owner(Demobot)).id:
        keys = [msg.server.id] + reg.group('path').split()
        if isinstance(nested_get(*keys[:-1]), dict):
            nested_pop(*keys)
        elif isinstance(nested_get(*keys[:-1]), list):
            nested_remove(keys[-1], *keys[:-1])

add_message_handler(delete_data, r'(?:remove|delete) (?P<path>.*)\Z')
