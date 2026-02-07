# YouTube Rate Limit - Quick Fix Guide

## Problem
You're seeing: **"Could not fetch transcript"** or **"YouTube is blocking requests from your IP"**

This happens when you make too many requests to YouTube's transcript API in a short time.

## Quick Solutions

### Solution 1: Wait (Easiest)
⏱️ **Wait 10-15 minutes**, then try again  
YouTube's rate limit is temporary and will reset automatically.

### Solution 2: Try a Different Video
Some videos have better accessibility. Try these test videos:
- `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- Any video with subtitles/captions enabled
- Shorter videos (under 10 minutes) work better

### Solution 3: Restart Your Network
🔄 **Get a new IP address:**
1. Restart your router/modem
2. Wait 2-3 minutes
3. Try again

### Solution 4: Use a VPN (If Available)
🌐 Connect to a VPN to change your IP address

### Solution 5: Reduce Request Frequency
⚡ **Best practices:**
- Don't click "Generate Summary" multiple times rapidly
- Wait 2-3 seconds between video loads
- Process one video at a time

## For Developers: Advanced Solutions

### Option A: Add Cookies Support
Install browser cookies to authenticate requests:

```python
# Install additional package
pip install browser-cookie3

# Update video_info.py
from youtube_transcript_api import YouTubeTranscriptApi
import browser_cookie3

def transcript(link):
    video_id = GetVideo.Id(link)
    try:
        # Use cookies from your browser
        cookies = browser_cookie3.chrome()  # or .firefox(), .edge()
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id, cookies=cookies)
        return " ".join(snippet.text for snippet in transcript_list)
    except Exception as e:
        return f"Error: {str(e)}"
```

### Option B: Use Proxies
Route requests through rotating proxies:

```python
# Update requirements.txt
requests[socks]

# Update video_info.py
proxies = {
    'http': 'socks5://127.0.0.1:9050',
    'https': 'socks5://127.0.0.1:9050'
}

transcript_list = api.fetch(video_id, proxies=proxies)
```

### Option C: Implement Retry Logic
Add exponential backoff:

```python
import time
from functools import wraps

def retry_on_rate_limit(max_retries=3, delay=5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "blocking requests" in str(e) and attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        print(f"Rate limited. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        raise
            return None
        return wrapper
    return decorator

@retry_on_rate_limit(max_retries=3, delay=10)
def transcript(link):
    # existing code
```

## Why This Happens

YouTube's transcript API has rate limits to prevent abuse:
- **~50-100 requests per hour** from a single IP
- **Stricter limits** for cloud IPs (AWS, Google Cloud, Azure)
- **Temporary bans** lasting 10-60 minutes

## Prevention Tips

✅ **Do:**
- Cache transcripts locally
- Implement rate limiting in your app
- Use one video for testing
- Clear browser cache occasionally

❌ **Don't:**
- Spam requests
- Run from cloud servers without proxies
- Load multiple videos quickly
- Refresh the page repeatedly

## Testing Without Rate Limits

Use these sample transcripts for testing:

```python
# test_transcript.py
SAMPLE_TRANSCRIPT = """
Welcome to this tutorial on Python programming.
In this video, we'll cover the basics of variables,
data types, and control flow. Let's get started!
"""

def get_test_transcript():
    return SAMPLE_TRANSCRIPT
```

Then in your code, add a test mode:

```python
# Set to True for testing
TEST_MODE = True

if TEST_MODE:
    transcript = get_test_transcript()
else:
    transcript = GetVideo.transcript(url)
```

## Additional Resources

- [YouTube Transcript API Docs](https://github.com/jdepoix/youtube-transcript-api)
- [Working Around IP Bans](https://github.com/jdepoix/youtube-transcript-api#working-around-ip-bans-requestblocked-or-ipblocked-exception)
- [Rate Limiting Best Practices](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)

## Quick Check

Before reporting an issue, verify:
1. ✅ Waited at least 15 minutes
2. ✅ Video has captions/subtitles enabled
3. ✅ Not using a cloud/VPN IP that's blocked
4. ✅ Tried a different video
5. ✅ Backend server is running

If all checks pass and you still have issues, it might be a YouTube API change.
