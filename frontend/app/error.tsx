'use client';

import { useEffect } from 'react';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('[AI Factory] Unhandled error:', error);
  }, [error]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#05050a] text-[#f1f1f8] px-6">
      <div className="max-w-md w-full text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-[rgba(248,113,113,0.1)] border border-[rgba(248,113,113,0.3)] flex items-center justify-center mx-auto">
          <span className="text-2xl">Ã¢Å¡Â </span>
        </div>
        <h1 className="text-xl font-bold text-[#f87171]">Something went wrong</h1>
        <p className="text-sm text-[#8888aa] leading-relaxed">
          {error.message || 'An unexpected error occurred. The pipeline state has been preserved.'}
        </p>
        {error.digest && (
          <p className="text-micro font-mono text-[#6366f1] bg-[rgba(99,102,241,0.08)] px-3 py-1.5 rounded-lg">
            Error ID: {error.digest}
          </p>
        )}
        <button
          onClick={reset}
          className="inline-flex items-center gap-2 px-6 py-2.5 bg-[#6366f1] hover:bg-[#5254cc] text-white text-sm font-semibold rounded-xl transition-all"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
