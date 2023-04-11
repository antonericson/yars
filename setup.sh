#!/bin/bash

# Function to check if a file exists
file_exists() {
  if [ -e "$1" ]; then
    return 0 # File exists
  else
    return 1 # File does not exist
  fi
}

# Function to check if a directory exists
dir_exists() {
  if [ -d "$1" ]; then
    return 0 # Directory exists
  else
    return 1 # Directory does not exist
  fi
}

# Verify Python 3.10.x installation
if ! python3.10 --version &>/dev/null; then
  echo "Python 3.10.x is not installed. Please install Python 3.10.x and try again."
  exit 1
fi

# Verify Node 19.8.x installation
if ! node --version | grep -qE "^v19\.8\."; then
  echo "Node 19.8.x is not installed. Please install Node 19.8.x and try again."
  exit 1
fi

# Install Python requirements
pip install -r requirements.txt

# Install Node dependencies
cd video-generation
npm install
cd ..

# Create additional files and directories if they do not exist
if ! file_exists "yars_secrets.py"; then
  echo "reddit_user = 'Your_reddit_username'" > yars_secrets.py
  echo "reddit_pw = 'Your_reddit_password'" >> yars_secrets.py
  echo "key = 'Your_reddit_key'" >> yars_secrets.py
  echo "secret = 'Your_reddit_secret'" >> yars_secrets.py
  echo "yars_secrets.py generated successfully."
else
  echo "yars_secrets.py already exists. Skipping generation."
fi

if ! dir_exists "extracted-posts"; then
  mkdir extracted-posts
  echo "extracted-posts directory created successfully."
else
  echo "extracted-posts folder already exists. Skipping generation."
fi

if ! dir_exists "background-videos"; then
  mkdir background-videos
  echo "background-videos directory created successfully."
else
  echo "background-videos folder already exists. Skipping generation."
fi

if ! dir_exists "video-generation/public"; then
  mkdir video-generation/public
  echo "video-generation/public directory created successfully."
else
  echo "video-generation/public folder already exists. Skipping generation."
fi

if ! dir_exists "video-generation/public/audio"; then
  mkdir video-generation/public/audio
  echo "video-generation/public/audio directory created successfully."
else
  echo "video-generation/public/audio folder already exists. Skipping generation."
fi

if ! dir_exists "video-generation/public/video"; then
  mkdir video-generation/public/video
  echo "video-generation/public/video directory created successfully."
else
  echo "video-generation/public/video folder already exists. Skipping generation."
fi

echo "Setup completed successfully!"
