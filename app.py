import streamlit as st
import yt_dlp
import os
from datetime import datetime

# FFmpeg path configuration
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"

# Download video function
def download_video(url, format_type, quality, output_dir, progress_callback=None):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    # Map UI quality to yt_dlp format string
    if format_type == 'mp4':
        quality_map = {
            "best": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
        }
        ydl_format = quality_map.get(quality, "bestvideo+bestaudio/best")
    else:  # mp3
        # For audio, select best audio or restrict by abr if possible
        audio_quality_map = {
            "320kbps": "bestaudio[abr<=320]",
            "192kbps": "bestaudio[abr<=192]",
            "128kbps": "bestaudio[abr<=128]",
            "64kbps":  "bestaudio[abr<=64]",
            "best":    "bestaudio/best"
        }
        ydl_format = audio_quality_map.get(quality, "bestaudio/best")

    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'format': ydl_format,
    }

    if format_type == 'mp3':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality.replace('kbps', ''),
        }]

    if os.path.exists(FFMPEG_PATH):
        ydl_opts['ffmpeg_location'] = FFMPEG_PATH

    # Add progress hook if provided
    if progress_callback:
        ydl_opts['progress_hooks'] = [progress_callback]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Streamlit app
def main():
    st.title("YouTube Downloader Pro")
    
    url = st.text_input("YouTube URL:")
    format_type = st.selectbox("Select Format:", ["mp4", "mp3"])
    quality = st.selectbox("Select Quality:", ["best", "1080p", "720p", "480p", "320kbps", "192kbps", "128kbps", "64kbps"])
    output_dir = st.text_input("Output Directory:", value=r"D:\youtube")

    progress_bar = st.progress(0, text="Waiting to start...")

    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = int(downloaded / total * 100)
                progress_bar.progress(percent, text=f"Downloading... {percent}%")
        elif d['status'] == 'finished':
            progress_bar.progress(100, text="Download finished!")

    if st.button("Download"):
        if url:
            with st.spinner("Downloading..."):
                try:
                    download_video(url, format_type, quality, output_dir, progress_callback=progress_hook)
                    st.success("Download completed successfully!")
                    # Show browser notification (Streamlit 1.23+)
                    try:
                        st.toast("Download completed!", icon="✅")
                    except Exception:
                        pass
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.error("Please enter a valid YouTube URL.")

if __name__ == "__main__":
    main()