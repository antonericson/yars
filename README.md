#  🤖 YARS - Yet Another Reddit Story

👀 Automatically generate short form vertical videos for social media based on reddit threads. 👀

YARS will automatically fetch popular reddit threads from your choice of subreddits and convert the **title**, **body**, and **subreddit name** to a video for social media. The videos include a voice over reading the reddit thread generated using [Coqcui TTS](https://github.com/coqui-ai/TTS), a video running in the background transcoded and spliced using [ffmpeg-python](https://github.com/kkroening/ffmpeg-python), and subtitles in the middle of the screen all generated with [Remotion](https://github.com/remotion-dev/remotion).

## Initial setup
```bash
./setup.sh
```

## Manual initial setup

**Requirements:**
- Python 3.10.x
- Node 19.8.x

Install Python dependencies
```bash
pip install -r requirements.txt
```

Install npm dependencies
```bash
cd video-generation
npm install
```

Create `yars_secrets.py` at the project root with the following code
```JavaScript
reddit_user = 'Your_reddit_username'
reddit_pw = 'Your_reddit_password'
key = 'Your_reddit_key'
secret = 'Your_reddit_secret'
```

Create a folder in the project root called `background-videos` where you will place the source background video files. These will be transcoded and the audio will be removed during video generation.
## Running the program

```bash
python3 main.py
```

By default the program will generate one video to the `/out` folder. You can create a batch of videos by using the `-n (--number_of_videos)` flag.
```bash
python3 main.py -n 10 # Will (one by one) generate 10 videos to the /out folder
```

## Output

In the `/out` folder you should now see a folder for each of your generated videos, containing the `.mp4` video file and a `.txt` description file. The description file is intended to be used when posting to social media to always accompany the video with the authors name and a link to the original post on reddit.

The video file will be in `.mp4` format with `1080x1920` resolution 30 fps.
