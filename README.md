# MusicBot - Telegram Music & Video Downloader

24/7 Telegram bot for downloading music and videos from YouTube.

## Features
- 🎵 Search and download music from YouTube
- 🎬 Download videos in multiple qualities (360p, 480p, 720p, 1080p)
- 🎧 30-second preview before downloading
- 📹 Support for YouTube playlists
- 📊 Admin statistics and user management

## Deployment on Render.com

1. Fork this repository
2. Sign up at [Render.com](https://render.com)
3. Create a new Web Service
4. Connect your GitHub repository
5. Render will automatically detect the `render.yaml` configuration
6. Your bot will be deployed and running 24/7!

## Requirements
- Python 3.11
- python-telegram-bot
- yt-dlp

## Admin Commands
- `/admin_stats` - View bot statistics
- `/admin_users` - List all users
- `/broadcast <message>` - Send message to all users
- `/announce <message>` - Send announcement to all users
