import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, nested_get, nested_append, nested_set
from commands.utilities import save
from discord import Embed

async def propose(Demobot, msg, reg):
    if nested_get(msg.server.id, "roles", "representative") in msg.author.roles and msg.channel == nested_get(msg.server.id, "channels", "proposals-discussion"):
        aliases = {
        "rule": "rule",
        "law": "rule",
        "mod": "mod",
        "moderation": "mod"
        }
        print(reg.group("type"))
        if reg.group("type"):
            if reg.group("type") not in aliases:
                return
            type = aliases[reg.group("type").lower()]
        else:
            type = "rule"
        propchan = nested_get(msg.server.id, "channels", "proposals")
        title = reg.group("title")
        if not title:
            title = "Untitled Proposal"
        else:
            title = title.title()
        newm = await Demobot.send_message(propchan, '%s %s Proposal:\n\n**%s**\nID: %s\n\n%s' % (nested_get(msg.server.id, "roles", "representative").mention, type, title, msg.id, reg.group("content")))
        await Demobot.add_reaction(newm, "👍")
        await Demobot.add_reaction(newm, "👎")
        await Demobot.add_reaction(newm, "➖")
        nested_append(newm, msg.server.id, "proposals", "messages")
        await save(None, None, None, overrideperms=True)

add_message_handler(propose, r'<@&(?P<roleid>[0-9]*)>\s*(?P<type>.*?)\s*proposal:\n*(?:\*\*(?P<title>.*?)\*\*)?\n*(?P<content>(?:.|\n)*?)\Z')
