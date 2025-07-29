import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import subprocess
from pytubefix import YouTube, exceptions
import re
import shutil

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader (High Resolution)")
        self.root.geometry("650x500")
        self.root.resizable(True, True)
        
        # Set theme colors (dark theme for Kali Linux)
        self.bg_color = "#2e3436"
        self.fg_color = "#d3d7cf"
        self.accent_color = "#729fcf"
        self.button_color = "#3465a4"
        
        self.root.configure(bg=self.bg_color)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Application title
        title_label = tk.Label(
            main_frame, 
            text="YouTube Downloader (High Resolution)", 
            font=("Helvetica", 16, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(pady=(0, 20))
        
        # URL input
        url_frame = tk.Frame(main_frame, bg=self.bg_color)
        url_frame.pack(fill=tk.X, pady=(0, 15))
        
        url_label = tk.Label(
            url_frame, 
            text="YouTube URL:", 
            bg=self.bg_color,
            fg=self.fg_color
        )
        url_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.url_entry = tk.Entry(url_frame, width=50, bg="#555753", fg=self.fg_color, insertbackground=self.fg_color)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # File format selection
        format_frame = tk.Frame(main_frame, bg=self.bg_color)
        format_frame.pack(fill=tk.X, pady=(0, 15))
        
        format_label = tk.Label(
            format_frame, 
            text="Format:", 
            bg=self.bg_color,
            fg=self.fg_color
        )
        format_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.format_var = tk.StringVar(value="mp4")
        
        mp4_radio = tk.Radiobutton(
            format_frame, 
            text="MP4 (Video)", 
            variable=self.format_var,
            value="mp4",
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor="#555753",
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        mp4_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        mp3_radio = tk.Radiobutton(
            format_frame, 
            text="MP3 (Audio)", 
            variable=self.format_var,
            value="mp3",
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor="#555753",
            activebackground=self.bg_color,
            activeforeground=self.fg_color
        )
        mp3_radio.pack(side=tk.LEFT)
        
        # Resolution selection (only for MP4)
        resolution_frame = tk.Frame(main_frame, bg=self.bg_color)
        resolution_frame.pack(fill=tk.X, pady=(0, 15))
        
        resolution_label = tk.Label(
            resolution_frame, 
            text="Resolution:", 
            bg=self.bg_color,
            fg=self.fg_color
        )
        resolution_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.resolution_var = tk.StringVar(value="highest")
        resolutions = ["highest", "4K", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
        
        self.resolution_dropdown = ttk.Combobox(
            resolution_frame, 
            textvariable=self.resolution_var,
            values=resolutions,
            state="readonly",
            width=10
        )
        self.resolution_dropdown.pack(side=tk.LEFT)

        # Audio quality (for MP3)
        audioquality_frame = tk.Frame(main_frame, bg=self.bg_color)
        audioquality_frame.pack(fill=tk.X, pady=(0, 15))
        
        audioquality_label = tk.Label(
            audioquality_frame, 
            text="Audio Quality:", 
            bg=self.bg_color,
            fg=self.fg_color
        )
        audioquality_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.audioquality_var = tk.StringVar(value="best")
        audioqualities = ["best", "high", "medium", "low"]
        
        self.audioquality_dropdown = ttk.Combobox(
            audioquality_frame, 
            textvariable=self.audioquality_var,
            values=audioqualities,
            state="readonly",
            width=10
        )
        self.audioquality_dropdown.pack(side=tk.LEFT)
        
        # Download location
        location_frame = tk.Frame(main_frame, bg=self.bg_color)
        location_frame.pack(fill=tk.X, pady=(0, 15))
        
        location_label = tk.Label(
            location_frame, 
            text="Save to:", 
            bg=self.bg_color,
            fg=self.fg_color
        )
        location_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.location_entry = tk.Entry(location_frame, width=40, bg="#555753", fg=self.fg_color, insertbackground=self.fg_color)
        self.location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        # Set default download location to user's Downloads folder
        default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.location_entry.insert(0, default_path)
        
        browse_button = tk.Button(
            location_frame, 
            text="Browse", 
            command=self.browse_location,
            bg=self.button_color,
            fg=self.fg_color,
            activebackground=self.accent_color,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=10
        )
        browse_button.pack(side=tk.LEFT)
        
        # Progress frame
        progress_frame = tk.Frame(main_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            length=100,
            mode="determinate"
        )
        self.progress_bar.pack(fill=tk.X)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(
            progress_frame, 
            textvariable=self.status_var,
            bg=self.bg_color,
            fg=self.fg_color
        )
        status_label.pack(fill=tk.X, pady=(5, 0))
        
        # Download button
        download_button = tk.Button(
            main_frame, 
            text="Download", 
            command=self.start_download,
            bg=self.button_color,
            fg=self.fg_color,
            activebackground=self.accent_color,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            padx=20,
            pady=10,
            font=("Helvetica", 12)
        )
        download_button.pack(pady=(0, 15))
        
        # Video info frame
        info_frame = tk.LabelFrame(
            main_frame, 
            text="Video Information", 
            bg=self.bg_color,
            fg=self.fg_color
        )
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(
            info_frame, 
            height=5,
            wrap=tk.WORD,
            bg="#555753",
            fg=self.fg_color,
            insertbackground=self.fg_color,
            state=tk.DISABLED
        )
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Format binding
        self.format_var.trace_add("write", self.toggle_format_specific_options)
    
    def toggle_format_specific_options(self, *args):
        if self.format_var.get() == "mp3":
            self.resolution_dropdown.config(state="disabled")
            self.audioquality_dropdown.config(state="readonly")
        else:
            self.resolution_dropdown.config(state="readonly")
            self.audioquality_dropdown.config(state="disabled")
    
    def browse_location(self):
        directory = filedialog.askdirectory()
        if directory:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, directory)
    
    def update_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        self.progress_var.set(percentage)
        self.status_var.set(f"Downloading... {percentage:.1f}%")
        self.root.update_idletasks()
    
    def validate_youtube_url(self, url):
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        match = re.match(youtube_regex, url)
        return bool(match)
    
    def check_ffmpeg(self):
        """Check if ffmpeg is installed on the system"""
        try:
            subprocess.run(["ffmpeg", "-version"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            return False
    
    def find_nearest_resolution(self, streams, target_res):
        """Find the nearest resolution to the target"""
        res_mapping = {
            "4K": "2160p",
            "1440p": "1440p",
            "1080p": "1080p",
            "720p": "720p",
            "480p": "480p",
            "360p": "360p",
            "240p": "240p",
            "144p": "144p"
        }
        
        # Convert target to standard format
        target = res_mapping.get(target_res, target_res)
        
        # If target is "highest", return the highest resolution
        if target == "highest":
            return streams.get_highest_resolution()
        
        # Try to find exact match first
        stream = streams.filter(resolution=target).first()
        if stream:
            return stream
        
        # If no exact match, find nearest match
        available_res = []
        for s in streams:
            if s.resolution:
                try:
                    # Extract numeric part of resolution (e.g., "1080p" -> 1080)
                    res_num = int(s.resolution[:-1])
                    available_res.append((s, res_num))
                except ValueError:
                    continue
        
        if not available_res:
            return streams.get_highest_resolution()
        
        # Sort by resolution
        available_res.sort(key=lambda x: x[1], reverse=True)
        
        try:
            target_num = int(target[:-1])
            
            # Find nearest resolution
            for s, res_num in available_res:
                if res_num <= target_num:
                    return s
                    
            # If all resolutions are higher than target, return the lowest
            return available_res[-1][0]
        except ValueError:
            # In case of parsing error, return highest resolution
            return available_res[0][0]
    
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        if not self.validate_youtube_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL")
            return
        
        location = self.location_entry.get().strip()
        if not location:
            messagebox.showerror("Error", "Please select a download location")
            return
        
        if not os.path.exists(location):
            try:
                os.makedirs(location)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create directory: {str(e)}")
                return
        
        # For high resolution videos, we need ffmpeg
        if self.format_var.get() == "mp4" and self.resolution_var.get() in ["4K", "1440p", "1080p"]:
            if not self.check_ffmpeg():
                messagebox.showerror(
                    "Error", 
                    "ffmpeg is required for high resolution downloads but is not installed. "
                    "Please install ffmpeg and try again."
                )
                return
        
        # Disable UI during download
        self.url_entry.config(state=tk.DISABLED)
        self.location_entry.config(state=tk.DISABLED)
        self.resolution_dropdown.config(state=tk.DISABLED)
        self.audioquality_dropdown.config(state=tk.DISABLED)
        
        # Start download in a separate thread
        download_thread = Thread(target=self.download_video)
        download_thread.daemon = True
        download_thread.start()
    
    def display_video_info(self, yt):
        # Enable text widget for editing
        self.info_text.config(state=tk.NORMAL)
        # Clear previous content
        self.info_text.delete(1.0, tk.END)
        
        # Insert video information
        info = f"Title: {yt.title}\n"
        info += f"Channel: {yt.author}\n"
        info += f"Length: {yt.length // 60}:{yt.length % 60:02d}\n"
        info += f"Views: {yt.views:,}\n"
        
        # Show available resolutions
        available_res = set()
        for stream in yt.streams.filter(type="video"):
            if stream.resolution:
                available_res.add(stream.resolution)
        
        if available_res:
            info += f"Available resolutions: {', '.join(sorted(available_res, key=lambda x: int(x[:-1]) if x[:-1].isdigit() else 0, reverse=True))}\n"
        
        self.info_text.insert(tk.END, info)
        # Disable editing
        self.info_text.config(state=tk.DISABLED)
    
    def download_video(self):
        url = self.url_entry.get().strip()
        location = self.location_entry.get().strip()
        file_format = self.format_var.get()
        resolution = self.resolution_var.get()
        audio_quality = self.audioquality_var.get()
        
        try:
            self.status_var.set("Fetching video information...")
            yt = YouTube(url, on_progress_callback=self.update_progress)
            
            # Display video information
            self.display_video_info(yt)
            
            # Download based on format
            if file_format == "mp4":
                self.status_var.set("Preparing to download video...")
                
                if resolution in ["4K", "1440p", "1080p"] and self.check_ffmpeg():
                    # For high resolution, we need to download video and audio separately and merge
                    self.status_var.set(f"Downloading high resolution video in {resolution}...")
                    
                    # Map our resolution names to pytube resolution strings
                    res_map = {
                        "4K": "2160p",
                        "1440p": "1440p",
                        "1080p": "1080p"
                    }
                    target_res = res_map.get(resolution, resolution)
                    
                    # Get best video stream (without audio)
                    video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True)
                    video_stream = self.find_nearest_resolution(video_stream, target_res)
                    
                    if not video_stream:
                        raise Exception(f"No suitable video stream found for resolution {resolution}")
                    
                    self.status_var.set(f"Downloading video stream in {video_stream.resolution}...")
                    video_file = video_stream.download(output_path=location, filename_prefix="video_")
                    
                    # Get best audio stream
                    self.status_var.set("Downloading audio stream...")
                    audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).first()
                    if not audio_stream:
                        raise Exception("No suitable audio stream found")
                        
                    audio_file = audio_stream.download(output_path=location, filename_prefix="audio_")
                    
                    # Merge streams using ffmpeg
                    self.status_var.set("Merging video and audio streams...")
                    
                    # Create safe filename by replacing problematic characters
                    safe_title = yt.title.replace('/', '_').replace('\\', '_').replace('"', "'").replace(':', '-')
                    output_file = os.path.join(location, safe_title + ".mp4")
                    
                    cmd = [
                        "ffmpeg", "-y",
                        "-i", video_file,
                        "-i", audio_file,
                        "-c:v", "copy",
                        "-c:a", "aac",
                        output_file
                    ]
                    
                    process = subprocess.run(cmd, 
                                           stdout=subprocess.PIPE, 
                                           stderr=subprocess.PIPE)
                    
                    if process.returncode != 0:
                        raise Exception(f"Failed to merge streams: {process.stderr.decode()}")
                    
                    # Clean up temporary files
                    os.remove(video_file)
                    os.remove(audio_file)
                    
                else:
                    # For lower resolutions, use progressive streams (video + audio)
                    stream = yt.streams.filter(progressive=True)
                    stream = self.find_nearest_resolution(stream, resolution)
                    
                    self.status_var.set(f"Downloading video in {stream.resolution}...")
                    output_file = stream.download(output_path=location)
                
            else:  # mp3
                self.status_var.set("Preparing to download audio...")
                
                # Get audio quality
                audio_stream = None
                if audio_quality == "best" or audio_quality == "high":
                    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
                elif audio_quality == "medium":
                    # Try to get a middle quality
                    streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
                    streams_list = list(streams)
                    if len(streams_list) > 1:
                        audio_stream = streams_list[len(streams_list) // 2]
                    else:
                        audio_stream = streams_list[0]
                else:  # low
                    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').first()
                
                if not audio_stream:
                    audio_stream = yt.streams.filter(only_audio=True).first()
                
                self.status_var.set(f"Downloading audio (bitrate: {audio_stream.abr if hasattr(audio_stream, 'abr') else 'unknown'})...")
                
                output_file = audio_stream.download(output_path=location)
                
                # Convert to MP3
                self.status_var.set("Converting to MP3...")
                mp3_file = os.path.splitext(output_file)[0] + ".mp3"
                
                if self.check_ffmpeg():
                    # Use ffmpeg for better quality conversion if available
                    cmd = [
                        "ffmpeg", "-y",
                        "-i", output_file,
                        "-vn",
                        "-ar", "44100",
                        "-ac", "2",
                        "-b:a", "192k",
                        mp3_file
                    ]
                    
                    process = subprocess.run(cmd, 
                                           stdout=subprocess.PIPE, 
                                           stderr=subprocess.PIPE)
                    
                    if process.returncode != 0:
                        # If ffmpeg fails, fall back to simple rename
                        os.rename(output_file, mp3_file)
                    else:
                        # Clean up the original file
                        os.remove(output_file)
                else:
                    # Simple rename if ffmpeg is not available
                    os.rename(output_file, mp3_file)
                
                output_file = mp3_file
            
            self.progress_var.set(100)
            self.status_var.set("Download complete!")
            messagebox.showinfo("Success", f"Download completed!\nSaved to:\n{output_file}")
            
        except exceptions.RegexMatchError:
            self.status_var.set("Error: Invalid YouTube URL")
            messagebox.showerror("Error", "Invalid YouTube URL")
        
        except exceptions.VideoUnavailable:
            self.status_var.set("Error: Video unavailable")
            messagebox.showerror("Error", "This video is unavailable")
        
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        finally:
            # Re-enable UI
            self.url_entry.config(state=tk.NORMAL)
            self.location_entry.config(state=tk.NORMAL)
            self.toggle_format_specific_options()  # Reset format-specific controls

def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
