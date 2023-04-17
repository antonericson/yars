#  🤖 YARS - Yet Another Reddit Story

[![ESLint](https://github.com/antonericson/yars/actions/workflows/eslint.yml/badge.svg)](https://github.com/antonericson/yars/actions/workflows/eslint.yml) [![Pylint](https://github.com/antonericson/yars/actions/workflows/pylint.yml/badge.svg)](https://github.com/antonericson/yars/actions/workflows/pylint.yml)

👀 Automatically generate short form vertical videos for social media based on reddit threads. 👀

YARS will automatically fetch popular reddit threads from your choice of subreddits and convert the **title**, **body**, and **subreddit name** to a video for social media. The videos include a voice over reading the reddit thread generated using [Coqcui TTS](https://github.com/coqui-ai/TTS), a video running in the background transcoded and spliced using [ffmpeg-python](https://github.com/kkroening/ffmpeg-python), and subtitles in the middle of the screen all generated with [Remotion](https://github.com/remotion-dev/remotion).

## Running the program

**Requirements:**
- Python 3.10.x
- Node 19.8.x
- eSpeak 1.48.x

Run inital setup script:

```bash
./setup.sh
```

Then you can run the program with:

```bash
python3 main.py
```

### Output

In the `/out` folder you should now see a folder for each of your generated videos, containing the `.mp4` video file and a `.txt` description file. The description file is intended to be used when posting to social media to always accompany the video with the authors name and a link to the original post on reddit.

The video file will be in `.mp4` format with `1080x1920` resolution 30 fps.
