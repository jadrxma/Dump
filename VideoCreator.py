import subprocess
import requests
import os
import tempfile

# Configuration for paths and API endpoints
RESOURCES_DIR = os.path.abspath('resources')
base_dir = "C:\\Users\\jad\\Desktop\\VideoProjects"
INTRO_PATH = f'{RESOURCES_DIR}/intro.mp3'
AUDIO_PATH = os.path.join(base_dir, 'audio.mp3')
FINAL_VIDEO_PATH = os.path.join(base_dir, 'final_video.mp4')
ELEVEN_LABS_API_KEY = '4c6dc7cd36fd2d2f34579c6f2fd80831'
PEXELS_API_KEY ='5fUtH4bdgqj7w5FxQq1veDhMJS5vFuTz4JGZJ4Kbwxlzu5m1EYTJh0co'
PEXELS_API_URL = 'https://api.pexels.com/videos/search'
Model_ID = 'GfIVpqb6MMu0aS33Uqvs'

def main():
    author = "Steve Jobs"
    quote = "The only way to do great work is to love what you do."

    background_video_path = fetch_stock_video("inspirational")
    audio_path = get_audio(quote)
    subs_path = generate_subtitles(quote, author)

    video_path = create_final_video(background_video_path, audio_path, subs_path)
    print(f'Video created at: {video_path}')

def fetch_stock_video(query):
    print('Fetching stock video from Pexels...')
    headers = {'Authorization': PEXELS_API_KEY}
    params = {'query': query, 'per_page': 1}  # Fetching one video based on the query

    try:
        response = requests.get(PEXELS_API_URL, headers=headers, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Python 3.6
        return None
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
        return None

    # Check if the response contains any videos
    try:
        video_data = response.json()
        video_url = video_data['videos'][0]['video_files'][0]['link']
    except (IndexError, KeyError) as e:
        print("No videos found or unexpected data format:", e)
        return None

    video_path = os.path.join(base_dir, 'background.mp4')
    try:
        with open(video_path, 'wb') as f:
            f.write(requests.get(video_url).content)
    except Exception as e:
        print("Failed to download the video:", e)
        return None

    return video_path


def get_audio(text):
    voice_id = "XRlny9TzSxQhHzOusWWe"  # Replace with your actual voice ID
    XI_API_KEY = '4c6dc7cd36fd2d2f34579c6f2fd80831'
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {'Content-Type': 'application/json',  "xi-api-key": XI_API_KEY}
    data = {
        'text': text,
        'model_id': 'eleven_monolingual_v1'  # Ensure this is correct
    }

    response = requests.post(url, headers=headers, json=data)
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

    if response.status_code == 200:
        with open(AUDIO_PATH, 'wb') as f:
            f.write(response.content)
        return AUDIO_PATH
    else:
        print("Failed to generate audio:", response.text)
        return None



def generate_subtitles(quote, author):
    subs_path = os.path.join(base_dir, 'subtitles.ass')
    with open(subs_path, 'w') as subs_file:
        subs_file.write(f"Dialogue: Marked=0,0:00:01.00,0:00:10.00,Default,,0000,0000,0000,,{quote}\n")
        subs_file.write(f"Dialogue: Marked=0,0:00:10.00,0:00:15.00,Default,,0000,0000,0000,,{author}\n")
    return subs_path


def escape_filepath(filepath):
    # Replace backslashes with double backslashes
    filepath = filepath.replace("\\", "\\\\")
    # Escape colons
    filepath = filepath.replace(":", "\\:")
    return filepath

def create_final_video(background_path, audio_path, subs_path):
    # Apply escaping to file paths
    background_path = escape_filepath(background_path)
    audio_path = escape_filepath(audio_path)
    subs_path = escape_filepath(subs_path)

    command = [
        'ffmpeg',
        '-i', f'"{background_path}"',
        '-i', f'"{audio_path}"',
        '-vf', f"ass='{subs_path}'",
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-strict', 'experimental',
        f'"{FINAL_VIDEO_PATH}"'
    ]

    print("Running FFmpeg command:", ' '.join(command))
    try:
        subprocess.run(' '.join(command), check=True, shell=True, text=True)
        print(f'Video created at: {FINAL_VIDEO_PATH}')
        return FINAL_VIDEO_PATH
    except subprocess.CalledProcessError as e:
        print("Failed to create video:", e)
        return None


if __name__ == '__main__':
    main()
