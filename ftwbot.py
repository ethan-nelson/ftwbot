import discord
import time
import twitter
import os
from lxml import html
import requests
import datetime
import poker
import copy
import threading
import random
import json
import tabulate
import asyncio

__version__ = '0.3'

card_sort = {'A':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13}

participants = []
in_progress = 0

my_user_id = '<@110629657417633792>'
log_channel_id = '91029061601615872'
poker_channel_id = '111655731958161408'

last_joke_time = datetime.datetime.now()

twilight = []
the_file = open('twilight.txt','r')
for line in the_file:
    twilight.append(line.rstrip('\n'))

drake = []
try:
    the_file = open('drake.txt','r')
    for line in the_file:
        drake.append(line.rstrip('\n'))
except:
    print('No lyrics file, drake.txt, detected.')
    drake = ['Sorry, no lyrics file found.']


async def fetch_latest_tweet(the_client, the_message):
    api = twitter.Api(consumer_key=os.environ['twitter_consumer_key'],
                      consumer_secret=os.environ['twitter_consumer_secret'],
                      access_token_key=os.environ['twitter_access_token_key'],
                      access_token_secret=os.environ['twitter_access_token_secret'])
    tweet = api.GetUserTimeline(screen_name='ftwaegwynn',count=1)[0]
    await the_client.send_message(the_message.channel,\
"""The most recent FTWAegwynn tweet is: %s

Read it at http://twitter.com/ftwaegwynn/status/%s.""" % (tweet.text, tweet.id))


client = discord.Client()


async def fetch_latest_logs(the_client, the_message):
    page = requests.get('http://www.warcraftlogs.com/guilds/recent_reports/79198/')
    tree = html.fromstring(page.text)
    wol = tree.xpath('/html/body/div/table/tbody/tr[1]/td[1]/a')[0]

    await the_client.send_message(log_channel_id,
"""Here are the WCL for tonight's %s
%s""" % (wol.text, wol.attrib['href']))

    await the_client.send_message(the_message.author, 'Logs are posted in #logs-raid.')


async def execute_poker(the_client, the_message):
    global participants, in_progress
    rolls = poker.poker(participants)

    announcement = ''

    for player in rolls:
        announcement += player + ':     ' + str.join('     ',rolls[player]) + '\n'#sorted(rolls[player], key=lambda x: card_sort[x[0]])) + '\n'

#    the_client.send_message(the_message.channel, 'Join us in #poker to see the results.')
    await the_client.send_message(the_message.channel, announcement)

    in_progress = 0
    participants = []

    return rolls


async def fetch_realm_status(the_client, the_message, realm):
    page = requests.get('https://us.api.battle.net/wow/realm/status?locale=en_US&realms=%s&apikey=%s' % (realm,os.environ['battlenet_key']))
    data = json.loads(page.text)
    status = data['realms'][0]['status']

    if status is True:
        status_msg = '%s is up!' % realm
        await the_client.send_message(the_message.channel, status_msg)
    else:
        status_msg = '%s is not up. :crying_cat_face:' % realm
        await the_client.send_message(the_message.channel, status_msg)

    return


async def fetch_raider_information(the_client, the_message, character, realm):
    the_client.delete_message(the_message)
    status_msg = 'Retrieving information on %s-%s. Please give me 5 seconds.' % (character,realm)
    await the_client.send_message(the_message.author, status_msg)
    page = requests.get('https://us.api.battle.net/wow/character/%s/%s?fields=items&locale=en_US&apikey=%s' % (realm,character,os.environ['battlenet_key']))
    data = json.loads(page.text)
    ilevel = data['items']['averageItemLevel']
    ileveleq = data['items']['averageItemLevelEquipped']

    page = requests.get('https://us.api.battle.net/wow/character/%s/%s?fields=progression&locale=en_US&apikey=%s' % (realm,character,os.environ['battlenet_key']))
    data = json.loads(page.text)
    clears = {}
    boss_clears = []
    for raid in data['progression']['raids']:
        if raid['name'] == "Hellfire Citadel":
            clears['normal'] = raid['normal']
            clears['heroic'] = raid['heroic']
            clears['mythic'] = raid['mythic']
            for boss in raid['bosses']:
                boss_clears.append([boss['name'],boss['normalKills'],boss['heroicKills'],boss['mythicKills']])

    message = """Raid information for %s-%s.
---------------------------
Average item level: %s
Average equipped item level: %s

Raiding progression in Hellfire Citadel.
%s""" % (character, realm, ilevel, ileveleq, tabulate.tabulate(boss_clears, headers=['Boss','Normal Kills','Heroic Kills','Mythic Kills']))

    await the_client.send_message(the_message.author, message)

    return

@client.event
async def on_message(message):
    time.sleep(0.1)
    if message.content.startswith('!joke'):
        global last_joke_time
        if datetime.datetime.now() - last_joke_time > datetime.timedelta(minutes=1):
            #await client.send_message(message.channel, 'What side of a turkey has the most feathers?')
            await client.send_message(message.channel, 'Why did the Grinch go to the liquor store?')
            time.sleep(0.5)
            #await client.send_message(message.channel, 'The outside!!! LMAO')
            await client.send_message(message.channel, 'To get his holiday spirit!')
            last_joke_time = datetime.datetime.now()

    elif message.content.startswith('!realm'):
        fetch_realm_status(client, message, message.content[7:])

    elif message.content.startswith('!player'):
        player_string = message.content[8:]
        player, realm = player_string.split('-')
        fetch_raider_information(client, message, player, realm)

    elif message.content.startswith('!hello'):
         await client.send_message(message.channel, """Hello, %s, it's me.
I was wondering if after all these years you'd like to meet, to go over everything.
They say that time's supposed to heal ya, but I ain't done much healing.
Hello, can you hear me?""" % (message.author.mention,))

    elif message.content.startswith('!fail'):
        await client.send_message(message.channel, 'You have failed, %s.' % (message.author.mention,))

    elif message.content.startswith('!ping'):
        await client.send_message(message.channel, 'Pong back atcha, %s.' % (message.author.mention,))

    elif message.content.startswith('!poker'):
        global in_progress, participants
        if in_progress == 0:
            await client.send_message(message.channel, 'Poker started by %s. If you would like to join, type !poker within 15 seconds.' % (message.author.mention,))
            in_progress = 1
            threading.Timer(15.0, execute_poker, args=[client, message]).start()
            participants.append(message.author.name)
        elif in_progress == 1 and message.author.name not in participants and len(participants) < 11:
            participants.append(message.author.name)

    elif message.content.startswith('!drake'):
        await client.send_message(message.channel, drake[random.randint(0,len(drake)-1)])

    elif message.content.startswith('!twilight'):
        await client.send_message(message.channel, twilight[random.randint(0,len(twilight)-1)])

    elif message.content.startswith('!teamjacob'):
        await client.send_message(message.channel, 'Team Edward all the way, %s.' % (message.author.mention,))

    elif message.content.startswith('!yell'):
        await client.send_message(message.channel, 'Please keep your voice down, %s.' % (message.author.mention,))

    elif message.content.startswith('!twitter'):
        try:
            fetch_latest_tweet(client, message)
        except:
            await client.send_message(message.channel, 'Sorry, I am not able to get a tweet right now.')

    elif message.content.startswith('!logs') and message.author.roles[0].name == 'Officer':
        client.delete_message(message)
        try:
            fetch_latest_logs(client, message)
        except:
            client.send.message(message.channel, 'Sorry, I am unable to get logs right now.')

    elif message.content.startswith(my_user_id) or message.content.startswith('@forthewynnbot'):
        client.delete_message(message)
        if 'help' in message.content:
            await client.send_message(message.author, 
"""Hi there and welcome to forthewynnbot v0.2. It was constructed by Emann.
The following commands are available for use:

    !drake: something special :)
    !fail: tells you how awesome you are
    !hello: greets you
    !joke: tells a very funny joke
    !logs: posts the latest Warcraft Logs in #logs-raid if you are an Officer
    !ping: pings the bot
    !poker: initiates a poker game
    !twilight: something else special :)
    !twitter: retrieves the latest FTWAegwynn tweet from Twitter
 
Commands you can direct at me:

    @forthewynnbot help: displays this message
    @forthewynnbot stop: turns me off for 5 minutes

For more information, visit http://github.com/ethan-nelson/ftwbot
""")
        elif 'stop' in message.content:
            await client.send_message(message.channel, 'Shutting down for 5 minutes.')
            time.sleep(300.0)
        else:
            await client.send_message(message.channel, 'Sorry, I do not understand that command.')

client.run(os.environ['discord_user'],os.environ['discord_password'])
