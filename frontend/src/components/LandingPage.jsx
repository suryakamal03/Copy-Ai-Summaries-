import { useState } from 'react';
import { FiLink } from 'react-icons/fi';

function LandingPage({ onGenerateSummary, loading, error }) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim() && !loading) {
      onGenerateSummary(url);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-4">
      {/* Trusted by text */}
      <p className="text-gray-500 text-base mb-8">
        Trusted by 300,000+ professionals
      </p>

      {/* YouTube Icon */}
      <div className="mb-6">
        <div className="w-20 h-20 flex items-center justify-center">
          <svg className="w-20 h-20 text-red-600" viewBox="0 0 90 90" fill="none">
            <rect x="10" y="25" width="70" height="45" rx="8" stroke="currentColor" strokeWidth="3" fill="none"/>
            <path d="M38 35 L58 45 L38 55 Z" fill="currentColor"/>
          </svg>
        </div>
      </div>

      {/* Title */}
      <h1 className="text-5xl font-bold text-gray-900 mb-4">
        Youtube Summarizer
      </h1>

      {/* Subtitle */}
      <p className="text-gray-600 text-lg text-center max-w-2xl mb-12">
        Convert YouTube videos into clear, concise summaries with AI<br />
        precision. Get the key points without watching the entire video.
      </p>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="w-full max-w-3xl">
        {/* URL Input */}
        <div className="relative mb-6">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
            <FiLink className="w-5 h-5" />
          </div>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste your YouTube video URL here"
            disabled={loading}
            className="w-full pl-12 pr-4 py-4 text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Generate Button */}
        <button
          type="submit"
          disabled={loading || !url.trim()}
          className="w-full bg-gray-600 hover:bg-gray-700 text-white font-medium py-4 rounded-lg transition-colors duration-200 text-base disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating Summary...
            </>
          ) : (
            'Generate Summary'
          )}
        </button>
      </form>
    </div>
  );
}

export default LandingPage;
