import os

import discord
from dotenv import load_dotenv

from discord.ext import commands
from pymongo import MongoClient
from bson.json_util import dumps

import random
import json
import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='%')

db_client = MongoClient('localhost', 27017)
db = db_client.bot

word_en = json.load(open('word_en.json', 'r'))
word_ru = json.load(open('word_ru.json', 'r'))

global_state = {}

@bot.event
async def on_ready():
    print('ready')

@bot.event
async def on_message(msg):
    print(msg.content)
    print(global_state)
    if str(msg.channel.type) != 'private' and msg.author.name != 'kpokoguJI':
        if msg.content.startswith('%'):
            await bot.process_commands(msg)
            return
        if not msg.guild.name in global_state:
            return
        if global_state[msg.guild.name]['state'] == 0:
            return
        if msg.content.lower() == global_state[msg.guild.name]['current_word'].lower() and msg.author.name != global_state[msg.guild.name]['picks']:
            global_state[msg.guild.name]['state'] = 0
            global_state[msg.guild.name]['picks'] = ''
            global_state[msg.guild.name]['timestamp'] = datetime.datetime.now().timestamp()
            global_state[msg.guild.name]['current_word'] = ''
            if msg.author.name in global_state[msg.guild.name]['points']:
                global_state[msg.guild.name]['points'][msg.author.name] += 1
            else:
                global_state[msg.guild.name]['points'][msg.author.name] = 1
            await msg.channel.send('correct, pick host')

@bot.command(name='rating')
async def rating(ctx):  
    if not ctx.message.guild.name in global_state:
        await ctx.send('no info')
        return
    print(dumps(global_state[ctx.message.guild.name]['points']))
    await ctx.send(dumps(global_state[ctx.message.guild.name]['points']))
    

@bot.command(name='next')
async def next(ctx):
    if not ctx.message.guild.name in global_state:
        await ctx.send('not started')
        return
    state = global_state[ctx.message.guild.name]
    if state['state'] == 0:
        await ctx.send('no host yet')
        return
    if ctx.message.author.name != state['picks']:
        await ctx.send('you are not host')
        return
    word = ''
    if state['language'] == 'ru':
        word = random.choice(word_ru)
    else:
        word = random.choice(word_en)
    state['current_word'] = word
    state['timestamp'] = datetime.datetime.now().timestamp()
    await ctx.message.author.create_dm()
    await ctx.message.author.dm_channel.send(f'current word is {word}')
    print(f'{ctx.message.guild.name} {state}')

@bot.command(name='start_en')
async def start_en(ctx): 
    if not ctx.message.guild.name in global_state:
        global_state[ctx.message.guild.name] = {
                'state': 1,
                'picks': '',
                'timestamp': None,
                'current_word': '',
                'language': '',
                'points': {}
                }
    if global_state[ctx.message.guild.name]['timestamp'] != None and datetime.datetime.now().timestamp() - global_state[ctx.message.guild.name]['timestamp'] < 300:
        await ctx.send('wait 5 mins')
        return 
    state = global_state[ctx.message.guild.name]
    state['picks'] = ctx.message.author.name
    state['timestamp'] = datetime.datetime.now().timestamp()
    state['language'] = 'en'
    state['current_word'] = random.choice(word_en)
    await ctx.message.author.create_dm()
    await ctx.message.author.dm_channel.send(f'current word is {state["current_word"]}')
    await ctx.send(f'game is started, host is {state["picks"]}')
    print(f'{ctx.message.guild.name} {state}')

@bot.command(name='start_ru')
async def start_ru(ctx):
    if not ctx.message.guild.name in global_state:
        global_state[ctx.message.guild.name] = {
                'state': 1,
                'picks': '',
                'timestamp': None,
                'current_word': '',
                'language': '',
                'points': {}
                }
    if global_state[ctx.message.guild.name]['timestamp'] != None and datetime.datetime.now().timestamp() - global_state[ctx.message.guild.name]['timestamp'] < 300:
        await ctx.send('wait 5 mins')
        return 
    state = global_state[ctx.message.guild.name]
    state['picks'] = ctx.message.author.name
    state['timestamp'] = datetime.datetime.now().timestamp()
    state['language'] = 'ru'
    state['current_word'] = random.choice(word_ru)
    await ctx.message.author.create_dm()
    await ctx.message.author.dm_channel.send(f'current word is {state["current_word"]}')
    await ctx.send(f'game is started, host is {state["picks"]}')
    print(f'{ctx.message.guild.name} {state}')

@bot.command(name='host')
async def host(ctx):
    if not ctx.message.guild.name in global_state:
        await ctx.send('not started')
        return
    state = global_state[ctx.message.guild.name]
    if state['state'] == 1 and datetime.datetime.now().timestamp() - state['timestamp'] < 300:
        await ctx.send('wait 5 mins')
        return 
    state['picks'] = ctx.message.author.name
    state['timestamp'] = datetime.datetime.now().timestamp()
    word = ''
    if state['language'] == 'ru':
        word = random.choice(word_ru)
    else:
        word = random.choice(word_en)
    state['current_word'] = word
    state['state'] = 1
    await ctx.message.author.create_dm()
    await ctx.message.author.dm_channel.send(f'current word is {state["current_word"]}')
    await ctx.send(f'host is {state["picks"]}')
    print(f'{ctx.message.guild.name} {state}')

bot.run(TOKEN)
