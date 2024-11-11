import praw
import random
import configparser
from gtts import gTTS
import re
import os

def sanitize_filename(title):
    # Remove invalid characters from the filename
    return re.sub(r'[<>:"/\\|?*]', '', title)

def fetch_reddit_post():
    config = configparser.ConfigParser()
    config.read('config.ini')

    client_id = config.get('default', 'client_id')
    client_secret = config.get('default', 'client_secret')
    user_agent = config.get('default', 'user_agent')

    # Initialize the Reddit API
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         user_agent=user_agent,
                         config_interpolation=None)

    subreddit_name = random.choice(['RedditStoryTime'])
    subreddit = reddit.subreddit(subreddit_name)

    # Keep choosing random posts until we find one with a long enough body
    while True:
        random_post = random.choice(list(subreddit.hot()))
        
        if len(random_post.selftext) > 1000:  # Minimum length
            break

    # Print post details
    print(f'SubReddit: {subreddit_name}')
    print("Title: ", random_post.title)
    print("Body: ", random_post.selftext)
    print(f'Score: {random_post.score}')
    print(f'URL: {random_post.url}')

    filtered_title = sanitize_filename(random_post.title)

    # Write to file
    with open(f"{filtered_title}.txt", "w", encoding="utf-8") as file:
        file.write(f"SubReddit: {subreddit_name}\n")
        file.write(f"Title: {random_post.title}\n")
        file.write(f"Body: {random_post.selftext}\n")
        file.write(f"Score: {random_post.score}\n")
        file.write(f"URL: {random_post.url}\n")

    # Text-to-speech for the post
    text_to_speak = f"{random_post.title}. {random_post.selftext}"
    tts = gTTS(text=text_to_speak, lang='en')
    audio_filename = f"{filtered_title}.mp3"
    tts.save(audio_filename)

    return filtered_title, audio_filename
