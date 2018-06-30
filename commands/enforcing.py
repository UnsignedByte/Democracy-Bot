import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, get_data, nested_get, nested_set
from datetime import datetime, timedelta

async def imprison(Demobot, user, reason):
    await Demobot.add_roles(user, nested_get(user.server.id, "roles", "prisoner"))
    gotten = nested_get(user.server.id, "prisoners", user.id)
    if not gotten:
        gotten = 12
    gotten = min(gotten*5, 86400)
    nested_set(gotten, user.server.id, "prisoners", user.id)
    duration = timedelta(seconds=gotten)
    await Demobot.send_message(user, "You have been imprisoned"+reason+"\nYou should be released in "+str(duration)+'.')
    await asyncio.sleep(gotten)
    await unimprison(Demobot, user)

async def enfimprison(Demobot, msg, reg):
    if nested_get(msg.server.id, "roles", "enforcer") in msg.author.roles:
        reasons = reg.group('reasons')
        if not reasons:
            reasons = " for no reason"
        await Demobot.send_message(msg.channel, msg.mentions[0].mention+' has been imprisoned'+reasons)
        await imprison(Demobot, msg.mentions[0], reasons)
    else:
        await Demobot.send_message(msg.channel, "You are not an enforcer!")

async def unimprison(Demobot, user):
    await Demobot.remove_roles(user, nested_get(user.server.id, "roles", "prisoner"))
    await Demobot.send_message(user, "You have been released from prison.")

async def enfunimprison(Demobot, msg, reg):
    if nested_get(msg.server.id, "roles", "enforcer") in msg.author.roles:
        await unimprison(Demobot, msg.mentions[0])
    else:
        await Demobot.send_message(msg.channel, "You are not an enforcer!")

async def impeach(Demobot, user):
    await Demobot.remove_roles(user, *[v for k, v in nested_get(user.server.id, "roles").items() if k not in ['prisoner', 'citizen']])

add_message_handler(enfimprison, r'(?:imprison|jail) (?P<user><@!?(?P<userid>[0-9]+)>)(?P<reasons>.*)?\Z')
add_message_handler(enfunimprison, r'(?:unimprison|release) (?P<user><@!?(?P<userid>[0-9]+)>)\Z')
