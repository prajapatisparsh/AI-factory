'use client';

import { useRef, useEffect, useState } from 'react';
import Link from 'next/link';
import gsap from 'gsap';
import { ArrowLeft, Zap, LayoutList, CheckSquare } from 'lucide-react';
import { FactoryProvider, useFactory } from '@/lib/factory-store';
import { InputSection } from '@/components/factory/input-section';
import { PipelineView } from '@/components/factory/pipeline-view';
import { AmbientPanel } from '@/components/factory/ambient-panel';
import { ResultsSection } from '@/components/factory/results-section';

// Ã¢â€â‚¬Ã¢â€â‚¬ Inner page (needs access to useFactory context) Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
function FactoryPageInner() {
  const { state } = useFactory();
  const { stage } = state;

  const inputRef = useRef<HTMLDivElement>(null);
  const pipelineRef = useRef<HTMLDivElement>(null);
  const [hasTransitioned, setHasTransitioned] = useState(false);
  // Which view to show once complete: results summary or the full pipeline log
  const [completeView, setCompleteView] = useState<'results' | 'pipeline'>('results');

  // Stage transition: idle -> running
  useEffect(() => {
    if ((stage === 'running' || stage === 'paused' || stage === 'complete') && !hasTransitioned) {
      setHasTransitioned(true);

      // Animate pipeline in
      if (pipelineRef.current) {
        gsap.fromTo(
          pipelineRef.current,
          { opacity: 0, y: 32 },
          { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out', delay: 0.1 }
        );
      }
    }

    if (stage === 'idle') {
      setHasTransitioned(false);
      setCompleteView('results');
    }
  }, [stage, hasTransitioned]);

  const showPipeline = stage === 'running' || stage === 'paused' || stage === 'complete';

  return (
    <div className="min-h-screen bg-[#05050a] text-[#f1f1f8]">
      {/* Ã¢â€â‚¬Ã¢â€â‚¬ Nav bar Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
      <nav className="fixed top-0 left-0 right-0 z-50 h-16 flex items-center px-6 border-b border-[rgba(99,102,241,0.08)] bg-[rgba(5,5,10,0.85)] backdrop-blur-md">
        <div className="flex items-center gap-4 flex-1">
          <Link
            href="/"
            className="flex items-center gap-1.5 text-[#8888aa] hover:text-[#c8c8e8] transition-colors text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="hidden sm:inline">Back</span>
          </Link>

          <div className="h-4 w-px bg-[rgba(99,102,241,0.2)]" />

          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-[#6366f1]" />
            <span className="text-sm font-semibold text-[#f1f1f8]">The AI Factory</span>
          </div>

          {/* Stage badge */}
          {stage !== 'idle' && (
            <div className={`ml-2 text-micro font-semibold px-2 py-0.5 rounded-full ${
              stage === 'running'
                ? 'bg-[rgba(99,102,241,0.15)] text-[#818cf8] border border-[rgba(99,102,241,0.3)]'
                : stage === 'paused'
                ? 'bg-[rgba(251,191,36,0.12)] text-[#fbbf24] border border-[rgba(251,191,36,0.3)]'
                : 'bg-[rgba(16,185,129,0.12)] text-[#10b981] border border-[rgba(16,185,129,0.3)]'
            }`}>
              {stage === 'running' ? 'RUNNING' : stage === 'paused' ? 'PAUSED' : 'COMPLETE'}
            </div>
          )}

          {/* Results / Pipeline Log toggle - only visible after completion */}
          {stage === 'complete' && (
            <div className="ml-4 flex items-center gap-1 p-1 rounded-lg bg-[rgba(99,102,241,0.08)] border border-[rgba(99,102,241,0.15)]">
              <button
                onClick={() => setCompleteView('results')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-all ${
                  completeView === 'results'
                    ? 'bg-[#6366f1] text-white shadow-sm'
                    : 'text-[#8888aa] hover:text-[#c8c8e8]'
                }`}
              >
                <CheckSquare className="w-3 h-3" />
                Results
              </button>
              <button
                onClick={() => setCompleteView('pipeline')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-all ${
                  completeView === 'pipeline'
                    ? 'bg-[#6366f1] text-white shadow-sm'
                    : 'text-[#8888aa] hover:text-[#c8c8e8]'
                }`}
              >
                <LayoutList className="w-3 h-3" />
                Pipeline Log
              </button>
            </div>
          )}
        </div>

        {/* Mode badge */}
        <div className="flex items-center gap-2">
          <span className="text-micro text-[#8888aa] uppercase tracking-wider">
            {state.mode === 'auto' ? 'Auto Mode' : 'Guided Mode'}
          </span>
        </div>
      </nav>

      {/* Ã¢â€â‚¬Ã¢â€â‚¬ Main content Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
      <main className="pt-16">
        {/* IDLE: full-screen input */}
        {stage === 'idle' && (
          <div ref={inputRef} className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-6">
            <div className="w-full max-w-2xl">
              <InputSection />
            </div>
          </div>
        )}

        {/* RUNNING / PAUSED / COMPLETE: pipeline + ambient sidebar */}
        {showPipeline && (
          <div ref={pipelineRef} className="opacity-0">
            <div className="max-w-screen-xl mx-auto px-4 sm:px-6 py-8">
              <div className="flex gap-6">
                {/* Main content */}
                <div className="flex-1 min-w-0">
                  {stage === 'complete' ? (
                    completeView === 'results' ? <ResultsSection /> : <PipelineView />
                  ) : (
                    <PipelineView />
                  )}
                </div>

                {/* Ambient sidebar */}
                <div className="hidden lg:block w-72 xl:w-80 flex-shrink-0">
                  <AmbientPanel />
                </div>
              </div>

              {/* Mobile ambient (bottom, collapsed) */}
              <div className="lg:hidden mt-6">
                <details className="rounded-xl border border-[rgba(99,102,241,0.15)] bg-[#0d0d18]">
                  <summary className="px-4 py-3 text-sm font-semibold text-[#c8c8e8] cursor-pointer flex items-center gap-2">
                    <span>Evolution & Activity</span>
                  </summary>
                  <div className="px-4 pb-4">
                    <AmbientPanel />
                  </div>
                </details>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Subtle grid background */}
      {stage === 'idle' && (
        <div className="fixed inset-0 grid-bg pointer-events-none" style={{ zIndex: 0 }} />
      )}
    </div>
  );
}

// Ã¢â€â‚¬Ã¢â€â‚¬ Export: wrap in provider Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
export default function FactoryPage() {
  return (
    <FactoryProvider>
      <FactoryPageInner />
    </FactoryProvider>
  );
}
