import sys
import praw
import time
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
CONFIG_FILE='./config.json'

def handle_post(submission):
    url = submission.shortlink
    title = submission.title
    sub = submission.subreddit.display_name

    if config['keywords']['enabled']:
        if any(x.lower() in title.lower() for x in config['keywords']['list']):
            print(title)
            notify(sub, title, url)
    else:
        notify(sub, title, url)

def handle_modqueue(item):
    url = 'https://reddit.com' + item.permalink
    sub = item.subreddit.display_name
    notify(sub, 'Modqueue', url)

def notify(subreddit, title, url):
    if first: return
    print("print config slack",config['slack']['enabled'])
    if config['slack']['enabled']:
        notify_slack(subreddit, title, url)
    if config['reddit_pm']['enabled']:
        notify_reddit(subreddit, title, url)
    if config['debug']:
        print(subreddit + ' | ' + title + ' | ' +  url)

def notify_slack(subreddit, title, url):
    message = title + " | " + url
    payload = { 'text': message }
    headers = { 'Content-Type': 'application/json', }
    print(os.environ.get("webhook"),payload,config['keywords']['list'])
    requests.post(os.environ.get("webhook"), data=json.dumps(payload), headers=headers)

def notify_reddit(subreddit, title, url):
    if title == 'Modqueue':
        subject = 'New item in modqueue on /r/' + subreddit + '!'
    else:
        subject = 'New post on /r/' + subreddit + '!'

    message = '[' + title + '](' + url + ')'

    for user in config['reddit_pm']['users']:
        r.redditor(user).message(subject, message)

def start_streams():
    modqueue_stream = (r.subreddit('mod').mod.stream.modqueue(pause_after=-1)
                       if config['modqueue'] else [])
    submission_stream = (r.subreddit(subreddits).stream.submissions(pause_after=-1)
                         if config['new_posts'] else [])
    return modqueue_stream, submission_stream

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

r = praw.Reddit(
    user_agent = config['reddit']['user_agent'],
    client_id = os.environ.get("client_id"),
    client_secret = os.environ.get("client_secret"),
    username = os.environ.get("username_1"),
    password = os.environ.get("password")
)
first = True
subreddits = '+'.join(config['subreddits'])
(modqueue_stream, submission_stream) = start_streams()
requests.post(os.environ.get("webhook"), data=json.dumps({ 'text':"starting script"}))
while True:
    try:
        for item in modqueue_stream:
            
            if item is None:
                break
            print(modqueue_stream.item)
            handle_modqueue(item)

        for submission in submission_stream:
            if submission is None:
                break
            handle_post(submission)

        first = False
        time.sleep(1)
    except KeyboardInterrupt:
        requests.post(os.environ.get("webhook"), data=json.dumps("keyboard"), )
        
        print('\n')
        sys.exit(0)
    except Exception as e:
        requests.post(os.environ.get("webhook"), data=json.dumps(e), )
        print('Error:', e)
        time.sleep(30)
        (modqueue_stream, submission_stream) = start_streams()

