import cv2
import numpy as np
import re
import subprocess
import os

def sanitize_filename(title):
    return re.sub(r'[<>:"/\\|?*]', '', title).strip()

def wrap_text(text, font, max_width):
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        line_size = cv2.getTextSize(test_line, font, 1, 2)[0]
        if line_size[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)

    return lines

def split_text(text, max_length=200):
    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_length:
            current_chunk += f" {word}"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word

    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def generate_video(original_title):
    filtered_title = sanitize_filename(original_title)
    post_folder = os.path.join("posts", filtered_title)
    os.makedirs(post_folder, exist_ok=True)

    text_filename = f"{filtered_title}.txt"
    
    # Read and process lines with error handling
    subreddit_name = "Unknown"
    title = "No Title"
    body = "No Body"

    with open(text_filename, "r", encoding="utf-8") as file:
        lines = file.readlines()
        
        # Check each line for expected formatting
        for line in lines:
            if line.startswith("SubReddit: "):
                subreddit_name = line.strip().split(": ", 1)[1]
            elif line.startswith("Title: "):
                title = line.strip().split(": ", 1)[1]
            elif line.startswith("Body: "):
                body = line.strip().split(": ", 1)[1]

    sanitized_body = body.replace('\n', ' ').replace('\r', ' ')
    sanitized_filename = os.path.join(post_folder, f"{filtered_title}_sanitized.txt")
    with open(sanitized_filename, "w", encoding="utf-8") as sanitized_file:
        sanitized_file.write(sanitized_body)

    audio_filename = f"{filtered_title}.mp3"

    width, height = 1280, 720
    fps = 24
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_file = os.path.join(post_folder, f"{filtered_title}.mp4")
    out = cv2.VideoWriter(video_file, fourcc, fps, (width, height))

    background = np.zeros((height, width, 3), dtype=np.uint8)
    print(f"Background shape: {background.shape}")

    title_font = cv2.FONT_HERSHEY_SIMPLEX
    title_lines = wrap_text(title, title_font, width - 20)

    # Display title for a few seconds
    for line_num, line in enumerate(title_lines):
        if not isinstance(line, str) or not line.strip():
            print(f"Skipping invalid line: {line}")
            continue

        print(f"Attempting to draw text: '{line}'")
        title_size = cv2.getTextSize(line, title_font, 1.5, 2)[0]
        title_x = (width - title_size[0]) // 2
        title_y = (height // 4) + (line_num * 50)

        title_x = int(round(title_x))
        title_y = int(round(title_y))

        cv2.putText(background, line, (title_x, title_y), title_font, 1.5, (255, 255, 255), 2, cv2.LINE_AA)

    for _ in range(fps * 3):  # Display the title for 3 seconds
        out.write(background)

    # Reset background for body text display
    body_chunks = split_text(sanitized_body, max_length=200)
    duration_per_chunk = 10 / len(body_chunks)

    for chunk in body_chunks:
        background[:] = 0
        body_lines = wrap_text(chunk, title_font, width - 20)

        for line_num, line in enumerate(body_lines):
            print(f"Attempting to draw text: '{line}'")
            text_size = cv2.getTextSize(line, title_font, 1.5, 2)[0]
            text_x = (width - text_size[0]) // 2
            text_y = (height // 4) + (line_num * 50)

            text_x = max(0, int(round(text_x)))
            text_y = max(0, int(round(text_y)))

            cv2.putText(background, line, (text_x, text_y), title_font, 1.5, (255, 255, 255), 2, cv2.LINE_AA)

        for _ in range(int(fps * duration_per_chunk)):
            out.write(background)

    out.release()

    finals_folder = "finals"
    os.makedirs(finals_folder, exist_ok=True)

    final_video_file = os.path.join(finals_folder, f"{filtered_title}.mp4")
    subprocess.run(['ffmpeg', '-i', video_file, '-i', audio_filename, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', final_video_file])

    print(f"Video saved as {final_video_file}")