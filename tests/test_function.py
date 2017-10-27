import json
import os
import re

import responses

from main import Poster
from .config import tape


def test_dummy():
    assert 1 + 1 == 2


def test_data_tweets_json_file_is_valid():
    assert json.loads(open('data/tweets.json', 'r').read())


# @tape.use_cassette('test_poster.json')
# def test_poster__set_twitter_api():
#     poster = Poster()
#     assert poster.api.me().screen_name == 'realGrickiTop'


# @tape.use_cassette('test_poster.json')
# def test_poster__set_last_n_tweets():
#     poster = Poster()
#     assert len(poster.last_n_tweets) == 9


# @tape.use_cassette('test_poster.json')
# def test_poster__get_wait_time__with_debug():
#     os.environ['DEBUG'] = 'True'

#     poster = Poster()
#     tweet = {
#         "text": "BOOM!",
#         "time_span": "before"
#     }

#     wait_time = poster.get_wait_time(tweet)
#     assert wait_time == 0
