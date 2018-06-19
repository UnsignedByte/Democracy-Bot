import asyncio
import pickle
from demobot.utils import *
from demobot.handlers import add_message_handler, get_data, nested_get, nested_pop, server_data
from discord import Embed, Permissions
from pprint import pformat, pprint

async def save(Demobot, msg, reg, overrideperms=False):
    if overrideperms or msg.author.id == "418827664304898048" or msg.author.id == '418921871333916683':
        if not overrideperms:
            em = Embed(title="Saving Data...", description="Saving...", colour=0xd32323)
            msg = await send_embed(Demobot, msg, em)
            await asyncio.sleep(1)
        data = get_data()
        with open("data/settings.txt", "wb") as f:
            pickle.dump(data[0], f)
        if not overrideperms:
            em.description = "Complete!"
            msg = await edit_embed(Demobot, msg, embed=em)
            await asyncio.sleep(0.5)
            await msg.delete()
        return True
    else:
        em = Embed(title="Insufficient Permissions", description=format_response(
            "{_mention} does not have sufficient permissions to perform this task.", _msg=msg), colour=0xd32323)
        await send_embed(Demobot, msg, em)
        return False

async def getData(Demobot, msg, reg):
    if msg.author.id == (await get_owner(Demobot)).id:
        dat = pformat(get_data()[0])
        a_l = 0
        a_s = '```xml'
        for a in dat.splitlines():
            if a_l+len(a)+1 <= 1991:
                a_l+=len(a)+1
                a_s+='\n'+a
            else:
                await msg.channel.send(a_s+'```')
                a_l = len(a)+1
                a_s = '```xml\n'+a
        await msg.channel.send(a_s+'```')

async def find(Demobot, msg, reg):
    if msg.author.id == (await get_owner(Demobot)).id:
        if reg.group('key') == '*':
            await msg.channel.send('`' + str(list(server_data[msg.server.id].keys())) + '`')
            return
        await msg.channel.send('```xml\n' + pformat(server_data[msg.server.id][reg.group('key')]) + '```')

async def delete_data(Demobot, msg, reg):
    if msg.author.id == (await get_owner(Demobot)).id:
        keys = [msg.server.id] + reg.group('path').split()
        if isinstance(nested_get(*keys[:-1]), dict):
            nested_pop(*keys)
        elif isinstance(nested_get(*keys[:-1]), list):
            nested_remove(keys[-1], *keys[:-1])
        await save(None, None, None, overrideperms=True)

async def global_delete_data(Demobot, msg, reg):
    if msg.author.id == (await get_owner(Demobot)).id:
        keys = reg.group('path').split()
        if isinstance(nested_get(*keys[:-1]), dict):
            nested_pop(*keys)
        elif isinstance(nested_get(*keys[:-1]), list):
            nested_remove(keys[-1], *keys[:-1])
        await save(None, None, None, overrideperms=True)

async def make_server(Demobot, msg, reg):
    if msg.author.id == (await get_owner(Demobot)).id:
        if len(Demobot.guilds) >= 10:
            await msg.channel.send("Demobot is in more than 10 servers! Try making a new bot.")
        else:
            await Demobot.create_guild(reg.group('name'))
    else:
        await msg.channel.send("You aren't the bot owner.")

add_message_handler(save, r'save\Z')
add_message_handler(getData, r'getdata\Z')
add_message_handler(delete_data, r'(?:remove|delete) (?P<path>.*)\Z')
add_message_handler(global_delete_data, r'global (?:remove|delete) (?P<path>.*)\Z')
add_message_handler(make_server, r'make a server called (?P<name>.*)\Z')

add_message_handler(find, r'sub (?P<key>.*)\Z')
