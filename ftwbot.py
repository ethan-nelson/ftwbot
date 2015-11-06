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

__version__ = '0.2'

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


def fetch_latest_tweet(the_client, the_message):
    api = twitter.Api(consumer_key=os.environ['twitter_consumer_key'],
                      consumer_secret=os.environ['twitter_consumer_secret'],
                      access_token_key=os.environ['twitter_access_token_key'],
                      access_token_secret=os.environ['twitter_access_token_secret'])
    tweet = api.GetUserTimeline(screen_name='ftwaegwynn',count=1)[0]
    the_client.send_message(the_message.channel,
"""The most recent FTWAegwynn tweet is: %s

Read it at http://twitter.com/ftwaegwynn/status/%s.""" % (tweet.text, tweet.id))


client = discord.Client()
client.login(os.environ['discord_user'],os.environ['discord_password'])


def fetch_latest_logs(the_client, the_message):
    page = requests.get('http://www.warcraftlogs.com/guilds/recent_reports/79198/')
    tree = html.fromstring(page.text)
    wol = tree.xpath('/html/body/div/table/tbody/tr[1]/td[1]/a')[0]

    the_client.send_message(log_channel_id,
"""Here are the WCL for tonight's %s
%s""" % (wol.text, wol.attrib['href']))

    the_client.send_message(the_message.author, 'Logs are posted in #logs-raid.')


def execute_poker(the_client, the_message):
    global participants, in_progress
    rolls = poker.poker(participants)

    announcement = ''

    for player in rolls:
        announcement += player + ':     ' + str.join('     ',rolls[player]) + '\n'#sorted(rolls[player], key=lambda x: card_sort[x[0]])) + '\n'

#    the_client.send_message(the_message.channel, 'Join us in #poker to see the results.')
    the_client.send_message(the_message.channel, announcement)

    in_progress = 0
    participants = []

    return rolls


@client.event
def on_message(message):
    if message.content.startswith('!joke'):
        global last_joke_time
        if last_joke_time - datetime.datetime.now() > datetime.timedelta(minutes=1):
            client.send_message(message.channel, 'What side of a turkey has the most feathers?')
            time.sleep(0.5)
            client.send_message(message.channel, 'The outside!!! LMAO')
            last_joke_time = datetime.datetime.now()

    elif message.content.startswith('!hello'):
        client.send_message(message.channel, 'Hello to you, %s.' % (message.author.mention(),))

    elif message.content.startswith('!fail'):
        client.send_message(message.channel, 'You have failed, %s.' % (message.author.mention(),))

    elif message.content.startswith('!ping'):
        client.send_message(message.channel, 'Pong back atcha, %s.' % (message.author.mention(),))

    elif message.content.startswith('!poker'):
        global in_progress, participants
        if in_progress == 0:
            client.send_message(message.channel, 'Poker started by %s. If you would like to join, type !poker within 15 seconds.' % (message.author.mention(),))
            in_progress = 1
            threading.Timer(15.0, execute_poker, args=[client, message]).start()
            participants.append(message.author.name)
        elif in_progress == 1 and message.author.name not in participants and len(participants) < 11:
            participants.append(message.author.name)

    elif message.content.startswith('!twilight'):
#        client.send_message(message.channel, 'Team Edward all the way, %s.' % (message.author.mention(),))
        client.send_message(message.channel, twilight[random.randint(0,len(twilight))])

    elif message.content.startswith('!twitter'):
        try:
            fetch_latest_tweet(client, message)
        except:
            client.send_message(message.channel, 'Sorry, I am not able to get a tweet right now.')

    elif message.content.startswith('!logs') and message.author.roles[0].name == 'Officer':
        try:
            fetch_latest_logs(client, message)
        except:
            client.send.message(message.channel, 'Sorry, I am unable to get logs right now.')

    elif message.content.startswith(my_user_id) or message.content.startswith('@forthewynnbot'):
        if 'help' in message.content:
            client.send_message(message.author, 
"""Hi there and welcome to forthewynnbot v0.2. It was constructed by Emann.
The following commands are available for use:

    !fail: tells you how awesome you are
    !hello: greets you
    !joke: tells a very funny joke
    !logs: posts the latest Warcraft Logs in #logs-raid if you are an Officer
    !ping: pings the bot
    !poker: initiates a poker game
    !twilight: something special :)
    !twitter: retrieves the latest FTWAegwynn tweet from Twitter
 
Commands you can direct at me:

    @forthewynnbot help: displays this message
    @forthewynnbot stop: turns me off for 5 minutes
""")
        elif 'stop' in message.content:
            client.send_message(message.channel, 'Shutting down for 5 minutes.')
            time.sleep(300.0)
        else:
            client.send_message(message.channel, 'Sorry, I do not understand that command.')


client.run()
