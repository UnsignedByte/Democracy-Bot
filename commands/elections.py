import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, nested_get, nested_append
from commands.utilities import save
from discord import Embed

async def running(Demobot, msg, reg):
    if nested_get(msg.server.id, "roles", 'citizen') in msg.author.roles and (not nested_get(msg.server.id, "prisoners", msg.author.id) or nested_get(msg.server.id, "prisoners", msg.author.id) < 1500):
        aliases = {
        'rep':'representative',
        'representative':'representative',
        'ld':'leader',
        'pres':'leader',
        'president':'leader',
        'leader':'leader'
        }
        if reg.group('pos') not in aliases:
            return
        dmm = await Demobot.send_message(msg.author, "Please dm me a short description of what you want to do as "+aliases[reg.group('pos')]+".\nYou can change this at any time by typing ```change my description to:\nDescription Here```")
        m = await Demobot.wait_for_message(timeout=600, author=msg.author, channel=dmm.channel)
        if not m:
            m = "*No description given*"
        else:
            m = m.content
        nested_append(Candidate(msg.author, m), msg.server.id, "elections", "candidates", aliases[reg.group('pos')])
        await save(None, None, None, overrideperms=True)
    else:
        await Demobot.send_message(msg.channel, "You must be a citizen **and** have 3 or less imprisonments in the past term in order to run for office!")

async def nominate(Demobot, msg, reg):
    if nested_get(msg.server.id, "roles", 'leader') in msg.author.roles :
        aliases = {
        'judge':'judge',
        'j':'judge',
        'jd':'judge'
        }
        if reg.group('pos') not in aliases:
            return

        m = await Demobot.wait_for_message(timeout=600, author=msg.author, channel=dmm.channel)
        if not m:
            m = "*No description given*"
        else:
            m = m.content
        nested_append(Candidate(msg.author, m), msg.server.id, "elections", "candidates", aliases[reg.group('pos')])
        await save(None, None, None, overrideperms=True)
    else:
        await Demobot.send_message(msg.channel, "You must be a citizen **and** have 3 or less imprisonments in the past term in order to run for office!")

add_message_handler(running, r'I\s*(?:(?:want|would\s*like)\s*to\s*run|am\s*running)\s*for\s*(?P<pos>.*?)\Z')
