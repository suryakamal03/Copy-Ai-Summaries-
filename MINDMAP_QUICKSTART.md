# 🧠 Mind Map Feature - Quick Start

## What You Get

The Mind Map tab now includes a powerful AI-powered visualization feature that transforms YouTube video transcripts into structured, hierarchical mind maps.

## How to Use (3 Steps)

### Step 1: Load Your Video
1. Go to the landing page
2. Enter your YouTube URL
3. Click "Generate Summary"

### Step 2: Navigate to Mind Map Tab
1. Click the **"Mind Map"** tab in the results page

### Step 3: Generate
1. Click the blue **"Generate Mind Map"** button
2. Wait 2-5 seconds
3. ✅ View your interactive mind map!

## Example Mind Map

```
                    Python Tutorial
                          |
         +----------------+----------------+
         |                |                |
      Basics          Functions        Data Types
         |                |                |
    +---------+      +---------+      +---------+
    |    |    |      |    |    |      |    |    |
  Vars Print Loop  Define Args  Lists Dicts Sets
```

## Features

✨ **One-Click Generation** - Just press the button
🧠 **AI-Powered** - Gemini analyzes and organizes content
📊 **Interactive Visual** - Explore the hierarchy
🔄 **Regenerate** - Get a fresh perspective anytime
💾 **Export Ready** - View standalone HTML files

## API Endpoints

### Generate Mind Map
```bash
POST http://localhost:5000/api/mindmap
Content-Type: application/json

{
  "url": "https://youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
  "mindmap": "mindmap\n  root((Topic))...",
  "title": "Video Title"
}
```

## Backend Code (api.py)

```python
@app.route('/api/mindmap', methods=['POST'])
def generate_mindmap():
    """Generate mindmap from video transcript using Gemini"""
    data = request.json
    youtube_url = data.get('url')
    
    # Get transcript
    transcript = GetVideo.transcript(youtube_url)
    
    # Generate with Gemini
    mindmap_code = Model.google_gemini(
        transcript=transcript,
        prompt=mindmap_prompt,
        model_type="gemini-flash-latest"
    )
    
    return jsonify({
        'mindmap': mindmap_code,
        'title': video_title
    })
```

## Frontend Integration (ResultsPage.jsx)

```jsx
// State management
const [mindmap, setMindmap] = useState('');
const [mindmapLoading, setMindmapLoading] = useState(false);

// Generate handler
const handleGenerateMindmap = async () => {
  setMindmapLoading(true);
  const response = await fetch('http://localhost:5000/api/mindmap', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: videoUrl }),
  });
  const data = await response.json();
  setMindmap(data.mindmap);
  setMindmapLoading(false);
};

// Render with Mermaid.js
<iframe srcDoc={`
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({ startOnLoad: true });
  </script>
  <div class="mermaid">${mindmap}</div>
`} />
```

## Testing

```bash
# Run the test script
python test_mindmap.py

# Choose option 1 for single video
# Choose option 2 for batch processing
```

## Customization

### Change Mind Map Depth
In `backend/api.py`, modify the prompt:

```python
# More detailed
"Branch out into 6-8 major themes"
"Each theme should have 3-5 sub-topics"

# Simpler
"Branch out into 3-4 major themes"  
"Each theme should have 2-3 sub-topics"
```

### Change Visualization Theme
In `ResultsPage.jsx`, update the Mermaid config:

```javascript
mermaid.initialize({ 
  theme: 'forest'  // Options: default, forest, dark, neutral
});
```

## What Makes It Different?

| Feature | Traditional Notes | Our Mind Map |
|---------|------------------|--------------|
| Speed | Manual, hours | Auto, seconds |
| Structure | Linear | Hierarchical |
| Visual | Text-only | Interactive diagram |
| AI-Powered | No | Yes (Gemini) |
| Updates | Manual edit | One-click regenerate |

## Common Issues

**Q: Mind map not showing?**
A: Check browser console. Try clicking "Regenerate".

**Q: Takes too long?**
A: Long videos (>1 hour) may take 5-10 seconds. This is normal.

**Q: Want different structure?**
A: Click "Regenerate" - Gemini creates a new version each time.

## Files Modified

✅ `backend/api.py` - Added `/api/mindmap` endpoint
✅ `frontend/src/components/ResultsPage.jsx` - Added Mind Map tab UI
✅ `test_mindmap.py` - Testing script
✅ `MINDMAP_FEATURE.md` - Full documentation

## Next Steps

1. **Try it**: Load a video and generate a mind map
2. **Test it**: Run `python test_mindmap.py`
3. **Customize it**: Adjust the prompt for your needs
4. **Export it**: Save the HTML files for offline use

---

💡 **Pro Tip**: Use mind maps for:
- Study guides from lectures
- Meeting notes from recordings
- Content analysis of competitor videos
- Quick overviews before watching long videos
