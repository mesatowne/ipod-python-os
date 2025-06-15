#!/usr/bin/env python3
import os
import subprocess

def list_songs(directory="/root/music"):
    """List and play MP3 files in the provided directory."""

    try:
        files = [f for f in os.listdir(directory) if f.lower().endswith(".mp3")]
    except FileNotFoundError:
        print(f"Directory not found: {directory}")
        return

    if not files:
        print("No MP3s found in", directory)
        return

    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")

    try:
        choice = int(input("Choose: ")) - 1
        if choice < 0 or choice >= len(files):
            raise ValueError
    except ValueError:
        print("Invalid selection")
        return

    file_path = os.path.join(directory, files[choice])
    try:
        subprocess.run(["mpg123", file_path], check=True)
    except FileNotFoundError:
        print("mpg123 not installed or not in PATH")
    except subprocess.CalledProcessError as e:
        print("Error playing file:", e)

if __name__ == "__main__":
    list_songs()
