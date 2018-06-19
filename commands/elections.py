import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, nested_get, nested_set, nested_pop
from commands.utilities import save
from discord import Embed


async def running(Demobot, msg, reg):
    if nested_get(msg.guild.id, "roles", 'citizen') in msg.author.roles:
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
        dmm = await msg.author.send("DM me a description for " + aliases[reg.group('pos')] + ".")
        def check(m):
            return m.author == msg.author and m.channel == dmm.channel
        m = await Demobot.wait_for('message', timeout=600, check=check)
        if not m:
            m = "*No description given*"
        else:
            m = m.content
        nested_pop(msg.guild.id, 'elections', aliases[reg.group('pos')], msg.author.id)
        nested_set(Candidate(m, msg.author.id), msg.guild.id, 'elections', aliases[reg.group('pos')], msg.author.id)
        await msg.author.send("You are now running.")
        await save(None, None, None, overrideperms=True)
    else:
        await msg.channel.send("You must be a citizen!")

async def nominate(Demobot, msg, reg):
    if nested_get(msg.guild.id, "roles", 'leader') in msg.author.roles :
        aliases = {
        'judge':'judge',
        'j':'judge',
        'jd':'judge'
        }
        if reg.group('pos') not in aliases:
            return
        else:
            role = nested_get(msg.guild.id, "roles", aliases[reg.group('pos')])

        type = "nomination"
        propchan = nested_get(msg.guild.id, "channels", 'proposals')
        newm = await propchan.send('\u200D')
        content = "make "+reg.group("user")+" a "+role.mention+"."
        em = Embed(title=type.title()+' Proposal', description=('ID: %s\n\n%s' % (newm.id, content)), colour = nested_get(msg.guild.id, "roles", "representative").colour)
        newm = await newm.edit(nested_get(msg.guild.id, "roles", "representative").mention, embed=em)

        propobj = Nomination(newm, type, content, msg.author, msg.mentions[0], role)
        nested_set(propobj, msg.guild.id, 'messages', 'proposals', newm.id)
        await newm.add_reaction("👍")
        await newm.add_reaction("👎")
        await newm.add_reaction("🤷")
        await save(None, None, None, overrideperms=True)
    else:
        await msg.channel.send("You are not leader!")

add_message_handler(running, r'I\s*(?:(?:want|would\s*like)\s*to\s*run|am\s*running)\s*for\s*(?P<pos>.*?)\Z')
add_message_handler(nominate, r'(?:I )?(?:want to )?nominate (?P<user><@!?(?P<userid>[0-9]+)>) for (?P<pos>.*)\Z')
