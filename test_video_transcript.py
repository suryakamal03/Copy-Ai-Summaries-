from src.video_info import GetVideo

# Test the specific video
url = "https://youtu.be/_HRA37X8N_Q?si=x2Fojn7CAqSw-0v-"

print(f"Testing URL: {url}")
print("=" * 50)

# Get video ID
video_id = GetVideo.Id(url)
print(f"Video ID: {video_id}")

# Try to get transcript
print("\nFetching transcript...")
transcript = GetVideo.transcript(url)

print("\n" + "=" * 50)
print("Result:")
print("=" * 50)
print(transcript[:500] if len(transcript) > 500 else transcript)
print(f"\nLength: {len(transcript)} characters")
print(f"Starts with 'Error:': {transcript.startswith('Error:')}")
