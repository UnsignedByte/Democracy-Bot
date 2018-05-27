from random import randint
import os
import pickle
from datetime import date
from shutil import copyfile
import pytz

print("Begin Handler Initialization")

message_handlers = {}
private_message_handlers = {}

print("\tBegin Loading Files")

print("\tLoaded files")

persistent_variables = {}

if not os.path.exists("data/data_backup/"):
    os.makedirs("data/data_backup/")

server_data = {}
if os.path.isfile("data/settings.txt"):
    with open("data/settings.txt", "rb") as f:
        server_data = pickle.load(f)
    copyfile("data/settings.txt", "data/data_backup/settings.txt")


def add_message_handler(handler, keyword):
    message_handlers[keyword] = handler


def add_private_message_handler(handler, keyword):
    private_message_handlers[keyword] = handler


def get_data():
    return [server_data]
# from https://stackoverflow.com/questions/13687924/setting-a-value-in-a-nested-python-dictionary-given-a-list-of-indices-and-value


def nested_set(value, *keys):
    dic = server_data
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value

def nested_get(*keys):
    dic = server_data
    for key in keys:
        dic=dic.setdefault( key, {} )
    return dic

def nested_append(value, *keys):
    v = nested_get(*keys)
    if v:
        v.append(value)
    else:
        nested_set([value], *keys)

def nested_remove(value, *keys, **kwargs):
    kwargs['func'] = kwargs.get('func', None)
    v = nested_get(*keys)
    if not v:
        return
    try:
        if not kwargs['func']:
            v.remove(value)
        else:
            for x in v:
                if kwargs['func'](x, value):
                    v.remove(x)
                    break
    except ValueError:
        return


print("Handler initialized")
print("Begin Command Initialization")
# Add modules here
from commands import *
from demobot.utils import *
import discord
print("Command Initialization Finished")

import asyncio
import re
from datetime import datetime, timedelta


async def on_message(Demobot, msg):
    if not msg.author.bot:
        if msg.author.status == discord.Status.offline:
            await Demobot.delete_message(msg)
            outm = await Demobot.send_message(msg.channel, "Hey! You shouldn't be speaking while invisible.")
            await asyncio.sleep(1)
            await Demobot.delete_message(outm)
        try:
            if msg.channel.is_private:
                await Demobot.send_message(msg.channel, "Demobot doesn't work in private channels")
            for a in message_handlers:
                reg = re.compile(a, re.I).match(msg.content)
                if reg:
                    await message_handlers[a](Demobot, msg, reg)
                    break
        except IndexError:
            em = discord.Embed(title="Missing Inputs", description="Not enough inputs provided.", colour=0xd32323)
            await send_embed(Demobot, msg, em)
        except (TypeError, ValueError):
            em = discord.Embed(title="Invalid Inputs", description="Invalid inputs provided.", colour=0xd32323)
            await send_embed(Demobot, msg, em)
        except discord.Forbidden:
            em = discord.Embed(title="Missing Permissions", description="Demobot is missing permissions to perform this task.", colour=0xd32323)
            await send_embed(Demobot, msg, em)
        except Exception as e:
            em = discord.Embed(title="Unknown Error", description="An unknown error occurred. Trace:\n%s" % e, colour=0xd32323)
            await send_embed(Demobot, msg, em)


async def elections_timed(Demobot):
    while True:
        currt = datetime.now(tz=pytz.utc)
        nextelection = currt + timedelta( (2-currt.weekday()) % 7 + 1 )
        nextelection = nextelection.replace(hour=8, minute=0, second=0, microsecond=0)
        await asyncio.sleep((nextelection-currt).total_seconds())
        for a in server_data:
            chann = nested_get(a, "channels", "announcements")
            if chann:
                await Demobot.send_message(chann, "Hey "+nested_get(a, "roles", "citizen").mention+"! You will be able to run for positions in government later today at "+(nextelection+timedelta(hours=12)).astimezone(pytz.timezone('US/Pacific')).strftime('%H:%M:%S')+" PST.")
        await asyncio.sleep(43200)
        for a in server_data:
            chann = nested_get(a, "channels", "announcements")
            if chann:
                electionmsg = await Demobot.send_message(chann, "Hey "+nested_get(a, "roles", "citizen").mention+"! You may now run for positions in government!\nTo do so, type `I am running for (position)` (remove the parentheses).\nElections will start later today at "+(nextelection+timedelta(hours=18)).astimezone(pytz.timezone('US/Pacific')).strftime('%H:%M:%S')+" PST.")
            nested_set(electionmsg, a, "elections", "runnable")
        await asyncio.sleep(21600)
        nested_set(None, a, "elections", "runnable")
        for a in server_data:
            chann = nested_get(a, "channels", "announcements")
            if chann:
                electionmsg = await Demobot.send_message(chann, "Hey "+nested_get(a, "roles", "citizen").mention+"! Elections have now started. They will last until tomorrow at "+(nextelection+timedelta(hours=18)).astimezone(pytz.timezone('US/Pacific')).strftime('%H:%M:%S')+" PST.")
            nested_set(electionmsg, a, "elections", "election")
        await asyncio.sleep(86400)

async def minutely_check(Demobot):
    while True:
        await utilities.save(None, None, None, overrideperms=True)
        await asyncio.sleep(60)

async def member_update(Demobot, before, after):
    roles = nested_get(after.server.id, 'roles')
    for a in nested_get(after.server.id, 'members'):
        nested_remove(before, after.server.id, 'members', a)
    for a in after.roles:
        try:
            nested_append(after, after.server.id, 'members', list(roles.keys())[list(roles.values()).index(a)])
        except ValueError:
            pass
    await utilities.save(None, None, None, overrideperms=True)

async def newuser(Demobot, user):
    roles_to_add = []
    if user in nested_get(user.server.id, "members", "citizen"):
        roles_to_add.append(nested_get(user.server.id, "roles", "citizen"))
    if user in nested_get(user.server.id, "members", "prisoner"):
        roles_to_add.append(nested_get(user.server.id, "roles", "prisoner"))
    await Demobot.add_roles(user, *roles_to_add)

async def on_reaction_add(Demobot, reaction, user):
    if user.bot:
        return
    msg = reaction.message
    if msg.channel == nested_get(msg.server.id, "channels", "proposals"):
        if nested_get(msg.server.id, "roles", "representative") in user.roles:
            ids = [x.msg.id for x in nested_get(msg.server.id, "proposals", "messages")]
            if msg.id in ids:
                prop = nested_get(msg.server.id, "proposals", "messages")[ids.index(msg.id)]
                if reaction.emoji == '👍':
                    prop.votes.up += 1
                elif reaction.emoji == '👎':
                    prop.votes.down += 1
                elif reaction.emoji == '🤷':
                    prop.votes.none += 1
                if user.id in prop.voted:
                    await Demobot.remove_reaction(msg, reaction.emoji, user)
                    await Demobot.send_message(msg.channel, 'dev message: don\'t vote twice, idiot')
                else:
                    prop.voted.append(user.id)
                    if prop.votes.up * 2 > len(nested_get(msg.server.id, 'members', 'representative')) - prop.votes.none:
                        await Demobot.add_reaction(msg, '✅')
                        await Demobot.send_message(nested_get(msg.server.id, "channels", "rules"), prop.content)

        else:
            await Demobot.remove_reaction(msg, reaction.emoji, user)
            await Demobot.send_message(msg.channel, 'dev message: you ain\'t a rep')
            # the below line throws a huge error, pls fix
            await enforcing.imprison(Demobot, msg.author)
    elif msg.channel == nested_get(msg.server.id, "channels", "elections"):
        pass


async def on_reaction_delete(Demobot, reaction, user):
    if user.bot:
        return
    msg = reaction.message
    if msg.channel == nested_get(msg.server.id, "channels", "proposals"):
        ids = [x.msg.id for x in nested_get(msg.server.id, "proposals", "messages")]
        if msg.id in ids:
            prop = nested_get(msg.server.id, "proposals", "messages")[ids.index(msg.id)]
            if user.id in prop.voted:
                prop.voted.remove(user.id)
            if reaction.emoji == '👍':
                prop.votes.up -= 1
            elif reaction.emoji == '👎':
                prop.votes.down -= 1
            elif reaction.emoji == '🤷':
                prop.votes.none -= 1
