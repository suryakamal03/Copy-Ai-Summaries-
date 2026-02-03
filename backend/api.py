from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.video_info import GetVideo
from src.model import Model
from src.prompt import Prompt

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
        youtube_url = data.get('url')
        
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
        youtube_url = data.get('url')
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
            model_type="gemini-flash-latest"
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
        youtube_url = data.get('url')
        
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
        youtube_url = data.get('url')
        
        if not youtube_url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Get transcript with timestamps
        transcript_time = GetVideo.transcript_time(youtube_url)
        
        if not transcript_time or transcript_time.startswith('Error:'):
            return jsonify({'error': 'Could not fetch transcript'}), 400
        
        # Generate highlights using Gemini
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
        
        highlights_text = Model.google_gemini(
            transcript=transcript_time,
            prompt=highlight_prompt,
            model_type="gemini-flash-latest"
        )
        
        if isinstance(highlights_text, tuple):
            return jsonify({'error': highlights_text[0]}), 500
        
        # Parse highlights into structured format
        highlights = []
        lines = highlights_text.strip().split('\n')
        current_highlight = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a timestamp (contains " - " and time format)
            if ' - ' in line and any(c.isdigit() for c in line[:15]):
                # Save previous highlight if exists
                if current_highlight:
                    highlights.append(current_highlight)
                
                # Start new highlight
                current_highlight = {
                    'timestamp': line,
                    'description': ''
                }
            elif current_highlight is not None:
                # Add to description
                if current_highlight['description']:
                    current_highlight['description'] += ' ' + line
                else:
                    current_highlight['description'] = line
        
        # Add last highlight
        if current_highlight:
            highlights.append(current_highlight)
        
        return jsonify({
            'highlights': highlights
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
