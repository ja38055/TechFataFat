import os
import json
import requests
import tempfile
import numpy as np
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from gtts import gTTS
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class GitHubShortsCreator:
    def __init__(self, topic=None):
        self.topic = topic or self.get_trending_topic()
        self.voice_settings = {
            'lang': 'en',
            'tld': 'com',  # American English (male voice)
            'slow': False
        }
        
    def get_trending_topic(self):
        """Get tech trends from Google Trends"""
        try:
            pytrends = TrendReq()
            df = pytrends.trending_searches(pn='IN')  # India
            return df[0][0] if not df.empty else "Latest Tech News"
        except:
            tech_terms = ["AI Development", "5G Technology", "Quantum Computing"]
            return np.random.choice(tech_terms)
    
    def generate_assets(self):
        """Create all video components"""
        # 1. Generate script
        script = (f"Tech enthusiasts! Breaking news about {self.topic}. "
                 "Stay tuned to TechFatafat for daily tech updates!")
        
        # 2. Create voiceover
        tts = gTTS(script, **self.voice_settings)
        voice_path = os.path.join(tempfile.gettempdir(), "voiceover.mp3")
        tts.save(voice_path)
        
        # 3. Generate visuals
        try:
            # Use Unsplash API if available
            access_key = os.getenv('UNSPLASH_ACCESS_KEY', '')
            if access_key:
                url = f"https://api.unsplash.com/photos/random?query={self.topic}-technology&client_id={access_key}"
                response = requests.get(url)
                img_url = response.json()['urls']['regular']
            else:
                img_url = f"https://source.unsplash.com/1080x1920/?{self.topic.replace(' ','-')}-technology"
            
            img = Image.open(BytesIO(requests.get(img_url).content))
        except:
            # Fallback to tech pattern
            img = Image.new('RGB', (1080, 1920), (10, 20, 30))
            draw = ImageDraw.Draw(img)
            # Add circuit pattern
            for i in range(0, 1080, 50):
                draw.line([(i, 0), (i, 1920)], fill=(0, 100, 200), width=1)
        
        # Add text overlay
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 80)
        draw.text((100, 100), "Tech Update", fill=(0, 200, 255), font=font)
        draw.text((100, 200), self.topic, fill=(255, 255, 255), font=font)
        
        bg_path = os.path.join(tempfile.gettempdir(), "background.jpg")
        img.save(bg_path)
        
        return voice_path, bg_path

    def create_video(self):
        """Build video file"""
        voice_path, bg_path = self.generate_assets()
        
        audio = AudioFileClip(voice_path)
        duration = min(max(audio.duration, 30), 60)  # 30-60 seconds
        
        video = (ImageClip(bg_path)
                .set_duration(duration)
                .set_audio(audio)
                .fx(vfx.colorx, 0.9)
                .fx(vfx.lum_contrast, 0.8))
        
        output_path = os.path.join(tempfile.gettempdir(), "output.mp4")
        video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            preset="ultrafast",
            threads=4,
            audio_codec="aac"
        )
        return output_path

    def upload_video(self, video_path):
        """YouTube upload handler"""
        creds = Credentials.from_authorized_user_info(
            json.loads(os.environ['YOUTUBE_CREDENTIALS'])
        )
        
        youtube = build('youtube', 'v3', credentials=creds)
        media = MediaFileUpload(video_path)
        
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": f"{self.topic} #Shorts",
                    "description": f"Daily tech short from TechFatafat about {self.topic}",
                    "categoryId": "28",
                    "tags": ["tech", "shorts", "technology"]
                },
                "status": {
                    "privacyStatus": "public"
                }
            },
            media_body=media
        )
        return request.execute()

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else None
    
    creator = GitHubShortsCreator(topic)
    video_path = creator.create_video()
    
    if video_path and os.path.exists(video_path):
        result = creator.upload_video(video_path)
        print(f"Uploaded video ID: {result['id']}")
        os.remove(video_path)
    else:
        print("Video creation failed")
        exit(1)
