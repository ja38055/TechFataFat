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
        """Enhanced video creation with better visuals"""
        try:
            # Get tech stock image (placeholder - replace with real API)
            response = requests.get(f"https://source.unsplash.com/1080x1920/?technology,{topic.split()[0]}")
            img = Image.open(BytesIO(response.content))
            
            # Add overlay
            overlay = Image.new('RGBA', img.size, (0,0,0,128))
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
            
            # Add text
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 80)
            text = f"Tech Update:\n{topic}"
            draw.text((540, 800), text, font=font, fill=(255,255,255), anchor="mm")
            
            # Save image
            img.save("background.png")
            
            # Generate voiceover
            tts = gTTS(f"Hello Tech Fatafat viewers! Today's tech update: {topic}", lang='en', tld='co.in')
            tts.save("voiceover.mp3")
            
            # Create video (requires ffmpeg)
            os.system('ffmpeg -loop 1 -i background.png -i voiceover.mp3 -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest short.mp4')
            return "short.mp4"
        except Exception as e:
            print(f"Error creating video: {e}")
            return None
    
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
