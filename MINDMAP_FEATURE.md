# Mind Map Generation Feature

## Overview
The Mind Map feature uses ChromaDB chunks and Gemini AI to automatically analyze video transcripts and create visual mind maps that organize key concepts, topics, and their relationships hierarchically.

## Features  

### 🧠 AI-Powered Analysis with ChromaDB
- Uses ChromaDB chunked transcripts for better context understanding
- Gemini analyzes all chunks to identify main themes and structure
- Automatically organizes information hierarchically
- Creates 4-6 major themes with 2-4 sub-topics each
- Uses clear, concise labels for easy understanding
- Proper indentation and hierarchy (General → Specific → Details)

### 📊 Interactive Visualization
- Powered by Mermaid.js for beautiful, interactive diagrams
- Hierarchical tree structure showing relationships
- Clean, professional design
- Responsive and zoomable

### ⚡ One-Click Generation
- Simple "Generate Mind Map" button
- Processes in seconds
- Regenerate anytime with fresh analysis
- Error handling with retry option

## How It Works

### Backend Processing
1. **Transcript Retrieval**: Fetches the video transcript
2. **ChromaDB Ingestion**: Checks if transcript is in ChromaDB, ingests if not
3. **Chunk Retrieval**: Gets ALL chunks from ChromaDB (500 words/chunk with 50-word overlap)
4. **Chunk Organization**: Sorts chunks by index for proper ordering
5. **AI Analysis**: Gemini analyzes all chunks to understand content structure
6. **Hierarchical Mindmap Generation**: Creates well-structured Mermaid.js mindmap syntax
7. **Cleanup**: Removes markdown code blocks and formatting
8. **Return**: Sends clean Mermaid code to frontend with chunk count

### Frontend Display
1. **Generate Button**: User clicks to start generation
2. **Loading State**: Shows spinner during processing
3. **Iframe Rendering**: Embeds Mermaid.js for visualization
4. **Interactive Display**: User can explore the mind map

## Usage

### Via Web Interface

1. **Load a Video**
   - Enter YouTube URL on the landing page
   - Click "Generate Summary"

2. **Navigate to Mind Map Tab**
   - Click the "Mind Map" tab in the results page

3. **Generate Mind Map**
   - Click the "Generate Mind Map" button
   - Wait a few seconds for AI processing
   - View the interactive mind map

4. **Regenerate (Optional)**
   - Click "Regenerate" to create a new version
   - Useful if you want a different perspective

### Via API

**Endpoint**: `POST /api/mindmap`

**Request:**
```json
{
  "url": "https://youtube.com/watch?v=..."
}
```

**Response:**
```json
{
  "mindmap": "mindmap\n  root((Topic))\n    Theme 1\n      Sub 1.1\n    Theme 2\n      Sub 2.1",
  "title": "Video Title"
}
```

**Error Response:**
```json
{
  "error": "Error message"
}
```

### Via Python Script

Test the mindmap generation directly:

```bash
python test_mindmap.py
```

This will:
1. Ask for a YouTube URL
2. Generate the mindmap
3. Save an HTML file you can open in your browser
4. Display the Mermaid code

## Mind Map Structure

```
mindmap
  root((Central Topic))
    Main Theme 1
      Sub-topic 1.1
      Sub-topic 1.2
      Sub-topic 1.3
    Main Theme 2
      Sub-topic 2.1
      Sub-topic 2.2
    Main Theme 3
      Sub-topic 3.1
      Sub-topic 3.2
      Sub-topic 3.3
    Main Theme 4
      Sub-topic 4.1
      Sub-topic 4.2
```

## Example Output

For a Python tutorial video, the mind map might look like:

```
mindmap
  root((Python Programming))
    Basics
      Variables
      Data Types
      Operators
    Control Flow
      If Statements
      Loops
      Functions
    Data Structures
      Lists
      Dictionaries
      Sets
    Advanced Topics
      Classes
      Modules
      Error Handling
```

## Technical Details

### Dependencies
- **Backend**: Gemini API (gemini-flash-latest model)
- **Frontend**: Mermaid.js v10 (loaded via CDN)
- **Rendering**: Iframe with embedded HTML

### Prompt Engineering
The mindmap prompt instructs Gemini to:
- Identify the central topic
- Extract 4-6 main themes
- Create 2-4 sub-topics per theme
- Use concise labels (2-5 words)
- Output only Mermaid syntax (no explanations)

### Code Cleanup
The backend automatically:
- Removes markdown code fences (```)
- Strips "mermaid" language tags
- Trims whitespace
- Validates the output

## Benefits

1. **Quick Understanding**: Get the big picture instantly
2. **Visual Learning**: See relationships between concepts
3. **Study Aid**: Perfect for note-taking and review
4. **Content Overview**: Understand video structure before watching
5. **Export Ready**: Save the HTML file for offline use

## Use Cases

### Students
- Create study guides from lecture videos
- Visualize complex topics
- Review key concepts before exams

### Professionals
- Analyze training videos
- Extract key points from webinars
- Create presentation outlines

### Content Creators
- Analyze competitor content structure
- Plan video outlines
- Understand topic coverage

### Researchers
- Map out interview transcripts
- Organize research video data
- Identify key themes

## Customization

### Change Mind Map Style
Edit the Mermaid initialization in ResultsPage.jsx:

```javascript
mermaid.initialize({ 
  startOnLoad: true,
  theme: 'forest',  // Try: default, forest, dark, neutral
  mindmap: {
    padding: 30,
    useMaxWidth: true
  }
});
```

### Adjust Detail Level
Modify the prompt in backend/api.py:

```python
# For more detailed maps:
"Branch out into 6-8 major themes"
"Each major theme should have 3-5 sub-topics"

# For simpler maps:
"Branch out into 3-4 major themes"
"Each major theme should have 2-3 sub-topics"
```

## Performance

- **Generation Time**: 2-5 seconds (depends on transcript length)
- **API Cost**: ~$0.001 - $0.005 per mindmap (using Flash model)
- **Transcript Limit**: First 3000 characters processed for optimal results

## Error Handling

The feature handles:
- ❌ Failed API calls → Retry button
- ❌ Invalid transcript → Error message
- ❌ Malformed Mermaid → Fallback display
- ❌ Network errors → User-friendly message

## Future Enhancements

Potential improvements:
- [ ] Export as PNG/SVG
- [ ] Multiple visualization styles
- [ ] Collapsible/expandable nodes
- [ ] Color-coded themes
- [ ] Direct download option
- [ ] Share via URL
- [ ] Custom depth control
- [ ] Integration with notes

## Testing

Run comprehensive tests:

```bash
# Single video test
python test_mindmap.py

# Choose option 1 for single video
# Choose option 2 for batch processing
```

## Troubleshooting

**Mind map not displaying?**
- Check browser console for errors
- Ensure Mermaid.js CDN is accessible
- Try regenerating the mind map

**Generation takes too long?**
- Video transcript might be very long
- Check your internet connection
- Verify Gemini API key is valid

**Mind map looks incorrect?**
- Click "Regenerate" for a fresh analysis
- Gemini interprets content differently each time
- Some videos may not have clear structure

## Credits

- **AI Model**: Google Gemini Flash
- **Visualization**: Mermaid.js
- **Framework**: React + Flask
