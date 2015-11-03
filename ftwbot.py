import discord
import time
import twitter
import os
from lxml import html
import requests
import datetime

date_format = '%Y-%m-%d %H:%M:%S'

my_user_id = '<@110629657417633792>'
log_channel_id = '91029061601615872'
os.environ['last_joke_time'] = datetime.datetime.now().strftime(date_format)


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


@client.event
def on_message(message):
    if message.content.startswith('!joke'):
        if datetime.datetime.strptime(os.environ['last_joke_time'],date_format) - datetime.datetime.now() > datetime.timedelta(minutes=1):
            client.send_message(message.channel, 'What side of a turkey has the most feathers?')
            time.sleep(0.5)
            client.send_message(message.channel, 'The outside!!! LMAO')
            os.environ['last_joke_time'] = datetime.datetime.now()

    elif message.content.startswith('!hello'):
        client.send_message(message.channel, 'Hello to you, {}.'.format(message.author.mention()))

    elif message.content.startswith('!fail'):
        client.send_message(message.channel, 'You are fail, {}.'.format(message.author.mention()))

    elif message.content.startswith('!poker'):
        client.send_message(message.channel, 'Poker is coming soon.')

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
            client.send_message(message.channel, 
"""Hi there and welcome to forthewynnbot. It was constructed by Emann.
The following commands are available for use:

    !fail: tells you how awesome you are
    !hello: greets you
    !joke: tells a very funny joke
    !logs: posts the latest Warcraft Logs in #logs-raid if you are an Officer
    !poker: initiates a poker game (not implemented yet)
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
