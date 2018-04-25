import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, server_data, nested_set, nested_get
from commands.utilities import save
from discord import Embed

@asyncio.coroutine
def role(Demobot, msg, reg):
    perms = msg.channel.permissions_for(msg.author)
    if perms.manage_server:
        aliases = {
        'rep':'representative',
        'representative':'representative',
        'leader':'leader',
        'president':'leader',
        'judge':'judge',
        'enforcer':'enforcer',
        'default':'citizen',
        'citizen':'citizen'
        }
        #update_user_data(msg.server.id, aliases[reg.group('name')], )
        if reg.group('role') is not '@everyone':
            nested_set(msg.role_mentions[msg.raw_role_mentions.index(reg.group('roleid'))], msg.server.id, "roles", aliases[reg.group('name').lower()])
        else:
            nested_set(msg.server.default_role, msg.server.id, "roles", aliases[reg.group('name').lower()])
        yield from Demobot.send_message(msg.channel, 'The '+aliases[reg.group('name').lower()]+' role for this server is now set to '+nested_get(msg.server.id, "roles", aliases[reg.group('name').lower()]).mention+'.')
        yield from save(None, None, None, overrideperms=True)

add_message_handler(role, r'make\s*(?P<role><@&(?P<roleid>[0-9]*)>|@everyone)\s*(?:an?|the)\s*(?P<name>leader|president|judge|enforcer|rep(?:resentative)?|citizen|default)\s*role')
