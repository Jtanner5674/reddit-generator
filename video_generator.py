from pydub import AudioSegment
import random
import os
import textwrap
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
import moviepy.editor as mp
from subtitler import generate_and_attach_subtitles  # Import the function we created

os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"


def generate_short(mp3_file, video_folder="backgrounds/temp", output_file=None, overlay_audio=True):
    # Convert MP3 to WAV using Pydub
    audio = AudioSegment.from_file(mp3_file)
    wav_file = mp3_file.replace(".mp3", ".wav")
    audio.export(wav_file, format="wav")

    # Load MP3 and get its duration
    audio_duration = len(audio) / 1000  # Convert to seconds

    # Use audio file name as default output file name if none is specified
    if output_file is None:
        audio_name = os.path.splitext(os.path.basename(mp3_file))[0]
        output_folder = "finals"
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f"{audio_name}_short.mp4")

    # Get a list of all video files in the folder
    video_files = [os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.endswith(('.mp4', '.mov'))]
    
    # Select a random video file
    video_path = random.choice(video_files)
    video = VideoFileClip(video_path)
    
    # Select a random start time, ensuring it fits within the video duration
    max_start = max(0, video.duration - audio_duration)
    start_time = random.uniform(0, max_start)
    
    # Cut the video to match the audio duration
    video_clip = video.subclip(start_time, start_time + audio_duration)
    
    # Resize and crop the video to a vertical 9:16 aspect ratio (1080x1920)
    video_clip = video_clip.resize(width=1080)
    video_clip = video_clip.crop(width=1080, height=1920, x_center=video_clip.w / 2, y_center=video_clip.h / 2)

    # Generate subtitles and attach them to the video
    temp_output_file = "temp_with_subtitles.mp4"
    try:
        generate_and_attach_subtitles(mp3_file, temp_output_file)  # Using our custom function
        temp_video_clip = VideoFileClip(temp_output_file)
    except Exception as e:
        print(f"Error generating subtitles: {e}")
        return

    # Overlay audio if specified
    if overlay_audio:
        audio_clip = AudioFileClip(mp3_file)
        temp_video_clip = temp_video_clip.set_audio(audio_clip)

    # Write the final video
    temp_video_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")
    print(f"Final video saved to {output_file}")

    # Cleanup temporary files
    if os.path.exists(temp_output_file):
        os.remove(temp_output_file)
    if os.path.exists(wav_file):
        os.remove(wav_file)
