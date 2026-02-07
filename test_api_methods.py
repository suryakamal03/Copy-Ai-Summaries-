from youtube_transcript_api import YouTubeTranscriptApi
import inspect

print("YouTubeTranscriptApi class methods:")
print("=" * 50)
for name, method in inspect.getmembers(YouTubeTranscriptApi, predicate=inspect.ismethod):
    print(f" - {name}")

print("\nYouTubeTranscriptApi class attributes:")
print("=" * 50)
for name in dir(YouTubeTranscriptApi):
    if not name.startswith('_'):
        print(f" - {name}")

# Try to use it correctly
video_id = "_HRA37X8N_Q"
print(f"\n\nTrying to fetch transcript for video: {video_id}")
print("=" * 50)

try:
    # Try method 1
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print(f"SUCCESS with get_transcript!")
    print(f"Transcript length: {len(transcript)}")
except Exception as e:
    print(f"get_transcript failed: {e}")

try:
    # Try method 2
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    print(f"SUCCESS with list_transcripts!")
    for t in transcript_list:
        print(f" - {t.language_code}: generated={t.is_generated}, translatable={t.is_translatable}")
except Exception as e:
    print(f"list_transcripts failed: {e}")
