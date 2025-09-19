# Timelink Discord Bot

A Discord bot designed for various utilities like interacting with users, showing real-time bus data, Reddit memes, and leveling systems. This bot uses the `discord.py` library and integrates multiple functionalities, including real-time GTFS data, Reddit memes, and a leveling system for users.

## Features
- **Hello Command**: Responds with a greeting when a user types `.hello`.
- **Good Morning Command**: Sends a good morning message when `.goodmorning` is used.
- **Embed Command**: Sends a customizable embedded message with fields and images when `.sendembed` is called.
- **Leveling System**: Tracks user XP and levels up users based on message activity.
- **Reddit Meme Fetching**: Fetches random memes from the r/memes subreddit and shares them in Discord.
- **GTFS Real-Time Integration**: Fetches real-time bus arrival data using the **TransLink** API with the `.routes <stop_code>` command.

---

## Requirements

- **Python 3.8+**
- **Dependencies**:
    - `discord.py`
    - `python-dotenv`
    - `asyncpraw`
    - `pandas`
    - `requests`
    - `google.transit`
    - `sqlite3` (for the leveling system)

You can install the required dependencies using:

```bash
pip install -r requirements.txt


