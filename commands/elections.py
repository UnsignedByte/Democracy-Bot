import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, nested_get
from commands.utilities import save
from discord import Embed


async def running(Demobot, msg, reg):
    if nested_get(msg.server.id, "roles", 'citizen') in msg.author.roles and nested_get(msg.server.id, "prisoners", msg.author.id) < 1500:
        aliases = {
            'rep': 'representative',
            'representative': 'representative',
            'ld': 'leader',
            'pres': 'leader',
            'president': 'leader',
            'leader': 'leader'
        }
        if reg.group('pos') not in aliases:
            return
        dmm = await Demobot.send_message(msg.author, "DM me a description for " + aliases[reg.group('pos')] + ".")
        m = await Demobot.wait_for_message(timeout=600, author=msg.author, channel=dmm.channel)
        if not m:
            m = "*No description given*"
        else:
            m = m.content
        nested_set(m, msg.server.id, 'elections', aliases[reg.group('pos')], msg.author.id)
        await Demobot.send_message(msg.author, "Demobot actually does work in DM for candidacies! You are now running.")
        await save(None, None, None, overrideperms=True)
    else:
        await Demobot.send_message(msg.channel, "You must be a citizen and have less than four imprisonments in the " +
                                   "past term to run for office!")

add_message_handler(running, r'I\s*(?:(?:want|would\s*like)\s*to\s*run|am\s*running)\s*for\s*(?P<pos>.*?)\Z')
