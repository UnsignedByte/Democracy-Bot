import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, server_data, nested_set, nested_get
from commands.utilities import save
from discord import Embed


async def role(Demobot, msg, reg):
    perms = msg.channel.permissions_for(msg.author)
    if perms.manage_server:
        aliases = {
        'rep':'representative',
        'representative':'representative',
        'leader':'leader',
        'president':'leader',
        'pres':'leader',
        'judge':'judge',
        'enforcer':'enforcer',
        'enf':'enforcer',
        'prisoner':'prisoner',
        'criminal':'prisoner',
        'default':'citizen',
        'citizen':'citizen'
        }
        if reg.group('name') not in aliases:
            return
        if reg.group('role') is not '@everyone':
            nested_set(msg.role_mentions[msg.raw_role_mentions.index(reg.group('roleid'))], msg.server.id, "roles",
                       aliases[reg.group('name').lower()])
        else:
            nested_set(msg.server.default_role, msg.server.id, "roles", aliases[reg.group('name').lower()])
        await Demobot.send_message(msg.channel, 'The ' + aliases[reg.group('name').lower()] +
                                   ' role for this server is now set to ' +
                                   nested_get(msg.server.id, "roles", aliases[reg.group('name').lower()]).mention + '.')
        await save(None, None, None, overrideperms=True)


async def channel(Demobot, msg, reg):
    perms = msg.channel.permissions_for(msg.author)
    if perms.manage_server:
        aliases = {
        'announcements':'announcements',
        'announcement':'announcements',
        'elections':'elections',
        'proposals':'proposals',
        'amendments':'amendments',
        'amend':'amendments',
        'proposals-discussion':'proposals-discussion',
        'proposal discussion':'proposals-discussion',
        'rules':'rules',
        'passed proposals':'rules',
        'election':'elections'
        }
        if reg.group('name') not in aliases:
            return
        nested_set(Demobot.get_channel(reg.group('channelid')), msg.server.id, "channels", aliases[reg.group('name').lower()])
        await Demobot.send_message(msg.channel, 'The '+aliases[reg.group('name').lower()]+' channel for this server is now set to '+nested_get(msg.server.id, "channels", aliases[reg.group('name').lower()]).mention+'.')
        await save(None, None, None, overrideperms=True)

add_message_handler(channel, r'make\s*(?P<channel><#(?P<channelid>[0-9]*)>)\s*(?:an?|the)\s*(?P<name>.*?)\s*channel$')
add_message_handler(role, r'make\s*(?P<role><@&(?P<roleid>[0-9]*)>|@everyone)\s*(?:an?|the)\s*(?P<name>.*?)\s*role$')
