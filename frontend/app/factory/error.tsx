'use client';

import { useEffect } from 'react';

export default function FactoryError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('[Factory] Error:', error);
  }, [error]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#05050a] text-[#f1f1f8] px-6">
      <div className="max-w-md w-full text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-[rgba(248,113,113,0.1)] border border-[rgba(248,113,113,0.3)] flex items-center justify-center mx-auto">
          <span className="text-2xl">⚠</span>
        </div>
        <h1 className="text-xl font-bold text-[#f87171]">Factory error</h1>
        <p className="text-sm text-[#8888aa] leading-relaxed">
          {error.message || 'The factory pipeline encountered an unexpected problem.'}
        </p>
        <div className="flex items-center justify-center gap-3">
          <button
            onClick={reset}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#6366f1] hover:bg-[#5254cc] text-white text-sm font-semibold rounded-xl transition-all"
          >
            Restart factory
          </button>
        </div>
      </div>
    </div>
  );
}
