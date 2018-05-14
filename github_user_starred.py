#!/usr/bin/python3

"""github_user_starred - python script. Lists starred repositories by user"""

import requests
import argparse
import signal
import sys
import re

from json import JSONDecoder


JSON_DECODER = JSONDecoder()

RCODE_OK = 0
RCODE_ERR_INET = 1
RCODE_ERR404 = 2
RCODE_ERR_NO_STARS = 3
RCODE_ERR_BAD_NAME = 4

MSG_RCODE = {RCODE_ERR404: "No such user",
             RCODE_ERR_NO_STARS: "This user did not starred anything",
             RCODE_OK: "OK",
             RCODE_ERR_INET: "GitHub doesn't respond",
             RCODE_ERR_BAD_NAME: "Bad username"}


def get_starred_repos(username):
    """Return tuple(RCODE, generator(tuple(repository_url, stargazers_count)))

    Params:
        username: str - user login

    """
    try:
        if not check_username(username):
            return RCODE_ERR_BAD_NAME, None

        req = "/users/{}/starred".format(username)
        answer = requests.get("http://api.github.com" + req)

        if answer.status_code != 200:
            return RCODE_ERR404, None

        parsed = JSON_DECODER.decode(answer.text)
        if not parsed:
            return RCODE_ERR_NO_STARS, None

        repos = ((repo['url'], repo['stargazers_count']) for repo in parsed)
        return RCODE_OK, repos

    except requests.exceptions.ConnectionError:
        return RCODE_ERR_INET, None


def check_username(username):
    """Return True if name is ok"""
    m = re.match(r"^[A-Za-z_]\w*$", username)
    return bool(m)


def signal_handler(*args):
    print("Interrupted")
    sys.exit(2)


def init_argparser():
    parser = argparse.ArgumentParser(description="Uses GitHub API to get"
                                     "list of starred repositories by user.")
    parser.add_argument("user_login", action="store",
                        help="GitHub user's login")
    return parser


def main():
    signal.signal(signal.SIGINT, signal_handler)
    parser = init_argparser()
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args(sys.argv[1:])
    username = args.user_login
    rcode, repos = get_starred_repos(username)
    if rcode != RCODE_OK:
        print(MSG_RCODE[rcode])
    else:
        for repo, stars in repos:
            print("{} - {}".format(repo, stars))


if __name__ == '__main__':
    main()
