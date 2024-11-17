from post_puller import fetch_reddit_post
from video_generator import generate_short
from subtitler import generate_and_attach_subtitles

def main():
    filtered_title, audio_filename = fetch_reddit_post()
    generate_short(audio_filename, overlay_audio=False)

if __name__ == "__main__":
    main()

 