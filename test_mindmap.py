"""Test mindmap generation with ChromaDB chunks and Gemini"""
from src.video_info import GetVideo
from src.model import Model
from src.rag_chat import RAGChat

def test_mindmap_generation():
    """Test mindmap generation from ChromaDB chunks"""
    print("=" * 60)
    print("TESTING MINDMAP GENERATION (ChromaDB + Gemini)")
    print("=" * 60)
    
    # Get video URL from user
    url = input("\nEnter YouTube URL (or press Enter to use default): ").strip()
    
    if not url:
        # Default test video
        url = "https://youtu.be/z89eJUwuwII"
        print(f"Using default video: {url}")
    
    print("\n1️⃣ Fetching video information...")
    video_title = GetVideo.title(url)
    print(f"   Title: {video_title}")
    
    print("\n2️⃣ Fetching transcript...")
    transcript = GetVideo.transcript(url)
    
    if transcript.startswith("Error:"):
        print(f"   ❌ {transcript}")
        return
    
    print(f"   ✅ Transcript fetched: {len(transcript)} characters")
    
    print("\n3️⃣ Initializing ChromaDB...")
    rag = RAGChat()
    
    # Check if collection exists, if not ingest
    collection_id = rag.generate_video_id(url)
    try:
        collection = rag.client.get_collection(name=collection_id)
        print(f"   ✅ Collection found: {collection_id}")
    except:
        print(f"   📥 Collection not found, ingesting transcript...")
        collection_id = rag.ingest_transcript(url, transcript, video_title)
        collection = rag.client.get_collection(name=collection_id)
        print(f"   ✅ Transcript ingested successfully")
    
    print("\n4️⃣ Retrieving ALL chunks from ChromaDB...")
    all_results = collection.get()
    all_chunks = all_results.get('documents', [])
    chunk_count = len(all_chunks)
    print(f"   ✅ Retrieved {chunk_count} chunks")
    
    # Organize chunks by their index for proper ordering
    metadatas = all_results.get('metadatas', [])
    indexed_chunks = []
    for i, chunk in enumerate(all_chunks):
        chunk_index = metadatas[i].get('chunk_index', i) if i < len(metadatas) else i
        indexed_chunks.append((chunk_index, chunk))
    
    # Sort by index and join
    indexed_chunks.sort(key=lambda x: x[0])
    chunks_text = "\n\n".join([chunk for _, chunk in indexed_chunks])
    print(f"   ✅ Organized and concatenated {len(indexed_chunks)} chunks")
    
    print("\n5️⃣ Generating hierarchical mindmap with Gemini...")
    mindmap_prompt = """Create a comprehensive, hierarchical mindmap from the video transcript chunks.

CRITICAL RULES - FOLLOW EXACTLY:

1. MANDATORY STRUCTURE (NO FLAT LISTS):
   - ONE central node with main topic in double parentheses: root((Topic Name))
   - EXACTLY 5-7 Level 1 branches (major categories)
   - EACH Level 1 branch MUST have 3-5 Level 2 sub-branches
   - SOME Level 2 branches should have 2-3 Level 3 details
   - CREATE A DEEP TREE, NOT A FLAT LIST

2. CONTENT ORGANIZATION:
   - Analyze ALL chunks to identify main themes
   - Group related information under appropriate categories
   - Categories: Setup, Tools, Techniques, Methods, Security, Advanced Topics, Best Practices, etc.
   - NO timestamps, NO single-line items
   - Create logical parent-child relationships

3. LABELING RULES:
   - Labels: 2-6 words maximum
   - Be specific and descriptive
   - Use technical terms from the video
   - NO generic labels like "Topic 1" or "Item A"

4. INDENTATION (CRITICAL):
   - Level 0: "mindmap" (first line)
   - Level 1: "  root((Central Topic))" (2 spaces)
   - Level 2: "    Major Category" (4 spaces) 
   - Level 3: "      Sub-concept" (6 spaces)
   - Level 4: "        Specific detail" (8 spaces)

5. EXAMPLE OF CORRECT STRUCTURE:

mindmap
  root((Ethical Hacking and Kali Linux))
    Fundamentals and Setup
      What is Ethical Hacking
      Legal and Ethical Boundaries
      Kali Linux Installation
      Recommended Environment
    Network Mapping Tools
      Nmap Network Scanner
        Advanced Scan Types
        Port Discovery Methods
      Netdiscover Tool
      Packet Sniffers
    Vulnerability Assessment
      Metasploit Framework
        Exploit Database Access
        Payload Configuration
      Web Vulnerability Scanners
      SQL Injection Tools
    Wi-Fi Hacking Techniques
      Password Cracking Tools
        Aircrack-ng Suite
        Dictionary Attacks
      WPA Key Recovery
      Network Monitoring
    Exploitation Methods
      Remote Code Execution
      Privilege Escalation
      Credential Harvesting
    Advanced Attacks
      Database Exploitation
        SQL Injection Attacks
        NoSQL Vulnerabilities
      Social Engineering
      Forensics Tools
    Security Best Practices
      Legal Compliance
      Permission Requirements
      Ethical Guidelines

OUTPUT REQUIREMENTS:
- Start with "mindmap" on line 1
- NO markdown code blocks (```), NO explanations
- ONLY the mindmap code
- Minimum 5 major branches
- Minimum 15 total sub-branches
- Create deep hierarchy (3-4 levels deep)

Now analyze the video transcript chunks and create a DEEP, HIERARCHICAL mindmap:"""
    
    mindmap_code = Model.google_gemini(
        transcript=chunks_text,
        prompt=mindmap_prompt,
        model_type="gemini-flash-latest"
    )
    
    if isinstance(mindmap_code, tuple):
        print(f"   ❌ Error: {mindmap_code[0]}")
        return
    
    # Clean up the response
    mindmap_code = mindmap_code.strip()
    if mindmap_code.startswith('```'):
        lines = mindmap_code.split('\n')
        mindmap_code = '\n'.join(lines[1:-1]) if len(lines) > 2 else mindmap_code
        mindmap_code = mindmap_code.replace('```mermaid', '').replace('```', '').strip()
    
    print("   ✅ Mindmap generated successfully!")
    print("\n" + "=" * 60)
    print("GENERATED MERMAID CODE:")
    print("=" * 60)
    print(mindmap_code)
    print("=" * 60)
    
    # Save to file for visualization
    output_file = "mindmap_output.html"
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mind Map - {video_title}</title>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            mindmap: {{
                padding: 20,
                useMaxWidth: true
            }}
        }});
    </script>
    <style>
        body {{
            margin: 0;
            padding: 40px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 24px;
        }}
        .mermaid {{
            width: 100%;
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Mind Map: {video_title}</h1>
        <div class="mermaid">
{mindmap_code}
        </div>
    </div>
</body>
</html>"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Mindmap saved to: {output_file}")
    print(f"   Open this file in your browser to view the interactive mindmap!")

def test_multiple_videos():
    """Test mindmap generation for multiple videos"""
    print("\n" + "=" * 60)
    print("BATCH MINDMAP GENERATION")
    print("=" * 60)
    
    videos = []
    while True:
        url = input("\nEnter YouTube URL (or press Enter to finish): ").strip()
        if not url:
            break
        videos.append(url)
    
    if not videos:
        print("No videos provided.")
        return
    
    for i, url in enumerate(videos, 1):
        print(f"\n{'='*60}")
        print(f"Processing video {i}/{len(videos)}")
        print(f"{'='*60}")
        
        try:
            video_title = GetVideo.title(url)
            print(f"Title: {video_title}")
            
            transcript = GetVideo.transcript(url)
            if transcript.startswith("Error:"):
                print(f"❌ Skipped: {transcript}")
                continue
            
            mindmap_prompt = """Create a mindmap in Mermaid.js format. Output ONLY raw Mermaid code starting with 'mindmap', no explanations."""
            
            mindmap_code = Model.google_gemini(
                transcript=transcript,
                prompt=mindmap_prompt,
                model_type="gemini-flash-latest"
            )
            
            if isinstance(mindmap_code, tuple):
                print(f"❌ Error: {mindmap_code[0]}")
                continue
            
            # Clean up
            mindmap_code = mindmap_code.strip()
            if mindmap_code.startswith('```'):
                lines = mindmap_code.split('\n')
                mindmap_code = '\n'.join(lines[1:-1]) if len(lines) > 2 else mindmap_code
                mindmap_code = mindmap_code.replace('```mermaid', '').replace('```', '').strip()
            
            # Save individual file
            filename = f"mindmap_{i}_{video_title[:30].replace(' ', '_')}.html"
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{video_title}</title>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
    <style>
        body {{ margin: 0; padding: 40px; background: #f5f5f5; font-family: sans-serif; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; }}
        h1 {{ color: #333; margin-bottom: 20px; }}
        .mermaid {{ width: 100%; display: flex; justify-content: center; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 {video_title}</h1>
        <div class="mermaid">
{mindmap_code}
        </div>
    </div>
</body>
</html>"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Saved: {filename}")
            
        except Exception as e:
            print(f"❌ Error processing video: {e}")
    
    print(f"\n✅ Batch processing complete! Generated {len(videos)} mindmaps.")

if __name__ == "__main__":
    print("\n🧠 GEMINI MINDMAP GENERATION TEST\n")
    
    while True:
        print("\nOptions:")
        print("1. Generate single mindmap")
        print("2. Batch generate multiple mindmaps")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            test_mindmap_generation()
        elif choice == '2':
            test_multiple_videos()
        elif choice == '3':
            print("\n👋 Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
