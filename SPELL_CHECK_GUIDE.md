# Gemini Transcript Spell-Check Feature

## Overview
YouTube's automatic transcription sometimes produces errors, especially with technical terms, tools, and software names. This feature uses Gemini AI to automatically correct transcription errors before ingesting the transcript into the RAG system.

## Common Issues Fixed

### Technical Tool Names
- ❌ "end mapap" → ✅ "nmap"
- ❌ "cubeectl" → ✅ "kubectl"  
- ❌ "darker" → ✅ "docker"
- ❌ "gay it" → ✅ "git"

### Programming Languages & Frameworks
- ❌ "pie thon" → ✅ "Python"
- ❌ "Jango" → ✅ "Django"
- ❌ "no JS" → ✅ "Node.js"
- ❌ "react jay ess" → ✅ "React.js"

### Database & Software
- ❌ "post gray SQL" → ✅ "PostgreSQL"
- ❌ "my sequel" → ✅ "MySQL"
- ❌ "mongo dB" → ✅ "MongoDB"

## How It Works

1. **Pre-Processing**: When a transcript is ingested, it passes through the `correct_transcript()` method first
2. **Gemini Analysis**: Gemini identifies potential transcription errors based on technical context
3. **Correction**: Only clear errors are fixed - meaning and structure are preserved
4. **Validation**: If the correction drastically changes the length, the original is used as a safety measure
5. **Ingestion**: The corrected transcript is then chunked and stored in ChromaDB

## Usage

### Automatic (Default)
The spell-check is **enabled by default** for all transcript ingestions:

```python
from src.rag_chat import RAGChat
from src.video_info import GetVideo

rag = RAGChat()
transcript = GetVideo.transcript(video_url)

# Spell-check is automatically applied
collection_id = rag.ingest_transcript(video_url, transcript, video_title)
```

### Manual Control
You can disable spell-check if needed:

```python
# Disable correction
collection_id = rag.ingest_transcript(
    video_url, 
    transcript, 
    video_title,
    enable_correction=False  # Skip spell-check
)
```

### Standalone Correction
You can also correct a transcript without ingesting:

```python
rag = RAGChat()
corrected_text = rag.correct_transcript(original_transcript)
```

## API Integration

The spell-check works automatically through the backend API:

### Chat Ingestion Endpoint
```bash
POST /api/chat/ingest
{
  "url": "https://youtube.com/watch?v=..."
}
```

The transcript is automatically corrected during ingestion.

### Chat Query Endpoint  
```bash
POST /api/chat/query
{
  "url": "https://youtube.com/watch?v=...",
  "question": "What tools were mentioned?"
}
```

Queries search the corrected transcript, ensuring accurate results.

## Testing

Run the test suite to see the correction in action:

```bash
python test_spell_check.py
```

This will:
1. Test correction on sample technical texts
2. Allow you to test with a real YouTube video
3. Test the full ingestion pipeline with correction

## Configuration

The correction uses:
- **Model**: `gemini-flash-latest` (fast and efficient)
- **Max length**: First 3000 characters to stay within token limits
- **Safety check**: Rejects corrections that change length by >20%

## Benefits

1. **Improved Accuracy**: RAG answers are more accurate with correct technical terms
2. **Better Search**: ChromaDB vector search works better with properly spelled terms
3. **User Experience**: Users get correct tool/software names in responses
4. **Automatic**: No manual intervention needed

## Performance

- **Processing Time**: ~1-2 seconds per transcript
- **API Cost**: Minimal (uses flash model)
- **Accuracy**: High for technical terms and common tools

## Example

**Before Correction:**
> "In this tutorial we'll use end mapap to scan the network and then deploy with darker and cubeectl"

**After Correction:**
> "In this tutorial we'll use nmap to scan the network and then deploy with docker and kubectl"

**Query Result:**  
User: "What tools were mentioned?"
Answer: "The video mentions nmap, docker, and kubectl" ✅

Without correction, the answer might be: "The video mentions end mapap, darker, and cubeectl" ❌

## Notes

- The correction focuses on **technical accuracy** not grammar
- Original sentence structure and meaning are preserved
- If Gemini is uncertain, it leaves terms unchanged
- Works best for technical/educational content
