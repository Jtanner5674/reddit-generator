from pydub import AudioSegment
import whisper
import random
import os
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

def generate_short(mp3_file, video_folder="backgrounds", output_file=None, overlay_audio=True):
    # Convert MP3 to WAV using Pydub
    audio = AudioSegment.from_file(mp3_file)
    wav_file = mp3_file.replace(".mp3", ".wav")
    audio.export(wav_file, format="wav")

    # Load the WAV file for Whisper transcription
    model = whisper.load_model("small")  # Use 'small' model for speed/accuracy balance
    result = model.transcribe(wav_file)
    transcription = result['text']

    # Load MP3 and get its duration
    audio_duration = len(audio) / 1000  # Convert to seconds

    # Use audio file name as default output file name if none is specified
    if output_file is None:
        audio_name = os.path.splitext(os.path.basename(mp3_file))[0]
        output_folder = "finals"
        os.makedirs(output_folder, exist_ok=True)  # Create folder if it doesn't exist
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

    # Split transcription into caption chunks
    caption_chunks = [transcription[i:i + 30] for i in range(0, len(transcription), 30)]
    chunk_duration = audio_duration / len(caption_chunks)
    
    # Create caption clips for each chunk
    caption_clips = []
    for i, chunk in enumerate(caption_chunks):
        caption = TextClip(chunk, fontsize=60, color='white', font='Arial', stroke_color='black', stroke_width=2)
        caption = caption.set_duration(chunk_duration).set_position(("center", 0.7 * video_clip.h)).set_start(i * chunk_duration)
        caption_clips.append(caption)

    # Overlay audio if specified
    if overlay_audio:
        audio_clip = AudioFileClip(mp3_file)
        video_clip = video_clip.set_audio(audio_clip)

    # Combine video and captions
    final_clip = CompositeVideoClip([video_clip] + caption_clips)
    
    # Write the final video
    final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")

# Usage example
mp3_file = "your_audio.mp3"
video_folder = "backgrounds"
generate_short(mp3_file, video_folder)
