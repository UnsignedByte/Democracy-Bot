import asyncio
from demobot.utils import *
from demobot.handlers import add_message_handler, get_data, nested_get, nested_set
from datetime import datetime, timedelta

async def imprison(Demobot, user, reason):
    await user.add_roles(nested_get(user.guild.id, "roles", "prisoner"), reason="Imprisonment")
    gotten = nested_get(user.guild.id, "prisoners", user.id)
    if not gotten:
        gotten = 12
    gotten = min(gotten*5, 86400)
    nested_set(gotten, user.guild.id, "prisoners", user.id)
    duration = timedelta(seconds=gotten)
    await user.send("You have been imprisoned "+reason+"\nYou should be released in "+str(duration)+'.')
    await asyncio.sleep(gotten)
    await unimprison(Demobot, user)

async def enfimprison(Demobot, msg, reg):
    if nested_get(msg.guild.id, "roles", "enforcer") in msg.author.roles:
        reasons = reg.group('reasons')
        if not reasons:
            reasons = "for no reason"
        await msg.channel.send(msg.mentions[0].mention+' has been imprisoned '+reasons)
        await imprison(Demobot, msg.mentions[0], reasons)
    else:
        await msg.channel.send("You are not an enforcer!")

async def unimprison(Demobot, user):
    await user.remove_roles(nested_get(user.guild.id, "roles", "prisoner"), reason="Unimprisonment")
    await user.send("You have been released from prison.")

async def enfunimprison(Demobot, msg, reg):
    if nested_get(msg.guild.id, "roles", "enforcer") in msg.author.roles:
        await unimprison(Demobot, msg.mentions[0])
    else:
        await msg.channel.send("You are not an enforcer!")

async def impeach(Demobot, user):
    await user.remove_roles(*[v for k, v in nested_get(user.guild.id, "roles").items() if k not in ['prisoner', 'citizen']], reason="Impeachment")

async def enfimpeach(Demobot, msg, reg):
    if nested_get(msg.guild.id, "roles", "enforcer") in msg.author.roles:
        reasons = reg.group('reasons')
        if not reasons:
            reasons = "for no reason"
        await msg.channel.send(msg.mentions[0].mention+' has been impeached '+reasons)
        await impeach(Demobot, msg.mentions[0])
    else:
        await msg.channel.send("You are not an enforcer!")

add_message_handler(enfimpeach, r'impeach (?P<user><@!?(?P<userid>[0-9]+)>) (?P<reasons>.*)?\Z')
add_message_handler(enfimprison, r'(?:imprison|jail) (?P<user><@!?(?P<userid>[0-9]+)>) (?P<reasons>.*)?\Z')
add_message_handler(enfunimprison, r'(?:unimprison|release) (?P<user><@!?(?P<userid>[0-9]+)>)\Z')
