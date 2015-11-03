import discord
import time
import twitter
import os


my_user_id = '<@110629657417633792>'


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

@client.event
def on_message(message):
    if message.content.startswith('!joke'):
        client.send_message(message.channel, 'What side of a turkey has the most feathers?')
        time.sleep(0.5)
        client.send_message(message.channel, 'The outside!!! LMAO')
    elif message.content.startswith('!twitter'):
        try:
            fetch_latest_tweet(client, message)
        except:
            client.send_message(message.channel, 'Sorry, I am not able to get a tweet right now.')
    elif message.content.startswith('!logs'):
        try:
            fetch_latest_logs(client, message)
        except:
            client.send.message(message.channel, 'Sorry, I am unable to get logs right now.')
    elif message.content.startswith(my_user_id) or message.content.startswith('@forthewynnbot'):
        if 'help' in message.content:
            client.send_message(message.channel, 
"""Hi there and welcome to forthewynnbot. It was constructed by Emann.
The following commands are available for use:

    !twitter: retrieves the latest FTWAegwynn tweet from Twitter
    !joke: tells a very funny joke

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
