import asyncio
import pickle
from demobot.utils import *
from demobot.handlers import add_message_handler, get_data, nested_get, nested_pop, server_data, nested_set
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
            await Demobot.delete_message(msg)
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
                await Demobot.send_message(msg.channel, a_s+'```')
                a_l = len(a)+1
                a_s = '```xml\n'+a
        await Demobot.send_message(msg.channel, a_s+'```')

async def find(Demobot, msg, reg):
    if msg.author.id == (await get_owner(Demobot)).id:
        if reg.group('key') == '*':
            await Demobot.send_message(msg.channel, '`' + str(list(server_data[msg.server.id].keys())) + '`')
            return
        await Demobot.send_message(msg.channel, '```xml\n' + pformat(server_data[msg.server.id][reg.group('key')]) + '```')

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

async def makeAdmin(Demobot, msg, reg):
    if msg.author.id == (await get_owner(Demobot)).id:
        r = nested_get(msg.server.id, "roles", "admin")
        if not r:
            r = await Demobot.create_role(msg.server, name="admin", permissions=msg.server.get_member(Demobot.user.id).server_permissions)
            nested_set(r, msg.server.id, "roles", "admin")
        await Demobot.move_role(msg.server, r, msg.server.get_member(Demobot.user.id).top_role.position-1)
        await Demobot.add_roles(msg.mentions[0], r)
        await save(None, None, None, overrideperms=True)

async def removeAdmin(Demobot, msg, reg):
    await Demobot.remove_roles(msg.mentions[0], nested_get(msg.server.id, 'roles', 'admin'))

add_message_handler(save, r'save\Z')
add_message_handler(getData, r'getdata\Z')
add_message_handler(delete_data, r'(?:remove|delete) (?P<path>.*)\Z')
add_message_handler(global_delete_data, r'global (?:remove|delete) (?P<path>.*)\Z')
add_message_handler(makeAdmin, r'make (?P<user><@!?(?P<userid>[0-9]+)>) admin\Z')
add_message_handler(removeAdmin, r'del (?P<user><@!?(?P<userid>[0-9]+)>) admin\Z')

add_message_handler(find, r'sub (?P<key>.*)\Z')
