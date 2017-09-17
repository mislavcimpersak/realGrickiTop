import json
import os

import vcr


def load_secrets_to_env():
    """
    Use local `secrets.json` file with credentials for testing and dump its
    content to env vars.
    """
    with open('secrets.json', 'r') as f:
        for env_name, env_value in json.loads(f.read()).items():
            os.environ[env_name] = env_value

load_secrets_to_env()

tape = vcr.VCR(
    serializer='json',
    cassette_library_dir='cassettes',
    filter_headers=['Authorization'],
    record_mode='once',
    match_on=['uri', 'method'],
    path_transformer=vcr.VCR.ensure_suffix('.json')
)
