from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from bs4 import BeautifulSoup
import requests
import re

class GetVideo:
    @staticmethod
    def Id(link):
        """Extracts the video ID from a YouTube video link."""
        if "youtube.com" in link:
            pattern = r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)'
            video_id = re.search(pattern, link).group(1)
            return video_id
        elif "youtu.be" in link:
            pattern = r"youtu\.be/([a-zA-Z0-9_-]+)"
            video_id = re.search(pattern, link).group(1)
            return video_id
        else:
            return None

    @staticmethod
    def title(link):
        """Gets the title of a YouTube video."""
        r = requests.get(link) 
        s = BeautifulSoup(r.text, "html.parser") 
        try:
            title = s.find("meta", itemprop="name")["content"]
            return title
        except TypeError:
            title = "⚠️ There seems to be an issue with the YouTube video link provided. Please check the link and try again."
            return title
        
    @staticmethod
    def transcript(link):
        """Gets the transcript of a YouTube video in any available language."""
        video_id = GetVideo.Id(link)
        if not video_id:
            return "Error: Invalid YouTube URL"
            
        # Define language priority
        languages = ['en', 'hi', 'es', 'fr', 'de', 'ja', 'ko', 'zh-CN', 'zh-TW', 'ar', 'pt', 'ru', 'it', 'nl', 'pl', 'tr', 'id', 'vi', 'th', 'ta', 'te', 'ml', 'kn', 'bn', 'pa']
        
        try:
            api = YouTubeTranscriptApi()
            
            # Method 1: Try to fetch transcript directly with language preferences
            for lang in languages:
                try:
                    transcript_data = api.fetch(video_id, [lang])
                    final_transcript = " ".join(snippet.text for snippet in transcript_data)
                    print(f"✓ Fetched transcript successfully in language: {lang}")
                    return final_transcript
                except NoTranscriptFound:
                    continue
                except Exception as e:
                    if "Too Many Requests" in str(e):
                        return "Error: YouTube rate limit reached. Please wait 10-15 minutes and try again."
                    continue
            
            # Method 2: Try to list and get any available transcript
            try:
                transcript_list_obj = api.list(video_id)
                
                # Try to get any manually created transcript first
                for transcript in transcript_list_obj:
                    if not transcript.is_generated:
                        try:
                            transcript_data = transcript.fetch()
                            final_transcript = " ".join(snippet.text for snippet in transcript_data)
                            print(f"✓ Using manual transcript: {transcript.language_code}")
                            return final_transcript
                        except Exception as e2:
                            print(f"Failed manual transcript {transcript.language_code}: {str(e2)}")
                            continue
                
                # Try auto-generated transcripts with translation
                for transcript in transcript_list_obj:
                    try:
                        # If it's translatable and not English, translate it
                        if hasattr(transcript, 'is_translatable') and transcript.is_translatable and transcript.language_code not in ['en', 'en-US', 'en-GB']:
                            try:
                                transcript = transcript.translate('en')
                                print(f"✓ Translated {transcript.language_code} to English")
                            except:
                                pass
                        
                        transcript_data = transcript.fetch()
                        final_transcript = " ".join(snippet.text for snippet in transcript_data)
                        print(f"✓ Using auto-generated transcript: {transcript.language_code}")
                        return final_transcript
                    except Exception as e3:
                        print(f"Failed auto-generated {transcript.language_code}: {str(e3)}")
                        continue
                
                return "Error: No transcripts/captions are available for this video."
                
            except TranscriptsDisabled:
                return "Error: Transcripts/subtitles are disabled for this video."
            except Exception as list_error:
                print(f"Method 2 failed: {str(list_error)}")
                return "Error: No transcripts/captions are available for this video."
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error fetching transcript: {error_msg}")
            
            # Check for specific error types
            if "Too Many Requests" in error_msg or "blocking requests" in error_msg:
                return "Error: YouTube rate limit reached. Please wait 10-15 minutes and try again."
            elif "Subtitles are disabled" in error_msg or "disabled for this video" in error_msg or "TranscriptsDisabled" in error_msg:
                return "Error: Transcripts/subtitles are disabled for this video."
            elif "Video unavailable" in error_msg or "unavailable" in error_msg:
                return "Error: Video is unavailable or private."
            else:
                return f"Error: Could not fetch transcript. {error_msg}"

    @staticmethod
    def transcript_time(link):
        """Gets the transcript of a YouTube video with timestamps in any available language."""
        video_id = GetVideo.Id(link)
        if not video_id:
            return "Error: Invalid YouTube URL"
            
        languages = ['en', 'hi', 'es', 'fr', 'de', 'ja', 'ko', 'zh-CN', 'zh-TW', 'ar', 'pt', 'ru', 'it', 'nl', 'pl', 'tr', 'id', 'vi', 'th', 'ta', 'te', 'ml', 'kn', 'bn', 'pa']
        
        try:
            api = YouTubeTranscriptApi()
            
            # Method 1: Try direct fetch with language preferences
            for lang in languages:
                try:
                    transcript_data = api.fetch(video_id, [lang])
                    final_transcript = ""
                    for snippet in transcript_data:
                        timevar = round(float(snippet.start))
                        hours = int(timevar // 3600)
                        timevar %= 3600
                        minutes = int(timevar // 60)
                        timevar %= 60
                        timevex = f"{hours:02d}:{minutes:02d}:{timevar:02d}"
                        final_transcript += f'{snippet.text} "time:{timevex}" '
                    print(f"✓ Fetched timestamped transcript in {lang}")
                    return final_transcript
                except NoTranscriptFound:
                    continue
                except Exception as e:
                    if "Too Many Requests" in str(e):
                        return "Error: YouTube rate limit reached. Please wait 10-15 minutes and try again."
                    continue
            
            # Method 2: List and try each available transcript
            try:
                transcript_list_obj = api.list(video_id)
                
                # Try manual transcripts first
                for transcript in transcript_list_obj:
                    if hasattr(transcript, 'is_generated') and not transcript.is_generated:
                        try:
                            transcript_data = transcript.fetch()
                            final_transcript = ""
                            for snippet in transcript_data:
                                timevar = round(float(snippet.start))
                                hours = int(timevar // 3600)
                                timevar %= 3600
                                minutes = int(timevar // 60)
                                timevar %= 60
                                timevex = f"{hours:02d}:{minutes:02d}:{timevar:02d}"
                                final_transcript += f'{snippet.text} "time:{timevex}" '
                            return final_transcript
                        except:
                            continue
                
                # Try auto-generated with translation
                for transcript in transcript_list_obj:
                    try:
                        if hasattr(transcript, 'is_translatable') and transcript.is_translatable and transcript.language_code not in ['en', 'en-US', 'en-GB']:
                            try:
                                transcript = transcript.translate('en')
                            except:
                                pass
                        
                        transcript_data = transcript.fetch()
                        final_transcript = ""
                        for snippet in transcript_data:
                            timevar = round(float(snippet.start))
                            hours = int(timevar // 3600)
                            timevar %= 3600
                            minutes = int(timevar // 60)
                            timevar %= 60
                            timevex = f"{hours:02d}:{minutes:02d}:{timevar:02d}"
                            final_transcript += f'{snippet.text} "time:{timevex}" '
                        return final_transcript
                    except:
                        continue
                
                return "Error: No transcripts/captions are available for this video."
            except TranscriptsDisabled:
                return "Error: Transcripts/subtitles are disabled for this video."
            except:
                return "Error: No transcripts/captions are available for this video."
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error fetching transcript with time: {error_msg}")
            
            if "Too Many Requests" in error_msg or "blocking requests" in error_msg:
                return "Error: YouTube rate limited. Please wait 10-15 minutes and try again."
            elif "Subtitles are disabled" in error_msg or "disabled for this video" in error_msg or "TranscriptsDisabled" in error_msg:
                return "Error: Transcripts/subtitles are disabled for this video."
            elif "Video unavailable" in error_msg or "unavailable" in error_msg:
                return "Error: Video is unavailable or private."
            else:
                return f"Error: Could not fetch transcript. {error_msg}"

