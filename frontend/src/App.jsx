import { useState } from 'react';
import LandingPage from './components/LandingPage';
import ResultsPage from './components/ResultsPage';

function App() {
  const [videoUrl, setVideoUrl] = useState('');
  const [videoInfo, setVideoInfo] = useState(null);
  const [summary, setSummary] = useState('');
  const [transcript, setTranscript] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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
