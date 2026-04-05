import { useState, useEffect } from 'react';
import { FiRefreshCw, FiSend } from 'react-icons/fi';

function ResultsPage({ videoUrl, videoInfo, summary, transcript, onNewVideo, onRegenerateSummary }) {
  const [activeTab, setActiveTab] = useState('output');
  const [question, setQuestion] = useState('');
  const [summaryType, setSummaryType] = useState('detailed');
  const [currentSummary, setCurrentSummary] = useState(summary);
  const [loading, setLoading] = useState(false);
  const [highlights, setHighlights] = useState([]);
  const [highlightsLoading, setHighlightsLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [ingestionComplete, setIngestionComplete] = useState(false);
  const [ingestionError, setIngestionError] = useState(null);
  const [mindmap, setMindmap] = useState('');
  const [mindmapLoading, setMindmapLoading] = useState(false);
  const [mindmapChunksUsed, setMindmapChunksUsed] = useState(0);

  // Auto-ingest transcript for RAG on mount
  useEffect(() => {
    const ingestTranscript = async () => {
      try {
        console.log('Starting transcript ingestion...');
        const response = await fetch('http://localhost:5000/api/chat/ingest', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: videoUrl }),
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log('Ingestion complete:', data);
          setIngestionComplete(true);
        } else {
          const error = await response.json();
          console.error('Ingestion failed:', error);
          setIngestionError(error.error || 'Failed to process transcript');
        }
      } catch (error) {
        console.error('Error ingesting transcript:', error);
        setIngestionError('Network error during transcript processing');
      }
    };
    ingestTranscript();
  }, [videoUrl]);

  // Fetch highlights when highlights tab is clicked
  const handleTabChange = async (tab) => {
    setActiveTab(tab);
    
    if (tab === 'highlights' && highlights.length === 0 && !highlightsLoading) {
      setHighlightsLoading(true);
      try {
        const response = await fetch('http://localhost:5000/api/highlights', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ url: videoUrl }),
        });

        if (response.ok) {
          const data = await response.json();
          setHighlights(data.highlights || []);
        }
      } catch (error) {
        console.error('Error fetching highlights:', error);
      } finally {
        setHighlightsLoading(false);
      }
    }
  };

  const handleSummaryTypeChange = async (e) => {
    const newType = e.target.value;
    setSummaryType(newType);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/summary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          url: videoUrl, 
          summaryType: newType 
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentSummary(data.summary);
      }
    } catch (error) {
      console.error('Error regenerating summary:', error);
    } finally {
      setLoading(false);
    }
  };

  // Extract video ID from URL
  const getVideoId = (url) => {
    const regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[7].length === 11) ? match[7] : '';
  };

  const videoId = videoInfo?.videoId || getVideoId(videoUrl);
  const videoTitle = videoInfo?.title || 'Video Summary';

  const handleAskQuestion = async (e) => {
    e.preventDefault();
    if (!question.trim() || chatLoading || !ingestionComplete) return;

    const userQuestion = question.trim();
    setQuestion('');

    // Add user message to chat
    setChatMessages(prev => [...prev, { role: 'user', content: userQuestion }]);
    setChatLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/chat/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: videoUrl, question: userQuestion }),
      });

      if (response.ok) {
        const data = await response.json();
        setChatMessages(prev => [
          ...prev,
          { role: 'assistant', content: data.answer, sources: data.sources }
        ]);
      } else {
        const error = await response.json();
        setChatMessages(prev => [
          ...prev,
          { role: 'assistant', content: `Error: ${error.error}` }
        ]);
      }
    } catch (error) {
      console.error('Error querying chat:', error);
      setChatMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Failed to get response. Please try again.' }
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleGenerateMindmap = async () => {
    setMindmapLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/mindmap', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: videoUrl }),
      });

      if (response.ok) {
        const data = await response.json();
        setMindmap(data.mindmap);
        setMindmapChunksUsed(data.chunks_used || 0);
      } else {
        const error = await response.json();
        console.error('Error generating mindmap:', error);
        
        // Check if it's a rate limit error
        if (error.error && error.error.includes('rate limit')) {
          alert('⚠️ YouTube Rate Limit Reached\n\nYouTube is temporarily blocking transcript requests from your IP.\n\nSolutions:\n1. Wait 10-15 minutes and try again\n2. Try a different video\n3. Restart your router to get a new IP');
        }
        
        setMindmap('error');
      }
    } catch (error) {
      console.error('Error generating mindmap:', error);
      setMindmap('error');
    } finally {
      setMindmapLoading(false);
    }
  };

  // Format transcript for display
  const formatTranscript = (text) => {
    if (!text) return [];
    
    // Split into chunks of ~50 characters for demo
    const words = text.split(' ');
    const chunks = [];
    let currentChunk = '';
    let time = 0;
    
    for (const word of words) {
      currentChunk += word + ' ';
      if (currentChunk.length > 50) {
        chunks.push({ time: formatTime(time), text: currentChunk.trim() });
        currentChunk = '';
        time += 3;
      }
    }
    
    if (currentChunk) {
      chunks.push({ time: formatTime(time), text: currentChunk.trim() });
    }
    
    return chunks.slice(0, 20); // Show first 20 chunks
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const transcriptChunks = formatTranscript(transcript);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4 bg-slate-950/90 backdrop-blur">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-slate-100 truncate max-w-2xl">
            {videoTitle}
          </h1>
          <div className="flex items-center gap-3">
            <button
              onClick={onNewVideo}
              className="flex items-center gap-2 px-4 py-2 text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <FiRefreshCw className="w-4 h-4" />
              <span className="text-sm font-medium">New Video</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-73px)]">
        {/* Left Panel - Video */}
        <div className="w-[52%] border-r border-slate-800 p-6 flex flex-col bg-slate-950">
          {/* Video Player */}
          <div className="bg-black rounded-lg overflow-hidden mb-4 ring-1 ring-slate-800">
            <iframe
              className="w-full aspect-video"
              src={`https://www.youtube.com/embed/${videoId}`}
              title="YouTube video player"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          </div>

          {/* View on YouTube Link */}
          <a
            href={videoUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sky-400 hover:text-sky-300 mb-6 text-sm"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
            </svg>
            View on YouTube
          </a>

          {/* Video Script Section */}
          <div className="flex-1 bg-slate-900 rounded-lg p-4 overflow-hidden flex flex-col border border-slate-800">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-slate-100">Video Script</h3>
              <button className="flex items-center gap-1.5 text-sm text-slate-300 hover:text-slate-100">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy
              </button>
            </div>
            <div className="flex-1 overflow-y-auto text-sm text-slate-300 space-y-2">
              {transcriptChunks.length > 0 ? (
                transcriptChunks.map((chunk, idx) => (
                  <p key={idx} className="flex gap-2">
                    <span className="text-slate-500 font-mono text-xs">{chunk.time}</span>
                    <span>{chunk.text}</span>
                  </p>
                ))
              ) : (
                <p className="text-slate-500 italic">No transcript available</p>
              )}
            </div>
          </div>
        </div>

        {/* Right Panel - Output */}
        <div className="w-[48%] flex flex-col bg-slate-950">
          {/* Tabs */}
          <div className="border-b border-slate-800">
            <div className="flex">
              {['Output', 'Highlights', 'Mind Map', 'Chat'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => handleTabChange(tab.toLowerCase().replace(' ', '-'))}
                  className={`px-6 py-3.5 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.toLowerCase().replace(' ', '-')
                      ? 'border-sky-400 text-sky-300'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto p-6 bg-slate-950">
            {activeTab === 'output' && (
              <div>
                {/* Summary Type Selector */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-slate-200 mb-2">
                    Summary Type:
                  </label>
                  <select
                    value={summaryType}
                    onChange={handleSummaryTypeChange}
                    disabled={loading}
                    className="block w-full max-w-xs px-3 py-2 bg-slate-900 border border-slate-700 text-slate-100 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent disabled:bg-slate-800 disabled:cursor-not-allowed text-sm"
                  >
                    <option value="short">Short Summary</option>
                    <option value="detailed">Detailed Summary</option>
                    <option value="full">Full Explanation</option>
                  </select>
                </div>

                {/* Summary Content */}
                {loading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="flex flex-col items-center gap-3">
                      <svg className="animate-spin h-8 w-8 text-slate-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <p className="text-sm text-slate-400">Generating summary...</p>
                    </div>
                  </div>
                ) : (
                  <div className="text-slate-200 text-[15px] leading-relaxed whitespace-pre-wrap">
                    {currentSummary || 'No summary available'}
                  </div>
                )}
              </div>
            )}
            {activeTab === 'highlights' && (
              <div>
                {highlightsLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="flex flex-col items-center gap-3">
                      <svg className="animate-spin h-8 w-8 text-slate-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <p className="text-sm text-slate-400">Generating highlights...</p>
                    </div>
                  </div>
                ) : highlights.length > 0 ? (
                  <div className="space-y-6">
                    {highlights.map((highlight, index) => (
                      <div key={index} className="border-l-4 border-sky-500 pl-4">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-sky-400 font-mono text-sm font-semibold">
                            {highlight.timestamp}
                          </span>
                          <button className="ml-auto p-1 text-slate-400 hover:text-slate-200">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                          </button>
                        </div>
                        <p className="text-slate-200 text-[15px] leading-relaxed">
                          {highlight.description}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-400">
                    No highlights available
                  </div>
                )}
              </div>
            )}
            {activeTab === 'mind-map' && (
              <div className="h-full flex flex-col">
                {!mindmap ? (
                  <div className="flex flex-col items-center justify-center flex-1">
                    <div className="text-center max-w-md">
                      <svg className="w-16 h-16 mx-auto mb-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                      </svg>
                      <h3 className="text-lg font-semibold text-slate-100 mb-2">Generate Mind Map</h3>
                      <p className="text-sm text-slate-400 mb-6">
                        Create a visual mind map that organizes the key concepts and topics from this video
                      </p>
                      <button
                        onClick={handleGenerateMindmap}
                        disabled={mindmapLoading}
                        className="inline-flex items-center gap-2 px-6 py-3 bg-sky-600 text-white font-medium rounded-lg hover:bg-sky-700 transition-colors disabled:bg-slate-700 disabled:cursor-not-allowed"
                      >
                        {mindmapLoading ? (
                          <>
                            <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Generating Mind Map...
                          </>
                        ) : (
                          <>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                            Generate Mind Map
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                ) : mindmap === 'error' ? (
                  <div className="flex items-center justify-center flex-1">
                      <div className="text-center text-red-400">
                      <p className="font-semibold mb-1">Failed to generate mind map</p>
                      <p className="text-sm text-slate-400">Please try again</p>
                      <button
                        onClick={handleGenerateMindmap}
                        className="mt-4 px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
                      >
                        Retry
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="h-full flex flex-col">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-slate-100">Mind Map</h3>
                        {mindmapChunksUsed > 0 && (
                          <p className="text-xs text-slate-400 mt-0.5">
                            Generated from {mindmapChunksUsed} ChromaDB chunks
                          </p>
                        )}
                      </div>
                      <button
                        onClick={() => { setMindmap(''); setMindmapChunksUsed(0); }}
                        className="text-sm text-slate-400 hover:text-slate-200 flex items-center gap-1"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        Regenerate
                      </button>
                    </div>
                    <div className="flex-1 border border-slate-800 rounded-lg overflow-hidden bg-slate-900">
                      <iframe
                        srcDoc={`
                          <!DOCTYPE html>
                          <html>
                            <head>
                              <script type="module">
                                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                                mermaid.initialize({ 
                                  startOnLoad: true,
                                  theme: 'dark',
                                  mindmap: {
                                    padding: 20,
                                    useMaxWidth: true
                                  }
                                });
                              </script>
                              <style>
                                body {
                                  margin: 0;
                                  padding: 20px;
                                  display: flex;
                                  justify-content: center;
                                  align-items: center;
                                  min-height: 100vh;
                                  background: #0f172a;
                                }
                                .mermaid {
                                  width: 100%;
                                  display: flex;
                                  justify-content: center;
                                }
                              </style>
                            </head>
                            <body>
                              <div class="mermaid">
${mindmap}
                              </div>
                            </body>
                          </html>
                        `}
                        className="w-full h-full"
                        title="Mind Map"
                      />
                    </div>
                  </div>
                )}
              </div>
            )}
            {activeTab === 'chat' && (
              <div className="flex flex-col h-full">
                {chatMessages.length === 0 ? (
                  <div className="flex items-center justify-center flex-1">
                    {!ingestionComplete ? (
                      <div className="text-center">
                        {ingestionError ? (
                          <div className="text-red-500 text-sm">
                            <p className="font-semibold mb-1">Error processing transcript</p>
                            <p className="text-xs">{ingestionError}</p>
                          </div>
                        ) : (
                            <div className="text-slate-400 text-sm">
                            <div className="flex items-center justify-center gap-2 mb-2">
                              <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              <span>Processing transcript...</span>
                            </div>
                            <p className="text-xs text-gray-400">This may take a few moments</p>
                          </div>
                        )}
                      </div>
                    ) : (
                          <div className="text-slate-400 text-sm">
                        Ask questions about the video content below
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex-1 overflow-y-auto space-y-4 pb-4">
                    {chatMessages.map((msg, index) => (
                      <div
                        key={index}
                        className={`flex ${
                          msg.role === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg px-4 py-3 ${
                            msg.role === 'user'
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                          {msg.sources && msg.sources.length > 0 && (
                            <div className="mt-2 pt-2 border-t border-gray-300">
                              <p className="text-xs text-gray-600 font-semibold mb-1">Sources:</p>
                              {msg.sources.map((source, idx) => (
                                <p key={idx} className="text-xs text-gray-500 italic mt-1">
                                  "{source.substring(0, 100)}..."
                                </p>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                    {chatLoading && (
                      <div className="flex justify-start">
                          <div className="bg-slate-900 text-slate-100 rounded-lg px-4 py-3 border border-slate-800">
                          <div className="flex items-center gap-2">
                            <svg className="animate-spin h-4 w-4 text-slate-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <span className="text-sm">Thinking...</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Bottom Input */}
          <div className="border-t border-slate-800 p-4 bg-slate-950">
            <form onSubmit={handleAskQuestion} className="relative">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                disabled={!ingestionComplete || chatLoading}
                placeholder={
                  !ingestionComplete 
                    ? "Processing transcript..." 
                    : "Ask AI about this content. Need more details or a different view?"
                }
                className={`w-full pl-4 pr-12 py-3 text-sm border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent bg-slate-900 text-slate-100 placeholder:text-slate-500 ${
                  !ingestionComplete || chatLoading ? 'bg-slate-800 cursor-not-allowed' : ''
                }`}
              />
              <button
                type="submit"
                disabled={!ingestionComplete || chatLoading}
                className={`absolute right-3 top-1/2 -translate-y-1/2 ${
                  ingestionComplete && !chatLoading 
                    ? 'text-sky-400 hover:text-sky-300' 
                    : 'text-slate-500 cursor-not-allowed'
                }`}
              >
                <FiSend className="w-5 h-5" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResultsPage;
