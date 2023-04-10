import ffmpeg
import random

# Replace with the path to your input video file
input_file = './background-videos/archive/reekVid1.mkv'

# Generate a random start time within the duration of the input video
duration = ffmpeg.probe(input_file)['format']['duration']
start_time = random.randint(5, int(float(duration)) - 80)

# Extract a 1 minute snippet starting from the randomly generated start time
output_file = 'randVideo3.mp4'
(
    ffmpeg
    .input(input_file, ss=start_time)
    .trim(start=0, duration=70)
    .filter('fps', fps=30, round='up')
    .output(output_file)
    .overwrite_output()
    .run()
)