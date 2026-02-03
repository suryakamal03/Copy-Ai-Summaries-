from src.video_info import GetVideo

# Test with the snooker video
url = "https://youtu.be/z89eJUwuwII?si=JEMjZY6orQ4OgYyq"

print("Testing transcript extraction...")
print("=" * 60)

video_id = GetVideo.Id(url)
print(f"Video ID: {video_id}")

transcript = GetVideo.transcript(url)
print(f"\nTranscript type: {type(transcript)}")
print(f"Transcript length: {len(transcript) if transcript else 0}")
print(f"\nFirst 500 characters:")
print(transcript[:500] if transcript else "None/Empty")
