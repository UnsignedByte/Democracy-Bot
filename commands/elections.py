import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, nested_get
from commands.utilities import save
from discord import Embed

async def running(Demobot, msg, reg):
    if nested_get(msg.server.id, "roles", 'citizen') in msg.author.roles and nested_get(msg.server.id, "roles", "prisoner") not in msg.author.roles:
        aliases = {
        'rep':'representative',
        'representative':'representative',
        'ld':'leader',
        'pres':'president',
        'president':'president',
        'leader':'leader'
        }
        if reg.group('pos') not in aliases:
            return
        dmm = await Demobot.send_message(msg.author, "Please dm me a short description of what you want to do as "+aliases[reg.group('pos')]+".\nYou can change this at any time by typing ```change my description to:\nDescription Here```")
        m = await Discow.wait_for_message(timeout=600, author=msg.author, channel=dmm.channel)
        if not m:
            m = "*No description given*"
        else:
            m = m.content
        nested_set(m, msg.server.id, "elections", "running", msg.author)
        await save(None, None, None, overrideperms=True)
    else:
        await Demobot.send_message(msg.channel, "You must be an unimprisoned citizen in order to run for office!")

add_message_handler(running, r'I\s*(?:(?:want|would\s*like)\s*to\s*run|am\s*running)\s*for\s*(?P<pos>.*?)\Z')
