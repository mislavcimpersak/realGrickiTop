from datetime import datetime
import json
import os
import random
import re
from time import sleep

import emoji
from iopipe.iopipe import IOpipe
import tweepy


iopipe = IOpipe(os.environ.get('IOPIPE_KEY'))


DEBUG = True if os.environ.get('DEBUG') == 'True' else False
EMOJI_OF_THE_DAY_TEXT = 'Emoji dana:'


class Poster(object):
    def __init__(self):
        """
        Initialize instance and set instance variables.
        """
        self.set_twitter_api()
        self.set_last_n_tweets(os.environ.get('NUMBER_OF_LAST_TWEETS', 10))

    def set_twitter_api(self):
        """
        Log in user and make `twitter.api` instance avaiable within instance.
        """
        auth = tweepy.OAuthHandler(
            os.environ.get('TWITTER_CONSUMER_KEY'),
            os.environ.get('TWITTER_CONSUMER_SECRET')
        )
        auth.set_access_token(
            os.environ.get('TWITTER_ACCESS_TOKEN'),
            os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
        )

        self.api = tweepy.API(auth)

    def set_last_n_tweets(self, number_of_tweets):
        """
        Populates `last_n_tweets` instance variable with a list of tweets as
        strings.

        :param number_of_tweets: how many tweets will be fetched
        :type number_of_tweets: int
        """
        tweets = self.api.user_timeline(count=number_of_tweets)

        self.last_n_tweets = [
            re.sub(r'{}.?'.format(EMOJI_OF_THE_DAY_TEXT), '', tweet.text).strip()
            for tweet in tweets
        ]

    def get_wait_time(self, tweet):
        """
        Tweets are sent around noon, not exactly at noon just to keep the joke
        light.
        Some tweets work if they are sent only before noon, some if they are
        sent only after noon. For most of them it doesn't matter.
        Code takes into account AWS lambdas variable cold start.

        :param tweet: dict with tweet data
        :type tweet: dict

        :returns: number of seconds to wait before posting tweet
        :rtype: int
        """
        # used for well... debugging stuff
        if DEBUG:
            return 0

        time_span = tweet['time_span']

        now = datetime.now()
        today = datetime.today()
        noon = datetime(today.year, today.month, today.day, 12)
        seconds_left_till_noon = (noon - now).seconds

        # whole function shouldn't execute longer then 4 minutes, so it can
        # continue to execute only 2 minutes after noon
        if seconds_left_till_noon > 120:
            return 0
        elif time_span is 'before':
            return random.randint(0, seconds_left_till_noon)
        elif time_span is 'after':
            return random.randint(
                seconds_left_till_noon, seconds_left_till_noon + 120)
        elif time_span is 'exact':
            return seconds_left_till_noon
        else:
            return random.randint(0, 2)

    def get_random_tweet(self):
        """
        Get a random tweet from provided .json file.
        If the tweet was already posted within the last n tweets, find a new
        one.

        :returns: single random tweet from `data/tweets.json`
        :rtype: dict
        """
        tweets = json.loads(open('data/tweets.json', 'r').read())
        tweet = random.choice(tweets)

        if tweet['text'].strip() in self.last_n_tweets:
            return self.get_random_tweet()
        else:
            return tweet

    def get_emoji_of_the_day_text(self):
        """
        Return emoji of the day™.
        This is just a dirty trick so that twitter doesn't return status 187
        (Status is a duplicate).

        :returns: emoji with accompanying text
        :rtype: str
        """
        emoji_char = random.choice(
            [e for e in emoji.EMOJI_UNICODE.values() if len(e) == 1]
        )
        return '\n\n{}{}'.format(EMOJI_OF_THE_DAY_TEXT, emoji_char)

    def post(self):
        """
        Post status update on twitter.
        """
        tweet = self.get_random_tweet()

        # wait before posting a tweet
        sleep(self.get_wait_time(tweet))

        tweet_text = '{}{}'.format(
            tweet['text'],
            self.get_emoji_of_the_day_text()
        )

        self.api.update_status(
            status=tweet_text,
            lat='45.814632',  # this is fixed, duh
            long='15.973277'
        )


@iopipe.decorator
def post_tweet(event, context):
    """
    The method that scheduler will call.
    """
    poster = Poster()
    poster.post()
