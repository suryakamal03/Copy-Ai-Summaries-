import requests
import json

# Test URL - short snooker video
test_url = "https://www.youtube.com/watch?v=F6W13QMQsag"

print("Testing backend API...")
print("=" * 50)

# Test 1: Video Info
print("\n1. Testing /api/video-info")
try:
    response = requests.post(
        'http://localhost:5000/api/video-info',
        json={'url': test_url},
        headers={'Content-Type': 'application/json'}
    )
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"✓ Video ID: {data.get('videoId')}")
        print(f"✓ Title: {data.get('title')}")
    else:
        print(f"✗ Error: {response.text}")
except Exception as e:
    print(f"✗ Connection error: {e}")

# Test 2: Summary
print("\n2. Testing /api/summary")
try:
    response = requests.post(
        'http://localhost:5000/api/summary',
        json={'url': test_url, 'summaryType': 'detailed'},
        headers={'Content-Type': 'application/json'},
        timeout=60
    )
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        summary = data.get('summary', '')
        print(f"✓ Summary generated ({len(summary)} chars)")
        print(f"Preview: {summary[:200]}...")
    else:
        print(f"✗ Error: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Transcript
print("\n3. Testing /api/transcript")
try:
    response = requests.post(
        'http://localhost:5000/api/transcript',
        json={'url': test_url},
        headers={'Content-Type': 'application/json'}
    )
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        transcript = data.get('transcript', '')
        print(f"✓ Transcript fetched ({len(transcript)} chars)")
    else:
        print(f"✗ Error: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 50)
print("Test complete!")
