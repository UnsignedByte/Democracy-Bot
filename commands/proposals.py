from demobot.utils import *
from demobot.handlers import add_message_handler, nested_get, nested_set, nested_pop
from commands.utilities import save


async def cancel(Demobot, msg, reg):
    if isInteger(reg.group('num')) and int(reg.group('num')) in nested_get(msg.server.id, 'proposals').keys():
        prop = nested_get(msg.server.id, 'proposals', int(reg.group('num')))
        if not prop.author == msg.author:
            await Demobot.send_message(msg.channel, 'You didn\'t create that prop!')
            return
        await Demobot.delete_message(prop.msg)
        nested_pop(int(reg.group('num')), msg.server.id, 'proposals')


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
add_message_handler(cancel, r'\s*cancel\s*(?P<num>.*?)\Z')
