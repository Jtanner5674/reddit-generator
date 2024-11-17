import os
import subprocess
from datetime import timedelta
import whisper
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
from moviepy.video.tools.subtitles import SubtitlesClip

OUTPUT_SRT = "output.srt"
OUTPUT_VID = "output.mp4"

def check_ffmpeg() -> bool:
    """Check if FFmpeg is installed and available."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0 and 'ffmpeg' in result.stdout
    except FileNotFoundError:
        return False

def generate_and_attach_subtitles(audio_path: str, video_path: str) -> None:
    """
    Generate subtitles from the given audio file and attach them to the given video.

    Args:
        audio_path (str): Path to the audio file.
        video_path (str): Path to the video file.

    Raises:
        FileNotFoundError: If the audio or video file is not found.
    """
    if not check_ffmpeg():
        raise EnvironmentError("FFmpeg must be installed to use this function.")

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Generate subtitles using Whisper
    model = whisper.load_model("base")
    transcribe = model.transcribe(audio=audio_path, fp16=False)
    segments = transcribe["segments"]

    # Save subtitles to an SRT file
    with open(OUTPUT_SRT, "w", encoding="utf-8") as f:
        for seg in segments:
            start = str(0) + str(timedelta(seconds=int(seg["start"]))) + ",000"
            end = str(0) + str(timedelta(seconds=int(seg["end"]))) + ",000"
            text = seg["text"]
            segment_id = seg["id"] + 1
            segment = f"{segment_id}\n{start} --> {end}\n{text[1:] if text[0] == ' ' else text}\n\n"
            f.write(segment)

    print("Subtitles generated and saved to output.srt")

    # Attach subtitles to video
    video = VideoFileClip(video_path)
    subtitles = SubtitlesClip(
        OUTPUT_SRT,
        lambda txt: TextClip(
            txt,
            font="Arial",
            fontsize=24,
            color="white",
            bg_color="black",
        ),
    )
    video_with_subtitles = CompositeVideoClip(
        [
            video,
            subtitles.set_position(("center", 0.95), relative=True),
        ]
    )

    video_with_subtitles.write_videofile(OUTPUT_VID, codec="libx264")
    print(f"Video with subtitles saved to {OUTPUT_VID}")
