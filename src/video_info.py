from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from bs4 import BeautifulSoup
import requests
import re
from yt_dlp import YoutubeDL
import json

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

class GetVideo:
    @staticmethod
    def _safe_video_id(link):
        link = (link or "").strip()
        if "youtube.com" in link:
            pattern = r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)'
            match = re.search(pattern, link)
            return match.group(1) if match else None
        if "youtu.be" in link:
            pattern = r"youtu\.be/([a-zA-Z0-9_-]+)"
            match = re.search(pattern, link)
            return match.group(1) if match else None
        return None

    @staticmethod
    def _seconds_to_hhmmss(total_seconds):
        hh = total_seconds // 3600
        mm = (total_seconds % 3600) // 60
        ss = total_seconds % 60
        return f"{hh:02d}:{mm:02d}:{ss:02d}"

    @staticmethod
    def _parse_caption_payload(text, include_timestamps=False):
        """Parse subtitle payloads that may be json3, VTT, or SRT into clean transcript text."""
        raw = (text or "").strip()
        if not raw:
            return ""

        # json3 format from YouTube captions API
        if raw.startswith("{") and '"events"' in raw:
            try:
                payload = json.loads(raw)
                events = payload.get("events", [])
                chunks = []
                for event in events:
                    segs = event.get("segs")
                    if not segs:
                        continue
                    content = "".join(seg.get("utf8", "") for seg in segs)
                    cleaned = re.sub(r"\s+", " ", content).strip()
                    if not cleaned or cleaned == "\\n":
                        continue
                    if include_timestamps:
                        start_ms = int(event.get("tStartMs", 0))
                        chunks.append(f'{cleaned} "time:{GetVideo._seconds_to_hhmmss(start_ms // 1000)}" ')
                    else:
                        chunks.append(cleaned)
                return " ".join(chunks).strip()
            except Exception:
                pass

        # VTT/SRT fallback parser
        lines = [ln.strip() for ln in raw.replace("\r", "").splitlines() if ln.strip()]
        chunks = []
        current_time = None
        for ln in lines:
            if ln.startswith(("WEBVTT", "Kind:", "Language:")):
                continue
            if "-->" in ln:
                start = ln.split("-->")[0].strip().split(" ")[0]
                parts = start.replace(",", ".").split(":")
                if len(parts) == 3:
                    h, m, s = parts
                elif len(parts) == 2:
                    h = "0"
                    m, s = parts
                else:
                    h, m, s = "0", "0", "0"
                current_time = int(float(h) * 3600 + float(m) * 60 + float(s))
                continue
            if ln.isdigit():
                continue
            cleaned = re.sub(r"<[^>]+>", "", ln).strip()
            if not cleaned:
                continue
            if include_timestamps and current_time is not None:
                chunks.append(f'{cleaned} "time:{GetVideo._seconds_to_hhmmss(current_time)}" ')
            else:
                chunks.append(cleaned)
        return " ".join(chunks).strip()

    @staticmethod
    def _fetch_with_ytdlp(link, include_timestamps=False):
        link = (link or "").strip()
        try:
            # Android client often works even when web client receives 429 bot checks.
            ydl_opts = {
                "quiet": True,
                "skip_download": True,
                "nocheckcertificate": True,
                "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
                "http_headers": BROWSER_HEADERS,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)

            subtitle_sources = [info.get("subtitles") or {}, info.get("automatic_captions") or {}]
            language_priority = ["en", "en-US", "en-GB", "hi", "es", "fr", "de", "ja", "ko", "zh", "ar", "pt", "ru"]

            for source in subtitle_sources:
                for language in language_priority:
                    tracks = source.get(language)
                    if not tracks and language == "en":
                        tracks = source.get("en-US") or source.get("en-GB")
                    if not tracks:
                        continue

                    for track in tracks:
                        url = track.get("url")
                        if not url:
                            continue
                        try:
                            resp = requests.get(url, headers=BROWSER_HEADERS, timeout=20)
                            resp.raise_for_status()
                            final_text = GetVideo._parse_caption_payload(resp.text, include_timestamps=include_timestamps)
                            if final_text:
                                return final_text
                        except Exception:
                            continue
            return None
        except Exception as e:
            print(f"yt-dlp fallback failed: {e}")
            return None

    @staticmethod
    def Id(link):
        """Extracts the video ID from a YouTube video link."""
        return GetVideo._safe_video_id(link)

    @staticmethod
    def title(link):
        """Gets the title of a YouTube video."""
        link = (link or "").strip()
        try:
            r = requests.get(link, headers=BROWSER_HEADERS, timeout=12)
            r.raise_for_status()
            s = BeautifulSoup(r.text, "html.parser")

            # Try multiple metadata selectors used by YouTube pages.
            for selector in [
                ("meta", {"property": "og:title"}),
                ("meta", {"name": "title"}),
                ("meta", {"itemprop": "name"}),
            ]:
                tag = s.find(selector[0], selector[1])
                if tag and tag.get("content"):
                    content = tag.get("content").strip()
                    if content:
                        return content

            page_title = (s.title.string.strip() if s.title and s.title.string else "")
            if page_title:
                return page_title.replace(" - YouTube", "").strip()
        except Exception:
            pass

        # Fallback to yt-dlp metadata when the watch page is partially blocked.
        try:
            ydl_opts = {
                "quiet": True,
                "skip_download": True,
                "nocheckcertificate": True,
                "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
                "http_headers": BROWSER_HEADERS,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
            title = (info.get("title") or "").strip()
            if title:
                return title
        except Exception:
            pass

        return "YouTube Video"
        
    @staticmethod
    def transcript(link):
        """Gets the transcript of a YouTube video in any available language."""
        link = (link or "").strip()
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
                ytdlp_fallback = GetVideo._fetch_with_ytdlp(link, include_timestamps=False)
                if ytdlp_fallback:
                    print("✓ Using yt-dlp fallback transcript")
                    return ytdlp_fallback
                return "Error: No transcripts/captions are available for this video."
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error fetching transcript: {error_msg}")
            ytdlp_fallback = GetVideo._fetch_with_ytdlp(link, include_timestamps=False)
            if ytdlp_fallback:
                print("✓ Using yt-dlp fallback transcript")
                return ytdlp_fallback
            
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
        link = (link or "").strip()
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
                ytdlp_fallback = GetVideo._fetch_with_ytdlp(link, include_timestamps=True)
                if ytdlp_fallback:
                    return ytdlp_fallback
                return "Error: No transcripts/captions are available for this video."
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error fetching transcript with time: {error_msg}")
            ytdlp_fallback = GetVideo._fetch_with_ytdlp(link, include_timestamps=True)
            if ytdlp_fallback:
                return ytdlp_fallback
            
            if "Too Many Requests" in error_msg or "blocking requests" in error_msg:
                return "Error: YouTube rate limited. Please wait 10-15 minutes and try again."
            elif "Subtitles are disabled" in error_msg or "disabled for this video" in error_msg or "TranscriptsDisabled" in error_msg:
                return "Error: Transcripts/subtitles are disabled for this video."
            elif "Video unavailable" in error_msg or "unavailable" in error_msg:
                return "Error: Video is unavailable or private."
            else:
                return f"Error: Could not fetch transcript. {error_msg}"

