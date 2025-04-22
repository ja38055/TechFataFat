import os
import json
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload  # ADD THIS IMPORT
from google.auth.transport.requests import Request
from pytrends.request import TrendReq
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import requests
from io import BytesIO

class YouTubeShortsAutomator:
    def __init__(self):
        creds_dict = json.loads(os.environ['YOUTUBE_CREDENTIALS'])
        self.credentials = Credentials(
            token=creds_dict.get('token'),
            refresh_token=creds_dict.get('refresh_token'),
            token_uri=creds_dict.get('token_uri'),
            client_id=creds_dict.get('client_id'),
            client_secret=creds_dict.get('client_secret'),
            scopes=creds_dict.get('scopes')
        )
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        
        self.channel_name = os.environ.get('CHANNEL_NAME', 'TechFatafat')
        self.pytrends = TrendReq(hl='en-US', tz=360)

    def get_trending_topic(self):
        try:
            df = self.pytrends.trending_searches(pn='india')
            print(df)
            return df[0][0] if not df.empty else "Tech News Update"
        except:
            return "Latest Tech Updates"

    def create_short_video(self, topic):
        try:
            # 1. Create background image
            img = Image.new('RGB', (1080, 1920), color=(30, 30, 60))
            draw = ImageDraw.Draw(img)
            
            # 2. Add text
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 80)  # Using default font
            text = f"Tech Short:\n{topic}"
            draw.text((540, 960), text, font=font, fill=(255, 255, 255), anchor="mm")
            
            # 3. Save image to file
            img_path = "background.png"
            img.save(img_path)
            
            # 4. Generate voiceover
            tts = gTTS(f"Hello {self.channel_name} viewers! Today's topic is {topic}", lang='en', tld='co.in')
            tts.save("voiceover.mp3")
            
            # 5. Combine into video (using ffmpeg)
            os.system('ffmpeg -loop 1 -i background.png -i voiceover.mp3 -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest short.mp4')
            
            return "short.mp4"
        except Exception as e:
            print(f"Error creating video: {e}")
            return None

    def upload_to_youtube(self, video_path, topic):
        try:
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
            return True
        except Exception as e:
            print(f"Error uploading video: {e}")
            return False

if __name__ == "__main__":
    automator = YouTubeShortsAutomator()
    topic = automator.get_trending_topic()
    print(f"Today's topic: {topic}")
    
    video_path = 0 # automator.create_short_video(topic)
    if video_path and False:
        print("Video created successfully!")
        if automator.upload_to_youtube(video_path, topic):
            print("Upload successful!")
        else:
            print("Upload failed")
    else:
        print("Failed to create video")
