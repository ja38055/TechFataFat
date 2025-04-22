import os
import json
import datetime
from pytrends.request import TrendReq
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from gtts import gTTS
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

class YouTubeShortsAutomator:
    def __init__(self):
        # Load credentials from environment variables
        creds_info = json.loads(os.environ['YOUTUBE_CREDENTIALS'])
        self.credentials = Credentials.from_authorized_user_info(creds_info, [
            'https://www.googleapis.com/auth/youtube.upload'
        ])
        self.channel_name = os.environ.get('CHANNEL_NAME', 'TechFatafat')
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
    def get_trending_topic(self):
        """Get trending tech topic using Google Trends"""
        try:
            df = self.pytrends.trending_searches(pn='india')
            return df[0][0] if not df.empty else "Tech News Update"
        except:
            return "Latest Tech Updates"
    
    def create_short_video(self, topic):
        """Create faceless short video with AI voice"""
        # Generate AI voiceover
        tts = gTTS(f"Hello {self.channel_name} viewers! Today's topic is {topic}", lang='en', tld='co.in')
        voiceover = BytesIO()
        tts.write_to_fp(voiceover)
        voiceover.seek(0)
        
        # Create video frame
        img = Image.new('RGB', (1080, 1920), color=(30, 30, 60))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 80)
        
        # Add text
        text = f"Tech Short:\n{topic}"
        draw.text((540, 960), text, font=font, fill=(255, 255, 255), anchor="mm")
        
        # Save as video
        video_path = "short.mp4"
        os.system(f"ffmpeg -loop 1 -i image.png -i audio.mp3 -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest {video_path}")
        return video_path
    
    def upload_to_youtube(self, video_path, topic):
        """Upload video to YouTube"""
        youtube = build('youtube', 'v3', credentials=self.credentials)
        
        request_body = {
            'snippet': {
                'title': f"{topic} #Shorts",
                'description': f"Auto-generated tech short for {self.channel_name}",
                'categoryId': '28'
            },
            'status': {
                'privacyStatus': 'public'
            }
        }
        
        media = MediaFileUpload(video_path)
        youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media
        ).execute()

if __name__ == "__main__":
    automator = YouTubeShortsAutomator()
    topic = automator.get_trending_topic()
    video_path = automator.create_short_video(topic)
    automator.upload_to_youtube(video_path, topic)
