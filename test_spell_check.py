"""Test transcript spell-checking with Gemini"""
from src.rag_chat import RAGChat
from src.video_info import GetVideo

# Example test cases showing common transcription errors
test_transcripts = [
    # Test 1: Technical tool names
    """In this video we'll cover how to use end mapap for network scanning. 
    We'll also discuss cubeectl for Kubernetes management and darker containers.""",
    
    # Test 2: Programming terms
    """Today we're learning pie thon programming. We'll use the Jango framework 
    and no JS for the backend. We'll also discuss react jay ess.""",
    
    # Test 3: Mixed technical content
    """First, install gay it on your system. Then use NPM to install dependencies. 
    Finally, run the post gray SQL database."""
]

def test_simple_correction():
    """Test the spell correction on sample texts"""
    print("=" * 60)
    print("TESTING SPELL CHECK CORRECTION")
    print("=" * 60)
    
    rag = RAGChat()
    
    for i, test_text in enumerate(test_transcripts, 1):
        print(f"\n📝 Test {i}:")
        print(f"Original: {test_text[:100]}...")
        
        corrected = rag.correct_transcript(test_text)
        print(f"\n✅ Corrected: {corrected[:100]}...")
        print("-" * 60)

def test_real_video():
    """Test with a real YouTube video"""
    print("\n" + "=" * 60)
    print("TESTING WITH REAL YOUTUBE VIDEO")
    print("=" * 60)
    
    # Replace with your test video URL
    url = input("\nEnter YouTube URL (or press Enter to skip): ").strip()
    
    if not url:
        print("Skipping real video test")
        return
    
    print("\nFetching transcript...")
    transcript = GetVideo.transcript(url)
    
    if transcript.startswith("Error:"):
        print(f"❌ {transcript}")
        return
    
    print(f"\n📄 Original transcript (first 300 chars):")
    print(transcript[:300])
    
    print("\n🔍 Correcting with Gemini...")
    rag = RAGChat()
    corrected = rag.correct_transcript(transcript)
    
    print(f"\n✅ Corrected transcript (first 300 chars):")
    print(corrected[:300])
    
    # Show differences
    print("\n📊 Comparison:")
    print(f"Original length: {len(transcript)}")
    print(f"Corrected length: {len(corrected)}")
    print(f"Length ratio: {len(corrected)/len(transcript):.2%}")

def test_ingestion_with_correction():
    """Test full ingestion pipeline with correction enabled"""
    print("\n" + "=" * 60)
    print("TESTING FULL INGESTION WITH CORRECTION")
    print("=" * 60)
    
    url = input("\nEnter YouTube URL for ingestion test (or press Enter to skip): ").strip()
    
    if not url:
        print("Skipping ingestion test")
        return
    
    print("\n1️⃣ Fetching transcript...")
    transcript = GetVideo.transcript(url)
    
    if transcript.startswith("Error:"):
        print(f"❌ {transcript}")
        return
    
    print(f"✅ Transcript fetched: {len(transcript)} characters")
    
    print("\n2️⃣ Ingesting with correction enabled...")
    rag = RAGChat()
    collection_id = rag.ingest_transcript(url, transcript, enable_correction=True)
    
    print(f"✅ Ingested successfully! Collection ID: {collection_id}")
    
    print("\n3️⃣ Testing a query...")
    question = input("Ask a question about the video: ").strip()
    
    if question:
        result = rag.query_chat(url, question)
        print(f"\n💬 Answer: {result['answer']}")

if __name__ == "__main__":
    print("\n🔧 GEMINI TRANSCRIPT SPELL-CHECK TEST\n")
    
    # Run tests
    test_simple_correction()
    test_real_video()
    test_ingestion_with_correction()
    
    print("\n✅ All tests completed!")
