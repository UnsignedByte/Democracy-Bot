import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, get_data, nested_get

async def kick(Demobot, msg, reg):
    if msg.author.id=='418827664304898048':
        await Demobot.kick(msg.mentions[0])

async def imprison(Demobot, user):
    roles = user.roles
    try:
        roles.remove(nested_get(msg.author.id, "roles", "citizen"))
    except ValueError:
        pass
    await Demobot.remove_roles(user, *roles)
    await Demobot.add_roles(user, nested_get(msg.author.id, "roles", "prisoner"))

async def enfimprison(Demobot, msg, req):
    if nested_get(msg.author.id, "roles", "enforcer") in msg.author.roles:
        await imprison(Demobot, msg.mentions[0])
    else:
        await Demobot.send_message(msg.channel, "You are not an enforcer!")

add_message_handler(kick, r'kick (?P<user><@!?(?P<userid>[0-9]+)>)\Z')
add_message_handler(enfimprison, r'(?:imprison|jail) (?P<user><@!?(?P<userid>[0-9]+)>)\Z')
