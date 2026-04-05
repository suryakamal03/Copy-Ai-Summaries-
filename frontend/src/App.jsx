import { useEffect, useState } from 'react';
import LandingPage from './components/LandingPage';
import ResultsPage from './components/ResultsPage';

const APP_STATE_KEY = 'youtube_summarizer_app_state_v1';

const loadSavedState = () => {
  const fallback = {
    videoUrl: '',
    videoInfo: null,
    summary: '',
    transcript: '',
    showResults: false,
  };

  try {
    const raw = localStorage.getItem(APP_STATE_KEY);
    if (!raw) return fallback;
    const parsed = JSON.parse(raw);
    return {
      videoUrl: parsed.videoUrl || '',
      videoInfo: parsed.videoInfo || null,
      summary: parsed.summary || '',
      transcript: parsed.transcript || '',
      showResults: Boolean(parsed.showResults),
    };
  } catch {
    return fallback;
  }
};

function App() {
  const initialState = loadSavedState();
  const [videoUrl, setVideoUrl] = useState(initialState.videoUrl);
  const [videoInfo, setVideoInfo] = useState(initialState.videoInfo);
  const [summary, setSummary] = useState(initialState.summary);
  const [transcript, setTranscript] = useState(initialState.transcript);
  const [showResults, setShowResults] = useState(initialState.showResults);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const stateToSave = {
      videoUrl,
      videoInfo,
      summary,
      transcript,
      showResults,
    };
    localStorage.setItem(APP_STATE_KEY, JSON.stringify(stateToSave));
  }, [videoUrl, videoInfo, summary, transcript, showResults]);

  const handleGenerateSummary = async (url, summaryType = 'detailed') => {
    setLoading(true);
    setError('');
    
    try {
      // Get video info
      const infoResponse = await fetch('http://localhost:5000/api/video-info', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!infoResponse.ok) {
        const errorData = await infoResponse.json();
        throw new Error(errorData.error || 'Failed to fetch video info');
      }

      const info = await infoResponse.json();
      setVideoInfo(info);

      // Get summary
      const summaryResponse = await fetch('http://localhost:5000/api/summary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, summaryType }),
      });

      if (!summaryResponse.ok) {
        const errorData = await summaryResponse.json();
        throw new Error(errorData.error || 'Failed to generate summary');
      }

      const summaryData = await summaryResponse.json();
      setSummary(summaryData.summary);

      // Get transcript
      const transcriptResponse = await fetch('http://localhost:5000/api/transcript', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (transcriptResponse.ok) {
        const transcriptData = await transcriptResponse.json();
        setTranscript(transcriptData.transcript);
      }

      setVideoUrl(url);
      setShowResults(true);
    } catch (err) {
      setError(err.message || 'An error occurred');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleNewVideo = () => {
    setVideoUrl('');
    setVideoInfo(null);
    setSummary('');
    setTranscript('');
    setShowResults(false);
    setError('');
    localStorage.removeItem(APP_STATE_KEY);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {!showResults ? (
        <LandingPage 
          onGenerateSummary={handleGenerateSummary}
          loading={loading}
          error={error}
        />
      ) : (
        <ResultsPage 
          videoUrl={videoUrl}
          videoInfo={videoInfo}
          summary={summary}
          transcript={transcript}
          onNewVideo={handleNewVideo}
          onRegenerateSummary={handleGenerateSummary}
        />
      )}
    </div>
  );
}

export default App;
