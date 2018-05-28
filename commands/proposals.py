import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, nested_get, nested_append, nested_set
from commands.utilities import save
from discord import Embed

async def propose(Demobot, msg, reg):
    if msg.channel == nested_get(msg.server.id, "channels", "proposals-discussion"):
        aliases = {
            "rule": "rule",
            "law": "rule",
            "mod": "mod",
            "moderation": "mod",
            "amend":"amend",
            "amendment":"amend",
            "override":"override",
            "rewrite":"override"
        }
        if reg.group("type"):
            if reg.group("type") not in aliases:
                return
            type = aliases[reg.group("type").lower()]
        else:
            type = "rule"
        propchan = nested_get(msg.server.id, "channels", "proposals")
        newm = await Demobot.send_message(
            propchan,
            '%s %s Proposal:\nID: %s\n\n%s' % (nested_get(msg.server.id, "roles", "representative").mention,
                                                         type, msg.id, reg.group("content")))
        await Demobot.add_reaction(newm, "👍")
        await Demobot.add_reaction(newm, "👎")
        await Demobot.add_reaction(newm, "🤷")
        propobj = Proposal(newm, type, reg.group('content'), msg.author)
        for i in range(10000):
            if not nested_get(msg.server.id, 'proposals', i):
                nested_set(propobj, msg.server.id, "proposals", i)
                break
        await save(None, None, None, overrideperms=True)

add_message_handler(propose, r'(?P<type>.*?)\s*prop(?:osal)?:\s*(?P<content>(?:.|\n)*?)\Z')
