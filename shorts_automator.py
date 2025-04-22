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

class HinglishShortsCreator:
    def __init__(self, topic=None):
        self.topic = topic or self.get_trending_topic()
        self.font_path = "NotoSansDevanagari-Regular.ttf"  # Hindi font
        self.voice_settings = {
            'lang': 'hi' if np.random.random() > 0.5 else 'en',
            'slow': False
        }
        
    def get_trending_topic(self):
        """Get Hinglish tech topics"""
        hinglish_topics = [
            "5G ki speed", "AI ka future", "Smartphone ki latest features",
            "Bitcoin ka bhav", "WhatsApp new updates", "Laptop buying tips"
        ]
        return np.random.choice(hinglish_topics)
    
    def generate_hinglish_script(self):
        """Generate Hinglish script"""
        templates = [
            ("Tech lovers suno! Aaj ki top story {topic} ke bare mein. "
             "Ye technology hamare life ko kar rahi hai bahut easy. "
             "Full details ke liye like karo aur subscribe karo {channel} ko!"),
            
            ("Kya aapko pata hai? {topic} mein hai amazing innovations. "
             "Iske advantages aur disadvantages janane ke liye, "
             "comment section mein poocho humse!"),
            
            ("Breaking tech news! {topic} ne badal diya game. "
             "Janiye iske sabhi features hamare saath. {channel} ke saath raho updated!")
        ]
        return np.random.choice(templates).format(
            topic=self.topic,
            channel=os.environ.get('CHANNEL_NAME', 'TechFatafat')
        )

    def create_hinglish_audio(self, script):
        """Generate Hinglish TTS with code-switching"""
        try:
            # Split into Hindi and English parts
            parts = []
            current_lang = 'en'
            for word in script.split():
                if any(c.isalpha() and ord(c) > 128 for c in word):
                    if current_lang != 'hi':
                        parts.append(('hi', []))
                        current_lang = 'hi'
                    parts[-1][1].append(word)
                else:
                    if current_lang != 'en':
                        parts.append(('en', []))
                        current_lang = 'en'
                    parts[-1][1].append(word)
            
            # Generate audio clips
            clips = []
            for lang, words in parts:
                text = ' '.join(words)
                with tempfile.NamedTemporaryFile(suffix=".mp3") as fp:
                    tts = gTTS(text, lang=lang)
                    tts.save(fp.name)
                    clips.append(AudioFileClip(fp.name))
            
            # Combine audio
            final_audio = concatenate_audioclips(clips)
            audio_path = os.path.join(tempfile.gettempdir(), "audio.mp3")
            final_audio.write_audiofile(audio_path)
            return audio_path
            
        except Exception as e:
            print(f"Audio error: {e}")
            return None

    def create_hinglish_visuals(self):
        """Create Hinglish text overlay"""
        try:
            # Background image with Indian tech theme
            response = requests.get("https://source.unsplash.com/1080x1920/?india,technology")
            img = Image.open(BytesIO(response.content))
            
            # Add gradient overlay
            overlay = Image.new('RGBA', img.size, (0,0,0,100))
            draw = ImageDraw.Draw(overlay)
            
            # Hinglish text
            font = ImageFont.truetype(self.font_path, 60)
            draw.text((50, 100), "Tech Samachar", fill=(255, 165, 0), font=font)  # Orange text
            draw.text((50, 200), self.topic, fill=(255,255,255), font=font)
            
            # English subheading
            en_font = ImageFont.truetype("arial.ttf", 40)
            draw.text((50, 300), "Latest Technology Updates", fill=(173,216,230), font=en_font)
            
            final_img = Image.alpha_composite(img.convert('RGBA'), overlay)
            img_path = os.path.join(tempfile.gettempdir(), "bg.png")
            final_img.save(img_path)
            return img_path
            
        except Exception as e:
            print(f"Visual error: {e}")
            return None

    def create_video(self):
        """Create Hinglish short"""
        script = self.generate_hinglish_script()
        audio_path = self.create_hinglish_audio(script)
        bg_path = self.create_hinglish_visuals()
        
        if not audio_path or not bg_path:
            return None
            
        try:
            audio = AudioFileClip(audio_path)
            duration = min(max(audio.duration, 30), 60)
            
            video = (ImageClip(bg_path)
                    .set_duration(duration)
                    .set_audio(audio)
                    .fx(vfx.colorx, 0.9)
                    .fx(vfx.lum_contrast, 0.8))
            
            # Add subtle background music
            bgm = AudioFileClip("indian_bgm.mp3").volumex(0.1).subclip(0, duration)
            final_audio = CompositeAudioClip([audio, bgm])
            video = video.set_audio(final_audio)
            
            output_path = os.path.join(tempfile.gettempdir(), "short.mp4")
            video.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                preset="ultrafast",
                audio_codec="aac",
                threads=4
            )
            return output_path
            
        finally:
            for f in [audio_path, bg_path]:
                if os.path.exists(f):
                    os.remove(f)

    
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
    if __name__ == "__main__":
    creator = HinglishShortsCreator()
    video_path = creator.create_video()
    if video_path:
        creator.upload_video(video_path)
