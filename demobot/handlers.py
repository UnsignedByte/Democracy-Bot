import os
import pickle
from shutil import copyfile
import pprint
from copy import deepcopy
from discord.utils import find

print("Begin Handler Initialization")

message_handlers = {}
private_message_handlers = {}

print("\tBegin Loading Files")

print("\tLoaded files")

persistent_variables = {}

if not os.path.exists("data/data_backup/"):
    os.makedirs("data/data_backup/")


def add_message_handler(handler, keyword):
    message_handlers[keyword] = handler


def add_private_message_handler(handler, keyword):
    private_message_handlers[keyword] = handler


def get_data():
    return [server_data]


def nested_set(value, *keys):
    dic = server_data
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


def nested_pop(*keys):
    nested_get(*keys[:-1]).pop(keys[-1], None)


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
    if not v or isinstance(v, discord.Member):
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

server_data = {}
if os.path.isfile("data/settings.txt"):
    with open("data/settings.txt", "rb") as f:
        server_data = pickle.load(f)
    copyfile("data/settings.txt", "data/data_backup/settings.txt")

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

from time import time

async def on_message(Demobot, msg):
    if not msg.author.bot:
        if hasattr(msg.author, 'status') and msg.author.status == discord.Status.offline:
            await msg.delete()
            outm = await msg.channel.send("Hey! You shouldn't be speaking while invisible.")
            await asyncio.sleep(1)
            await outm.delete()
        try:
            for a in message_handlers:
                reg = re.compile(a, re.I).match(msg.content)
                if reg:
                    if isinstance(msg.channel, discord.DMChannel):
                        await msg.channel.send("Demobot doesn't work in private channels")
                        return
                    await message_handlers[a](Demobot, msg, reg)
                    break
            #There used to be a whole lot of catches here but they were extremely annoying because they did NOT display the trace. "Invalid inputs" is a stupid error message that gives no information.
        except Exception as e:
            em = discord.Embed(title="Unknown Error",
                               description="An unknown error occurred. Trace:\n%s" % e, colour=0xd32323)
            await msg.channel.send(embed=em)
            traceback.print_tb(e.__traceback__)


async def elections_timed(Demobot):

    dev = False
    # Making the election day not wednesday for dev purposes

    while True:
        currt = datetime.now(tz=pytz.utc)
        nextelection = currt + timedelta((2 - currt.weekday()) % 7 + (0 if dev else 1))
        nextelection = nextelection.replace(hour=2, minute=0, second=0, microsecond=0)
        await asyncio.sleep((nextelection - currt).total_seconds() if not dev else 1)
        for a in server_data:
            chann = Demobot.get_channel(nested_get(a, "channels", "announcements"))
            citizen_m = nested_get(a, "roles", "citizen").mention
            tim = nextelection.astimezone(pytz.timezone('US/Pacific')).strftime('%H:%M')
            if chann:
                await chann.send(citizen_m + "! Elections have now started. They end in two days at " + tim + ".")

            next = nested_get(a, 'channels', 'elections')
            if next:
                await next.send('```\n```\n\n**Elections Start Here**\n\n' +
                                           'Leader: Candidate with the largest difference between up and down wins.\n' +
                                           'Representative: Candidates with at least a third of the generic win.\n\n' +
                                           'Click the reactions to toggle a vote. You can vote more than once.\n' +
                                           '**Remember to vote the generic!**')
                nested_set({}, a, 'elections', 'msg')
                le = nested_get(a, 'elections', 'leader')
                for b in le:
                    c = await next.send('.\n\n**Leader Candidate**\n' + nested_get(a, 'elections', 'leader', b).desc +
                              '\n\nVotes: **0 - 0**')
                    await c.add_reaction('👍')
                    await c.add_reaction('👎')
                    nested_set(nested_get(a, 'elections', 'leader', b).ii, a, 'elections', 'msg', c.id)
                er = nested_get(a, 'elections', 'representative')
                out = '.\n\n**Representative Candidates**\nYou must vote the generic vote!\n\n'
                key = 127462
                count = ('\n\nVotes: **0 | ' + '0 - ' * len(er))[:-3] + '**'
                for b in er:
                    out += chr(key) + ' ' + nested_get(a, 'elections', 'representative', b).desc + '\n'
                    nested_set(nested_get(a, 'elections', 'representative', b).ii, a, 'elections', 'msg', key)
                    key += 1
                c = await next.send(out + count)
                await c.add_reaction('🗳')
                for d in range(127462, key):
                    await c.add_reaction(chr(d))
                nested_set('rep', a, 'elections', 'msg', c.id)
        await asyncio.sleep(172800 if not dev else 1)
        for a in server_data:
            chann = nested_get(a, 'channels', 'announcements')
            citizen_m = nested_get(a, "roles", "citizen").mention

            for l in nested_get(a, 'members', 'leader'):
                await l.remove_roles(nested_get(a, 'roles', 'leader'))

            le = nested_get(a, 'elections', 'leader')
            winner = 1000
            user = None
            for b in le:
                c = nested_get(a, 'elections', 'leader', b)
                if winner == 1000 or len(c.up) - len(c.down) > winner:
                    winner = len(c.up) - len(c.down)
                    user = find(lambda m: m.id == c.ii, Demobot.get_guild(a).members)

            for l in nested_get(a, 'members', 'representative'):
                await l.remove_roles(nested_get(a, 'roles', 'representative'))

            generic = len(nested_get(a, 'elections', 'generic'))
            er = nested_get(a, 'elections', 'representative')
            users = []
            nested_pop(a, 'elections', 'representatives')
            for b in er:
                c = nested_get(a, 'elections', 'representative', b)
                nested_set(Backup(time(), len(c.up) / generic), a, 'elections', 'backup', c.ii)
                if len(c.up) / generic >= 1 / 3 and not c.ii == user.id:
                    users.append(find(lambda m: m.id == c.ii, Demobot.get_guild(a).members))

            secondary = []
            forbid = [user.id]
            for b in range(max(0, 3 - len(users))):
                thing = next_backup(a, forbid)
                secondary.append(find(lambda m: m.id == thing, Demobot.get_guild(a).members))
                forbid.append(thing)


            await user.remove_roles(nested_get(a, 'roles', 'representative'))
            await user.add_roles(nested_get(a, 'roles', 'leader'))

            out = ''
            for u in users:
                await u.add_roles(nested_get(a, 'roles', 'representative'))
                out += u.mention + ', '

            out = 'No one was elected representative.\n' \
                if out == '' else out[:-2] + " have been elected representative!\n"
            for u in secondary:
                await u.add_roles(nested_get(a, 'roles', 'representative'))
                out += u.mention + ', '

            if chann:
                await chann.send(citizen_m + "! Elections have now ended.")
                await chann.send(user.mention + " has been elected leader!")
                await chann.send(out[:-2] + " have been made reps from the backup list.")

            if not dev:
                nested_set({}, a, 'elections')
                nested_set(set([]), a, 'elections', 'generic')
        await asyncio.sleep(100000)


def next_backup(server, leader):
    out = -1
    rep = ''
    backup = nested_get(server, 'elections', 'backup')
    for a in backup:
        if a not in leader and nested_get(server, 'elections', 'backup', a).score > out:
            out = nested_get(server, 'elections', 'backup', a).score
            rep = a
    return rep


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
    roles = nested_get(after.guild.id, 'roles')
    for a in nested_get(after.guild.id, 'members'):
        nested_remove(before, after.guild.id, 'members', a)
    for a in after.roles:
        try:
            nested_append(after, after.guild.id, 'members', list(roles.keys())[list(roles.values()).index(a)])
        except ValueError:
            pass
    await utilities.save(None, None, None, overrideperms=True)


async def newuser(Demobot, user):
    roles_to_add = []
    if user.id in nested_get(user.guild.id, "members", "citizen"):
        roles_to_add.append(nested_get(user.guild.id, "roles", "citizen"))
    if user.id in nested_get(user.guild.id, "members", "prisoner"):
        roles_to_add.append(nested_get(user.guild.id, "roles", "prisoner"))
    await user.add_roles(*roles_to_add)


async def on_reaction_add(Demobot, reaction, user):
    if user.bot:
        return
    msg = reaction.message
    if msg.channel == nested_get(msg.guild.id, "channels", "proposals"):
        if nested_get(msg.guild.id, "roles", "representative") in user.roles:
            if msg.id in nested_get(msg.guild.id, 'messages', 'proposals'):
                prop = nested_get(msg.guild.id, 'messages', "proposals", msg.id)
                if reaction.emoji == '👍':
                    prop.votes.up += 1
                elif reaction.emoji == '👎':
                    prop.votes.down += 1
                elif reaction.emoji == '🤷':
                    prop.votes.none += 1
                if user.id in prop.voted:
                    prop.voted.append(user.id)
                    await msg.remove_reaction(reaction.emoji, user)
                    await user.send('You already voted! Don\'t vote twice.')
                else:
                    prop.voted.append(user.id)
                    if prop.votes.up * 2 > len(nested_get(msg.guild.id, 'members', 'representative')) - \
                            prop.votes.none and prop.votes.up > 0:
                        nested_pop(msg.guild.id, 'messages', 'proposals', msg.id)
                        await msg.clear_reactions()
                        if prop.tt == 'rule':
                            await msg.add_reaction('✅')
                            await nested_get(msg.guild.id, "channels", "rules").send_message(prop.content)
                        elif prop.tt == 'nomination':
                            await msg.add_reaction('✅')
                            await prop.usr.add_roles(prop.role)
                        elif prop.tt == 'mod':
                            await msg.add_reaction('✔')
                            nm = await nested_get(msg.guild.id, 'channels', 'enf-todo').send(
                                '%s TODO:\n\n%s\n\nWhen complete, have an enforcer react with a ✔.' %
                                (nested_get(msg.guild.id, 'roles', 'enforcer').mention, prop.content))
                            await nm.add_reaction('✔')
                            nested_set(nm, msg.guild.id, 'messages', 'proposals', nm.id)
                        else:
                            await msg.add_reaction('✔')
                    elif len(prop.voted) == len(nested_get(msg.guild.id, 'members', 'representative')):
                        if prop.votes.up <= prop.votes.down:
                            nested_pop(msg.guild.id, 'messages', 'proposals', msg.id)
                            await msg.clear_reactions()
                            await msg.add_reaction('❌')

        else:
            await msg.remove_reaction(reaction.emoji, user)
            await user.send('You have been imprisoned because you are not a representative.')
            await enforcing.imprison(Demobot, user)
    elif msg.channel == nested_get(msg.guild.id, "channels", "elections"):
        await msg.remove_reaction(reaction.emoji, user)
        if msg.id not in nested_get(msg.guild.id, 'elections', 'msg'):
            return
        ii = nested_get(msg.guild.id, 'elections', 'msg', msg.id)
        if not ii == 'rep':
            c = nested_get(msg.guild.id, 'elections', 'leader', ii)
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
            await msg.edit_message(new_content='.\n\n**Leader Candidate**\n' + c.desc + '\n\nVotes: **' +
                                                        str(len(c.up)) + ' - ' + str(len(c.down)) + '**')
        elif ii == 'rep':
            generic = nested_get(msg.guild.id, 'elections', 'generic')
            if reaction.emoji == '🗳':
                generic.add(msg.author.id)
            elif msg.author.id in generic:
                thing = nested_get(msg.guild.id, 'elections', 'msg', ord(reaction.emoji))
                c = nested_get(msg.guild.id, 'elections', 'representative', thing)
                if msg.author.id in c.up:
                    c.up.discard(msg.author.id)
                else:
                    c.up.add(msg.author.id)
            er = nested_get(msg.guild.id, 'elections', 'representative')
            out = '.\n\n**Representative Candidates**\nYou must vote the generic vote!\n\n'
            count = '\n\nVotes: **' + str(len(generic)) + ' | '
            key = 127462
            for b in er:
                out += chr(key) + ' ' + nested_get(msg.guild.id, 'elections', 'representative', b).desc + '\n'
                key += 1
                count += str(len(nested_get(msg.guild.id, 'elections', 'representative', b).up)) + ' - '
            await msg.edit_message(new_content=out + count[:-3] + '**')


async def on_reaction_delete(Demobot, reaction, user):
    if user.bot:
        return
    msg = reaction.message
    if msg.channel == nested_get(msg.guild.id, "channels", "proposals") and \
            msg.id in nested_get(msg.guild.id, 'messages', 'proposals'):
        prop = nested_get(msg.guild.id, 'messages', "proposals", msg.id)
        if user.id in prop.voted:
            prop.voted.remove(user.id)
        if reaction.emoji == '👍':
            prop.votes.up -= 1
        elif reaction.emoji == '👎':
            prop.votes.down -= 1
        elif reaction.emoji == '🤷':
            prop.votes.none -= 1
