from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import re

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.video_info import GetVideo
from src.model import Model
from src.prompt import Prompt
from src.rag_chat import RAGChat


def _parse_timestamped_transcript(transcript_text):
    """Extract ordered timestamped snippets from the timestamped transcript payload."""
    if not transcript_text:
        return []

    pattern = r'(.*?)(?:\s+"time:([0-9]{2}:[0-9]{2}:[0-9]{2})")'
    matches = re.findall(pattern, transcript_text)
    snippets = []

    for text, timestamp in matches:
        cleaned_text = ' '.join(text.split()).strip()
        if cleaned_text:
            snippets.append((timestamp, cleaned_text))

    return snippets


def _build_fallback_highlights(transcript_time, target_count=6):
    """Create usable highlights directly from timestamped transcript snippets."""
    snippets = _parse_timestamped_transcript(transcript_time)
    if not snippets:
        return []

    if len(snippets) <= target_count:
        selected = snippets
    else:
        step = max(1, len(snippets) // target_count)
        selected = [snippets[index] for index in range(0, len(snippets), step)][:target_count]

    highlights = []
    for index, (timestamp, text) in enumerate(selected):
        start_time = timestamp
        if index + 1 < len(selected):
            end_time = selected[index + 1][0]
        else:
            end_time = timestamp

        summary = text
        if len(summary) > 180:
            summary = summary[:177].rstrip() + '...'

        highlights.append({
            'timestamp': f'{start_time} - {end_time}',
            'description': summary,
        })

    return highlights

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    """Get video title and ID from URL"""
    try:
        data = request.json
        youtube_url = (data.get('url') or '').strip()
        
        if not youtube_url:
            return jsonify({'error': 'URL is required'}), 400
        
        video_id = GetVideo.Id(youtube_url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        video_title = GetVideo.title(youtube_url)
        
        return jsonify({
            'videoId': video_id,
            'title': video_title,
            'thumbnailUrl': f'http://img.youtube.com/vi/{video_id}/0.jpg'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summary', methods=['POST'])
def generate_summary():
    """Generate video summary"""
    try:
        data = request.json
        youtube_url = (data.get('url') or '').strip()
        summary_type = data.get('summaryType', 'detailed')  # 'short', 'detailed', or 'full'
        
        if not youtube_url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Get transcript
        transcript = GetVideo.transcript(youtube_url)
        
        if not transcript or transcript.startswith('Error:'):
            return jsonify({'error': 'Could not fetch transcript'}), 400
        
        # Map summary type to prompt ID
        prompt_map = {
            'short': 'short',
            'detailed': 'detailed',
            'full': 0
        }
        
        prompt_id = prompt_map.get(summary_type, 'detailed')
        
        # Generate summary using Gemini
        summary = Model.google_gemini(
            transcript=transcript,
            prompt=Prompt.prompt1(ID=prompt_id),
            model_type="gemini-2.5-flash"
        )
        
        # Check if summary generation failed
        if isinstance(summary, tuple):
            return jsonify({'error': summary[0], 'details': summary[1]}), 500
        
        return jsonify({
            'summary': summary,
            'summaryType': summary_type
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transcript', methods=['POST'])
def get_transcript():
    """Get video transcript"""
    try:
        data = request.json
        youtube_url = (data.get('url') or '').strip()
        
        if not youtube_url:
            return jsonify({'error': 'URL is required'}), 400
        
        transcript = GetVideo.transcript(youtube_url)
        
        if not transcript or transcript.startswith('Error:'):
            return jsonify({'error': 'Could not fetch transcript'}), 400
        
        return jsonify({
            'transcript': transcript
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/highlights', methods=['POST'])
def generate_highlights():
    """Generate video highlights with timestamps"""
    try:
        data = request.json
        youtube_url = (data.get('url') or '').strip()
        
        if not youtube_url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Get transcript with timestamps
        transcript_time = GetVideo.transcript_time(youtube_url)
        
        if not transcript_time or transcript_time.startswith('Error:'):
            return jsonify({'error': 'Could not fetch transcript'}), 400
        
        fallback_highlights = _build_fallback_highlights(transcript_time)

        # Generate highlights using Gemini when available, but keep a transcript-based fallback.
        highlight_prompt = """Analyze the video transcript below and generate key highlights with timestamps.

For each highlight:
1. Identify the time range (start - end time)
2. Provide a clear, informative explanation of what happens in that segment
3. Focus on important topics, transitions, or key information

Format each highlight as:
TIME_START - TIME_END
[Explanation of what this segment covers]

Generate 5-8 highlights that cover the main parts of the video.

VIDEO TRANSCRIPT WITH TIMESTAMPS:
"""
        
        highlights = []
        try:
            highlights_text = Model.google_gemini(
                transcript=transcript_time,
                prompt=highlight_prompt,
                model_type="gemini-2.5-flash"
            )

            if isinstance(highlights_text, tuple):
                raise RuntimeError(highlights_text[0])

            lines = (highlights_text or '').strip().split('\n')
            current_highlight = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check if line is a timestamp (contains " - " and time format)
                if ' - ' in line and any(c.isdigit() for c in line[:15]):
                    if current_highlight:
                        highlights.append(current_highlight)

                    current_highlight = {
                        'timestamp': line,
                        'description': '',
                    }
                elif current_highlight is not None:
                    if current_highlight['description']:
                        current_highlight['description'] += ' ' + line
                    else:
                        current_highlight['description'] = line

            if current_highlight:
                highlights.append(current_highlight)
        except Exception as gemini_error:
            print(f"Gemini highlights generation failed, using fallback: {gemini_error}")

        if not highlights:
            highlights = fallback_highlights

        if not highlights:
            return jsonify({'error': 'Could not generate highlights from transcript'}), 500
        
        return jsonify({
            'highlights': highlights
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/ingest', methods=['POST'])
def chat_ingest():
    """Ingest video transcript into ChromaDB for RAG chatbot"""
    try:
        data = request.json
        youtube_url = data.get('url')
        
        if not youtube_url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Get transcript
        transcript = GetVideo.transcript(youtube_url)
        
        if not transcript or transcript.startswith('Error:'):
            print(f"Failed to get transcript for {youtube_url}")
            return jsonify({'error': 'Could not fetch transcript'}), 400
        
        print(f"Transcript fetched successfully, length: {len(transcript)} chars")
        
        # Get video title
        video_title = GetVideo.title(youtube_url)
        print(f"Video title: {video_title}")
        
        # Initialize RAG and ingest
        print("Initializing RAG chat...")
        rag = RAGChat()
        print("Starting ingestion...")
        collection_id = rag.ingest_transcript(youtube_url, transcript, video_title)
        print(f"Ingestion completed successfully. Collection ID: {collection_id}")
        
        return jsonify({
            'success': True,
            'collection_id': collection_id,
            'message': 'Transcript ingested successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/query', methods=['POST'])
def chat_query():
    """Query the RAG chatbot"""
    try:
        data = request.json
        youtube_url = data.get('url')
        question = data.get('question')
        
        if not youtube_url or not question:
            return jsonify({'error': 'URL and question are required'}), 400
        
        # Initialize RAG
        rag = RAGChat()
        
        # Check if collection exists, if not ingest first
        if not rag.check_collection_exists(youtube_url):
            # Auto-ingest transcript
            transcript = GetVideo.transcript(youtube_url)
            if not transcript or transcript.startswith('Error:'):
                return jsonify({'error': 'Could not fetch transcript'}), 400
            
            video_title = GetVideo.title(youtube_url)
            rag.ingest_transcript(youtube_url, transcript, video_title)
        
        # Query chat
        result = rag.query_chat(youtube_url, question)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mindmap', methods=['POST'])
def generate_mindmap():
    """Generate mindmap from video transcript using ChromaDB chunks and Gemini"""
    try:
        data = request.json
        youtube_url = data.get('url')
        
        if not youtube_url:
            return jsonify({'error': 'URL is required'}), 400
        
        print(f"Generating mindmap for URL: {youtube_url}")
        
        # Get transcript
        transcript = GetVideo.transcript(youtube_url)
        
        print(f"Transcript fetched: {len(transcript) if transcript else 0} characters")
        
        if not transcript or transcript.startswith('Error:'):
            error_msg = transcript if transcript else 'No transcript available'
            print(f"Error fetching transcript: {error_msg}")
            return jsonify({'error': f'Could not fetch transcript: {error_msg}'}), 400
        
        # Get video title
        video_title = GetVideo.title(youtube_url)
        
        # Initialize RAG to work with ChromaDB
        print("Initializing RAG for ChromaDB access...")
        rag = RAGChat()
        
        # Check if collection exists, if not ingest first
        collection_id = rag.generate_video_id(youtube_url)
        try:
            collection = rag.client.get_collection(name=collection_id)
            print(f"Collection found: {collection_id}")
        except:
            print(f"Collection not found, ingesting transcript...")
            collection_id = rag.ingest_transcript(youtube_url, transcript, video_title)
            collection = rag.client.get_collection(name=collection_id)
            print(f"Transcript ingested successfully")
        
        # Get ALL chunks from ChromaDB
        all_results = collection.get()
        all_chunks = all_results.get('documents', [])
        chunk_count = len(all_chunks)
        print(f"Retrieved {chunk_count} chunks from ChromaDB")
        
        if not all_chunks:
            print("No chunks found, falling back to raw transcript")
            chunks_text = transcript
        else:
            # Organize chunks by their index for proper ordering
            metadatas = all_results.get('metadatas', [])
            indexed_chunks = []
            for i, chunk in enumerate(all_chunks):
                chunk_index = metadatas[i].get('chunk_index', i) if i < len(metadatas) else i
                indexed_chunks.append((chunk_index, chunk))
            
            # Sort by index and join
            indexed_chunks.sort(key=lambda x: x[0])
            chunks_text = "\n\n".join([chunk for _, chunk in indexed_chunks])
            print(f"Organized and concatenated {len(indexed_chunks)} chunks")
        
        # Generate mindmap using Gemini with valid Mermaid syntax
        mindmap_prompt = """You are an expert at creating valid Mermaid.js mindmaps. Analyze the video transcript and create a hierarchical mindmap.

MERMAID MINDMAP SYNTAX RULES (CRITICAL - FOLLOW EXACTLY):

1. Valid Mermaid mindmap structure:
```
mindmap
  root((Main Topic))
    Branch 1
      Sub Branch 1a
      Sub Branch 1b
    Branch 2
      Sub Branch 2a
```

2. INDENTATION RULES (EXACT SPACES):
   - "mindmap" = no indentation
   - "root" = 2 spaces
   - Level 1 branches = 4 spaces
   - Level 2 branches = 6 spaces
   - Level 3 branches = 8 spaces

3. TEXT RULES:
   - Root node MUST use double parentheses: root((Text Here))
   - All other nodes: just plain text, NO special characters
   - NO quotes, NO brackets except for root
   - Keep text simple: 2-5 words per node
   - Avoid special chars: & / \ @ # $ % * + =

4. STRUCTURE REQUIREMENTS:
   - Create 5-7 main branches (Level 1)
   - Each main branch should have 3-5 sub-branches (Level 2)
   - Some sub-branches can have details (Level 3)
   - Make it hierarchical and balanced

5. EXAMPLE (COPY THIS STRUCTURE):
mindmap
  root((Ethical Hacking Basics))
    Introduction and Setup
      What is Ethical Hacking
      Legal Framework
      Kali Linux Setup
    Core Tools
      Network Scanners
        Nmap Tool
        Netdiscover
      Password Crackers
      Vulnerability Scanners
    Hacking Techniques
      Wi-Fi Hacking
        WPA Cracking
        Aircrack Suite
      Web Exploitation
      SQL Injection
    Advanced Methods
      Metasploit Framework
      Social Engineering
      Privilege Escalation
    Security Practices
      Legal Compliance
      Ethical Guidelines
      Permission Requirements

IMPORTANT:
- Output ONLY the mindmap code
- Start with "mindmap" (no code blocks)
- Use EXACT spacing (count the spaces!)
- NO special characters in node text
- Make it deep and hierarchical

Now create the mindmap from the transcript:"""
        
        # Call Gemini with chunks
        print(f"Calling Gemini API to generate hierarchical mindmap...")
        mindmap_code = Model.google_gemini(
            chunks_text,
            mindmap_prompt,
            "",
            "gemini-flash-latest"
        )
        
        print(f"Gemini response type: {type(mindmap_code)}")
        
        if isinstance(mindmap_code, tuple):
            print(f"Gemini API error: {mindmap_code}")
            return jsonify({'error': mindmap_code[0], 'details': mindmap_code[1]}), 500
        
        # Clean up the response - remove markdown code blocks if present
        mindmap_code = mindmap_code.strip()
        print(f"Generated mindmap length: {len(mindmap_code)} characters")
        
        if mindmap_code.startswith('```'):
            # Remove markdown code fences
            lines = mindmap_code.split('\n')
            mindmap_code = '\n'.join(lines[1:-1]) if len(lines) > 2 else mindmap_code
            mindmap_code = mindmap_code.replace('```mermaid', '').replace('```', '').strip()
        
        # Additional cleanup - ensure it starts with "mindmap"
        if not mindmap_code.startswith('mindmap'):
            lines = mindmap_code.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('mindmap'):
                    mindmap_code = '\n'.join(lines[i:])
                    break
        
        # Clean special characters that break Mermaid
        lines = mindmap_code.split('\n')
        cleaned_lines = []
        for line in lines:
            # Keep indentation but clean text
            if line.strip():
                # Don't clean the root node with (())
                if '((' in line and '))' in line:
                    cleaned_lines.append(line)
                else:
                    # Remove problematic characters from regular nodes
                    cleaned_line = line.replace(':', ' -').replace(';', ',').replace('"', '').replace("'", '')
                    cleaned_line = cleaned_line.replace('&', 'and').replace('/', ' or ')
                    cleaned_lines.append(cleaned_line)
            else:
                cleaned_lines.append(line)
        
        mindmap_code = '\n'.join(cleaned_lines)
        
        print(f"Mindmap generated successfully with {chunk_count} chunks")
        print(f"First 300 chars: {mindmap_code[:300]}")
        
        return jsonify({
            'mindmap': mindmap_code,
            'title': video_title,
            'chunks_used': chunk_count
        })
    
    except Exception as e:
        print(f"Exception in generate_mindmap: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
