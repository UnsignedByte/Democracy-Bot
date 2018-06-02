from demobot.utils import *
from demobot.handlers import add_message_handler, nested_get, nested_set, nested_pop
from commands.utilities import save
from discord import Embed


async def cancel(Demobot, msg, reg):
    if reg.group('num') in nested_get(msg.server.id, 'messages', 'proposals').keys():
        prop = nested_get(msg.server.id, 'messages', 'proposals', reg.group('num'))
        if not prop.author == msg.author:
            await Demobot.send_message(msg.channel, 'You didn\'t create that prop!')
            return
        await Demobot.edit_message(prop.msg, '%s %s Proposal:\nId:%s\n\n%s\n\n*(Canceled)*' % (nested_get(msg.server.id, "roles", "representative").mention, prop.tt, prop.msg.id, '~~'+'~~\n~~'.join(prop.content.splitlines())+'~~'))
        await Demobot.clear_reactions(prop.msg)
        nested_pop(msg.server.id, 'messages', 'proposals', reg.group('num'))

async def propose(Demobot, msg, reg):
    if msg.channel == nested_get(msg.server.id, "channels", "politics"):
        aliases = {
            "rule": "rule",
            "law": "rule",
            "mod": "moderation",
            "moderation": "moderation",
            "amend":"amendment",
            "amendment":"amendment",
            "override":"override",
            "rewrite":"override"
        }
        if reg.group("type"):
            if reg.group("type") not in aliases:
                return
            type = aliases[reg.group("type").lower()]
        else:
            type = "rule"
        propchan = nested_get(msg.server.id, "channels", 'proposals')
        newm = await Demobot.send_message(propchan, 'Proposal:')
        em = Embed(title=type.title()+'proposal')
        newm = await Demobot.edit_message(
            newm,
            '%s %s Proposal:\nId: %s\n\n%s' % (nested_get(msg.server.id, "roles", "representative").mention, type, newm.id, reg.group("content")))

        propobj = Proposal(newm, type, reg.group('content'), msg.author)
        nested_set(propobj, msg.server.id, 'messages', 'proposals', newm.id)
        await Demobot.add_reaction(newm, "👍")
        await Demobot.add_reaction(newm, "👎")
        await Demobot.add_reaction(newm, "🤷")
        await save(None, None, None, overrideperms=True)

add_message_handler(propose, r'(?P<type>.*?)\s*prop(?:osal)?:\s*(?P<content>(?:.|\s)*?)\Z')
add_message_handler(cancel, r'\s*cancel\s*prop\s*(?P<num>[0-9]*)\Z')
