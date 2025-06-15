# ipod-python-os
## Quick Build

```bash
git clone https://github.com/mesatowne/ipod-python-os.git
cd buildroot
cp ../ipod-python-os/.config .
make -j$(nproc)
```

## Running the MP3 player

Use `main.py` to play MP3 files. Provide a directory on the command line or set the `MUSIC_DIR` environment variable:

```bash
python3 main.py /path/to/mp3s
# or
MUSIC_DIR=/path/to/mp3s python3 main.py
```
