"""This module creates {username}/{project} folders
and download the avatar picture files with names
that match GitHub contributor’s login"""
import argparse
import json
import os
import requests


parser = argparse.ArgumentParser(description='Extract github avatars')
parser.add_argument('-u', "--user", action='store', #required = True,
                    default='kennethreitz', help = 'GitHub user login')
parser.add_argument('-p', "--project", action='store', #required = True,
                    default='requests', help = 'GitHub project name')
parser.add_argument('-l', "--login", action='store', #required = True,
                    help = 'GitHub user login for authorization')
parser.add_argument('-t', "--token", action='store', #required = True,
                    help = 'GitHub token')
args = parser.parse_args()

gh_session = requests.Session()
gh_session.auth = (args.login, args.token)


def get_contributors_avatar_dict(api_url):
    """This function builds dictionary with contributors login and their avatars url"""
    contributors_avatar = []
    while api_url is not None:
        response = gh_session.get(api_url)
        json_data = json.loads(response.text)

        for record in json_data:
            contributors_avatar.append({'login': record['login'],
                                        'avatar_url':record['avatar_url']})

        if 'next' in response.links.keys():
            api_url = response.links['next']['url']
        else:
            api_url = None
    return contributors_avatar


URL = f'https://api.github.com/repos/{args.user}/{args.project}/contributors?page=1&per_page=All'

contributors_avatar_dict = get_contributors_avatar_dict(URL)

folder_name = "{}{}{}".format(args.user, os.sep, args.project)
os.makedirs(folder_name, exist_ok=True)


for contributor in contributors_avatar_dict:
    contributor_response = gh_session.get(contributor['avatar_url'], stream=True)
    file_extension = contributor_response.headers['Content-Type'].split('/')[1]

    if file_extension in ['jpeg', 'png']:
        image_name = os.path.join(folder_name, '.'.join((contributor["login"], file_extension)))
        with open(image_name, 'wb') as image:
            for chunk in contributor_response.iter_content(chunk_size=128):
                image.write(chunk)
