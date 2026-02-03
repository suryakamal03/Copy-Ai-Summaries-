import { useState } from 'react';
import { FiRefreshCw, FiDownload, FiGlobe, FiSend } from 'react-icons/fi';

function ResultsPage({ videoUrl, videoInfo, summary, transcript, onNewVideo, onRegenerateSummary }) {
  const [activeTab, setActiveTab] = useState('output');
  const [question, setQuestion] = useState('');
  const [summaryType, setSummaryType] = useState('detailed');
  const [currentSummary, setCurrentSummary] = useState(summary);
  const [loading, setLoading] = useState(false);
  const [highlights, setHighlights] = useState([]);
  const [highlightsLoading, setHighlightsLoading] = useState(false);

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

  const handleAskQuestion = (e) => {
    e.preventDefault();
    // Handle question submission
    console.log('Question:', question);
    setQuestion('');
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
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900 truncate max-w-2xl">
            {videoTitle}
          </h1>
          <div className="flex items-center gap-3">
            <button
              onClick={onNewVideo}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <FiRefreshCw className="w-4 h-4" />
              <span className="text-sm font-medium">New Video</span>
            </button>
            <button className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              <FiDownload className="w-4 h-4" />
              <span className="text-sm font-medium">Export</span>
            </button>
            <button className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              <FiGlobe className="w-4 h-4" />
              <span className="text-sm font-medium">Auto Detect</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-73px)]">
        {/* Left Panel - Video */}
        <div className="w-[52%] border-r border-gray-200 p-6 flex flex-col">
          {/* Video Player */}
          <div className="bg-black rounded-lg overflow-hidden mb-4">
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
            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-6 text-sm"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
            </svg>
            View on YouTube
          </a>

          {/* Video Script Section */}
          <div className="flex-1 bg-gray-50 rounded-lg p-4 overflow-hidden flex flex-col">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-900">Video Script</h3>
              <button className="flex items-center gap-1.5 text-sm text-gray-700 hover:text-gray-900">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy
              </button>
            </div>
            <div className="flex-1 overflow-y-auto text-sm text-gray-600 space-y-2">
              {transcriptChunks.length > 0 ? (
                transcriptChunks.map((chunk, idx) => (
                  <p key={idx} className="flex gap-2">
                    <span className="text-gray-400 font-mono text-xs">{chunk.time}</span>
                    <span>{chunk.text}</span>
                  </p>
                ))
              ) : (
                <p className="text-gray-400 italic">No transcript available</p>
              )}
            </div>
          </div>
        </div>

        {/* Right Panel - Output */}
        <div className="w-[48%] flex flex-col">
          {/* Tabs */}
          <div className="border-b border-gray-200">
            <div className="flex">
              {['Output', 'Highlights', 'Mind Map', 'Chat'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => handleTabChange(tab.toLowerCase().replace(' ', '-'))}
                  className={`px-6 py-3.5 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.toLowerCase().replace(' ', '-')
                      ? 'border-gray-900 text-gray-900'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto p-6">
            {activeTab === 'output' && (
              <div>
                {/* Summary Type Selector */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Summary Type:
                  </label>
                  <select
                    value={summaryType}
                    onChange={handleSummaryTypeChange}
                    disabled={loading}
                    className="block w-full max-w-xs px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed text-sm"
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
                      <svg className="animate-spin h-8 w-8 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <p className="text-sm text-gray-600">Generating summary...</p>
                    </div>
                  </div>
                ) : (
                  <div className="text-gray-800 text-[15px] leading-relaxed whitespace-pre-wrap">
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
                      <svg className="animate-spin h-8 w-8 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <p className="text-sm text-gray-600">Generating highlights...</p>
                    </div>
                  </div>
                ) : highlights.length > 0 ? (
                  <div className="space-y-6">
                    {highlights.map((highlight, index) => (
                      <div key={index} className="border-l-4 border-blue-500 pl-4">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-blue-600 font-mono text-sm font-semibold">
                            {highlight.timestamp}
                          </span>
                          <button className="ml-auto p-1 text-gray-400 hover:text-gray-600">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                          </button>
                        </div>
                        <p className="text-gray-800 text-[15px] leading-relaxed">
                          {highlight.description}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    No highlights available
                  </div>
                )}
              </div>
            )}
            {activeTab === 'mind-map' && (
              <div className="text-gray-600 text-sm">Mind Map feature coming soon...</div>
            )}
            {activeTab === 'chat' && (
              <div className="text-gray-600 text-sm">Chat feature coming soon...</div>
            )}
          </div>

          {/* Bottom Input */}
          <div className="border-t border-gray-200 p-4">
            <form onSubmit={handleAskQuestion} className="relative">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask AI about this content. Need more details or a different view?"
                className="w-full pl-4 pr-12 py-3 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="submit"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-blue-600 hover:text-blue-700"
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
