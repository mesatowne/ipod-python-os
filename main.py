#!/usr/bin/env python3
import os
import subprocess
import argparse


def find_music_dir(default="/root/music"):
    """Return directory for MP3 files.

    Uses the MUSIC_DIR environment variable if set, otherwise the provided
    default path.
    """
    return os.getenv("MUSIC_DIR", default)

def list_songs(directory):
    """Return a sorted list of MP3 files in the directory."""

    try:
        files = [f for f in os.listdir(directory) if f.lower().endswith(".mp3")]
    except FileNotFoundError:
        print(f"Directory not found: {directory}")
        return

    if not files:
        print("No MP3s found in", directory)
        return

    return sorted(files)


def run_player(directory):
    """Display songs and handle playback selection in a loop."""

    songs = list_songs(directory)
    if not songs:
        return

    while True:
        for i, f in enumerate(songs, 1):
            print(f"{i}. {f}")

        choice = input("Choose number or 'q' to quit: ")
        if choice.lower() == "q":
            break

        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(songs):
                raise ValueError
        except ValueError:
            print("Invalid selection")
            continue

        file_path = os.path.join(directory, songs[idx])
        try:
            subprocess.run(["mpg123", file_path], check=True)
        except FileNotFoundError:
            print("mpg123 not installed or not in PATH")
            break
        except subprocess.CalledProcessError as e:
            print("Error playing file:", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple MP3 player")
    parser.add_argument("directory", nargs="?", default=find_music_dir(),
                        help="Directory containing MP3 files")
    args = parser.parse_args()
    run_player(args.directory)
