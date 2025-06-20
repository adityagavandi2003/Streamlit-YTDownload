import streamlit as st
import yt_dlp
import os
import glob
from datetime import datetime

# Download video function
def download_video(url, format_type, quality, output_dir, progress_callback=None):
    os.makedirs(output_dir, exist_ok=True)
    if format_type == 'mp4':
        quality_map = {
            "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "1080p": "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]/best[height<=1080]",
            "720p": "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]/best[height<=720]",
            "480p": "bestvideo[ext=mp4][height<=480]+bestaudio[ext=m4a]/best[ext=mp4][height<=480]/best[height<=480]",
        }
        ydl_format = quality_map.get(quality, "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")
        ydl_opts = {
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'format': ydl_format,
        }
        # Add postprocessor to convert to mp4 if not already
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }]
    else:  # mp3
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
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality.replace('kbps', ''),
            }]
        }

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
    # Remove output_dir input from GUI, use a fixed directory
    output_dir = "./downloads"  # Use a Linux-friendly default

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
                    try:
                        st.toast("Download completed!", icon="✅")
                    except Exception:
                        pass

                    # Find the most recent file in the output_dir
                    files = glob.glob(os.path.join(output_dir, '*'))
                    if files:
                        latest_file = max(files, key=os.path.getctime)
                        file_name = os.path.basename(latest_file)
                        with open(latest_file, "rb") as f:
                            file_bytes = f.read()
                        mime = "video/mp4" if format_type == "mp4" else "audio/mpeg"
                        st.info("Your file is ready! Click the button below to download.")
                        st.download_button(
                            label=f"Download {file_name}",
                            data=file_bytes,
                            file_name=file_name,
                            mime=mime
                        )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.error("Please enter a valid YouTube URL.")

if __name__ == "__main__":
    main()