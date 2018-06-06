from random import randint
import os
import pickle
from datetime import date
from shutil import copyfile
import pytz
import pprint
from copy import deepcopy

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


def nested_pop(*keys):
    nested_get(*keys[:-1]).pop(keys[-1], None)


#we made two different pops, oops :/
def alt_pop(key, *keys):
    nested_get(*keys).pop(key)


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
    except AttributeError:
        print(v)


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

import traceback


async def on_message(Demobot, msg):
    if not msg.author.bot:
        if hasattr(msg.author, 'status') and msg.author.status == discord.Status.offline:
            await Demobot.delete_message(msg)
            outm = await Demobot.send_message(msg.channel, "Hey! You shouldn't be speaking while invisible.")
            await asyncio.sleep(1)
            await Demobot.delete_message(outm)
        try:
            for a in message_handlers:
                reg = re.compile(a, re.I).match(msg.content)
                if reg:
                    if msg.channel.is_private:
                        await Demobot.send_message(msg.channel, "Demobot doesn't work in private channels")
                        return
                    await message_handlers[a](Demobot, msg, reg)
                    break
            #There used to be a whole lot of catches here but they were extremely annoying because they did NOT display the trace. "Invalid inputs" is a stupid error message that gives no information.
        except Exception as e:
            em = discord.Embed(title="Unknown Error",
                               description="An unknown error occurred. Trace:\n%s" % e, colour=0xd32323)
            await send_embed(Demobot, msg, em)
            traceback.print_tb(e.__traceback__)


async def elections_timed(Demobot):

    dev = True
    # Making the election day not wednesday for dev purposes
    test_diff = -4

    while True:
        currt = datetime.now(tz=pytz.utc)
        nextelection = currt + timedelta((2 - currt.weekday()) % 7 + (test_diff if dev else 0))
        nextelection = nextelection.replace(hour=19, minute=0, second=0, microsecond=0)
        for a in server_data:
            chann = nested_get(a, "channels", "announcements")
        await asyncio.sleep((nextelection-currt).total_seconds() if not dev else 1)
        for a in server_data:
            chann = nested_get(a, "channels", "announcements")
            citizen_m = nested_get(a, "roles", "citizen").mention
            time = (nextelection + timedelta(hours=18)).astimezone(pytz.timezone('US/Pacific')).strftime('%H:%M')
            if chann:
                electionmsg = await Demobot.send_message(
                    chann, citizen_m + "! Elections have now started. They end in two days at " + time + ".")

            next = nested_get(a, 'channels', 'elections')
            if next:
                nested_set({}, a, 'elections', 'msg')
                le = nested_get(a, 'elections', 'leader')
                for b in le:
                    c = await Demobot.send_message(
                        next, '.\n\n**Leader Candidate**\n' + nested_get(a, 'elections', 'leader', b).desc +
                              '\n\n👍 0   |   👎 0')
                    await Demobot.add_reaction(c, '👍')
                    await Demobot.add_reaction(c, '👎')
                    nested_set(nested_get(a, 'elections', 'leader', b).ii, a, 'elections', 'msg', c.id)
                er = nested_get(a, 'elections', 'representative')
                out = '.\n\n**Representative Candidates**\nYou must vote the generic vote!\n\n'
                key = 127462
                for b in er:
                    out += chr(key) + ' ' + nested_get(a, 'elections', 'representative', b).desc + '\n'
                    key += 1
                c = await Demobot.send_message(next, out)
                await Demobot.add_reaction(c, '🗳')
                for d in range(127462, key):
                    await Demobot.add_reaction(c, chr(d))
                nested_set('rep', a, 'elections', 'msg', c.id)
        await asyncio.sleep(86400)


async def minutely_check(Demobot):
    while True:
        for a in server_data:
            propchan = nested_get(a, "channels", "proposals")
            if propchan:
                for j in deepcopy(list(nested_get(a, 'messages', 'proposals').values())):
                    t = j.msg.edited_timestamp
                    t = t if t else j.msg.timestamp
                    if (datetime.utcnow() - t).total_seconds() > 86400:
                        nested_pop(a, 'messages', "proposals", j.msg.id)
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
            if msg.id in nested_get(msg.server.id, 'messages', 'proposals'):
                prop = nested_get(msg.server.id, 'messages', "proposals", msg.id)
                if reaction.emoji == '👍':
                    prop.votes.up += 1
                elif reaction.emoji == '👎':
                    prop.votes.down += 1
                elif reaction.emoji == '🤷':
                    prop.votes.none += 1
                if user.id in prop.voted:
                    prop.voted.append(user.id)
                    await Demobot.remove_reaction(msg, reaction.emoji, user)
                    await Demobot.send_message(user, 'You already voted! Don\'t vote twice.')
                else:
                    prop.voted.append(user.id)
                    if prop.votes.up * 2 > len(nested_get(msg.server.id, 'members', 'representative')) - \
                            prop.votes.none and prop.votes.up > 0:
                        nested_pop(msg.server.id, 'messages', 'proposals', msg.id)
                        await Demobot.clear_reactions(msg)
                        if prop.tt == 'rule':
                            await Demobot.add_reaction(msg, '✅')
                            await Demobot.send_message(nested_get(msg.server.id, "channels", "rules"), prop.content)
                        elif prop.tt == 'mod':
                            await Demobot.add_reaction(msg, '✔')
                            nm = await Demobot.send_message(
                                nested_get(msg.server.id, 'channels', 'enf-todo'),
                                '%s TODO:\n\n%s\n\nWhen complete, have an enforcer react with a ✔.' %
                                (nested_get(msg.server.id, 'roles', 'enforcer').mention, prop.content))
                            await Demobot.add_reaction(nm, '✔')
                            nested_set(nm, msg.server.id, 'messages', 'proposals', nm.id)
                        else:
                            await Demobot.add_reaction(msg, '✔')
                    elif len(prop.voted) == len(nested_get(msg.server.id, 'members', 'representative')):
                        if prop.votes.up <= prop.votes.down:
                            nested_pop(msg.server.id, 'messages', 'proposals', msg.id)
                            await Demobot.clear_reactions(msg)
                            await Demobot.add_reaction(msg, '❌')

        else:
            await Demobot.remove_reaction(msg, reaction.emoji, user)
            await Demobot.send_message(user, 'You have been imprisoned because you are not a representative.')
            await enforcing.imprison(Demobot, user)
    elif msg.channel == nested_get(msg.server.id, "channels", "elections"):
        if msg.id not in nested_get(msg.server.id, 'elections', 'msg'):
            return
        ii = nested_get(msg.server.id, 'elections', 'msg', msg.id)
        if not ii == 'rep':
            c = nested_get(msg.server.id, 'elections', 'leader', ii)
            if reaction.emoji == '👍':
                if msg.author.id in c.up:
                    c.up.discard(msg.author.id)
                else:
                    c.up.add(msg.author.id)
            elif reaction.emoji == '👎':
                if msg.author.id in c.down:
                    c.down.discard(msg.author.id)
                else:
                    c.down.add(msg.author.id)
            await Demobot.edit_message(msg, new_content='.\n\n**Leader Candidate**\n' + c.desc + '\n\n👍 ' +
                                                        str(len(c.up)) + '   |   👎 ' + str(len(c.down)))
        elif ii == 'rep':
            print(ord(reaction.emoji) - 127462)
        await Demobot.remove_reaction(msg, reaction.emoji, user)


async def on_reaction_delete(Demobot, reaction, user):
    if user.bot:
        return
    msg = reaction.message
    if msg.channel == nested_get(msg.server.id, "channels", "proposals") and \
            msg.id in nested_get(msg.server.id, 'messages', 'proposals'):
        prop = nested_get(msg.server.id, 'messages', "proposals", msg.id)
        if user.id in prop.voted:
            prop.voted.remove(user.id)
        if reaction.emoji == '👍':
            prop.votes.up -= 1
        elif reaction.emoji == '👎':
            prop.votes.down -= 1
        elif reaction.emoji == '🤷':
            prop.votes.none -= 1
