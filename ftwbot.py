import discord
import time
import twitter
import os


def fetch_latest_tweet(the_client, the_message):
    api = twitter.Api(consumer_key=os.environ['twitter_consumer_key'],
                      consumer_secret=os.environ['twitter_consumer_secret'],
                      access_token_key=['twitter_access_token_key'],
                      access_token_secret=['twitter_access_token_secret'])
    tweet = api.GetUserTimeline(screen_name='ftwaegwynn',count=1)[0]
    the_client.send_message(the_message.channel,
"""The most recent FTWAegwynn tweet is: %s

Read it at http://twitter.com/ftwaegwynn/status/%s.""" % (tweet.text, tweet.id))


client = discord.Client()
client.login(os.environ['discord_user'],os.environ['discord_password'])

@client.event
def on_message(message):
    if message.content.startswith('!joke'):
        client.send_message(message.channel, 'What side of a turkey has the most feathers?')
        time.sleep(0.5)
        client.send_message(message.channel, 'The outside!!! LMAO')
    elif message.content.startswith('!twitter'):
        fetch_latest_tweet(client, message)
    elif message.content.startswith('<@110629657417633792>'):
        client.send_message(message.channel, 
"""Hi there and welcome to forthewynnbot. It was constructed by Emann.
The following commands are available for use:

    !twitter: retrieves the latest FTWAegwynn tweet from Twitter
    !joke: tells a very funny joke""")

client.run()
