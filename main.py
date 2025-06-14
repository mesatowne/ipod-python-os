#!/usr/bin/env python3
import os
import subprocess

def list_songs(dir="/root/music"):
    try:
        files = [f for f in os.listdir(dir) if f.endswith(".mp3")]
        if not files:
            print("No MP3s found in", dir)
            return
        for i, f in enumerate(files):
            print(f"{i+1}. {f}")
        choice = int(input("Choose: ")) - 1
        subprocess.run(["mpg123", os.path.join(dir, files[choice])])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    list_songs()
