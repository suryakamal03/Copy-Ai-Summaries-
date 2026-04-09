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
    <div className="relative min-h-screen overflow-hidden bg-[#06111f] text-slate-100">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.18),_transparent_32%),radial-gradient(circle_at_80%_20%,_rgba(14,165,233,0.14),_transparent_28%),linear-gradient(180deg,_#06111f_0%,_#081a31_48%,_#06111f_100%)]" />

      <div className="relative flex min-h-screen flex-col items-center justify-center px-4 py-16">
        <div className="w-full max-w-3xl px-4 py-8 md:px-6 md:py-10">
          <div className="mb-6 flex justify-center">
            <svg className="h-12 w-12 text-red-500/90" viewBox="0 0 90 90" fill="none">
              <rect x="10" y="25" width="70" height="45" rx="8" stroke="currentColor" strokeWidth="3" fill="none" />
              <path d="M38 35 L58 45 L38 55 Z" fill="currentColor" />
            </svg>
          </div>

          <h1 className="mb-4 text-center text-5xl font-semibold tracking-tight text-white md:text-6xl">
            Youtube Summarizer
          </h1>

          <p className="mx-auto mb-10 max-w-xl text-center text-base leading-7 text-slate-300 md:text-lg">
            Convert YouTube videos into clear, concise summaries with AI precision.
            Get the key points without watching the entire video.
          </p>

          <form onSubmit={handleSubmit} className="mx-auto w-full max-w-3xl">
            <div className="relative mb-6">
              <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
                <FiLink className="h-5 w-5" />
              </div>
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Paste your YouTube video URL here"
                disabled={loading}
                className="w-full rounded-2xl border border-slate-700 bg-slate-950/90 py-4 pl-12 pr-4 text-base text-slate-100 shadow-inner shadow-black/20 placeholder:text-slate-500 focus:border-sky-400 focus:outline-none focus:ring-2 focus:ring-sky-500/40 disabled:cursor-not-allowed disabled:bg-slate-900"
              />
            </div>

            {error && (
              <div className="mb-4 rounded-xl border border-red-400/30 bg-red-500/10 p-3 text-sm text-red-200">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !url.trim()}
              className="flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-sky-500 to-blue-600 py-4 text-base font-semibold text-white shadow-lg shadow-blue-950/30 transition hover:from-sky-400 hover:to-blue-500 disabled:cursor-not-allowed disabled:from-slate-600 disabled:to-slate-700"
            >
              {loading ? (
                <>
                  <svg className="h-5 w-5 animate-spin text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
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
      </div>
    </div>
  );
}

export default LandingPage;
