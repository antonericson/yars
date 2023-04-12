#!/bin/bash

# Run Pylint on all Python files in the current directory
echo "Running Pylint on Python files..."
pylint *.py

# Move to the 'video-generation' directory
cd video-generation

# Run ESLint on all TypeScript files in the 'video-generation' directory
echo "Running ESLint on TypeScript files..."
npx eslint src --ext ts,tsx,js,jsx && npx tsc