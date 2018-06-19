import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, server_data, nested_set, nested_get
from commands.utilities import save
from discord import Embed

async def role(Demobot, msg, reg):
    perms = msg.channel.permissions_for(msg.author)
    if perms.manage_guild:
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
            nested_set(msg.role_mentions[msg.raw_role_mentions.index(int(reg.group('roleid')))], msg.guild.id, "roles",
                       aliases[reg.group('name').lower()])
        else:
            nested_set(msg.guild.default_role.id, msg.guild.id, "roles", aliases[reg.group('name').lower()])
        await msg.channel.send('The ' + aliases[reg.group('name').lower()] +
                                   ' role for this server is now set to <&' +
                                   nested_get(msg.guild.id, "roles", aliases[reg.group('name').lower()]) + '>.')
        await save(None, None, None, overrideperms=True)


async def channel(Demobot, msg, reg):
    perms = msg.channel.permissions_for(msg.author)
    if perms.manage_guild:
        aliases = {
            'announcements':'announcements',
            'announcement':'announcements',
            'elections':'elections',
            'proposals':'proposals',
            'prop':'proposals',
            'amendments':'amendments',
            'amendment':'amendments',
            'amend':'amendments',
            'complaint':'complaints',
            'complaints':'complaints',
            'politics-discussion':'politics',
            'politics discussion':'politics',
            'political discussion':'politics',
            'politics':'politics',
            'rules':'rules',
            'rule':'rules',
            'law':'rules',
            'laws':'rules',
            'passed proposals':'rules',
            'enforcer todo':'enf-todo',
            'todo':'enf-todo',
            'election':'elections'
        }
        if reg.group('name') not in aliases:
            return
        nested_set(int(reg.group('channelid')), msg.guild.id, "channels", aliases[reg.group('name').lower()])
        await msg.channel.send('The '+aliases[reg.group('name').lower()]+' channel for this server is now set to <#'+str(nested_get(msg.guild.id, "channels", aliases[reg.group('name').lower()]))+'>.')
        await save(None, None, None, overrideperms=True)

add_message_handler(channel, r'make\s*(?P<channel><#(?P<channelid>[0-9]*)>)\s*(?:an?|the)\s*(?P<name>.*?)\s*channel$')
add_message_handler(role, r'make\s*(?P<role><@&(?P<roleid>[0-9]*)>|@everyone)\s*(?:an?|the)\s*(?P<name>.*?)\s*role$')
