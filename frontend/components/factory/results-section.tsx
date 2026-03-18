'use client';

import { useRef, useEffect, useState } from 'react';
import gsap from 'gsap';
import {
  CheckCircle2, RotateCcw, FileCode, Download, ThumbsUp,
  BarChart2, Layers, BookOpen, Sparkles, Star, ArrowRight,
  Trophy, TrendingUp, Zap,
} from 'lucide-react';
import { useFactory } from '@/lib/factory-store';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

// Ã¢â€â‚¬Ã¢â€â‚¬ Animated counter Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
function AnimatedNumber({ target, duration = 1.5, delay = 0 }: { target: number; duration?: number; delay?: number }) {
  const [display, setDisplay] = useState(0);
  const startRef = useRef<number | null>(null);

  useEffect(() => {
    const totalMs = duration * 1000;
    const delayMs = delay * 1000;

    const timeout = window.setTimeout(() => {
      const startTime = performance.now();
      const frame = (now: number) => {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / totalMs, 1);
        // ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        setDisplay(Math.round(eased * target));
        if (progress < 1) requestAnimationFrame(frame);
      };
      requestAnimationFrame(frame);
    }, delayMs);

    return () => clearTimeout(timeout);
  }, [target, duration, delay]);

  return <>{display}</>;
}

// Ã¢â€â‚¬Ã¢â€â‚¬ Score ring Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
function ScoreRing({ score, color }: { score: number; color: string }) {
  const circleRef  = useRef<SVGCircleElement>(null);
  const [filled, setFilled] = useState(false);
  const r = 52;
  const circ = 2 * Math.PI * r;

  useEffect(() => {
    setFilled(false);
    if (circleRef.current) {
      gsap.fromTo(circleRef.current,
        { strokeDashoffset: circ },
        { strokeDashoffset: circ - (score / 100) * circ, duration: 1.8, ease: 'power3.out', delay: 0.3,
          onComplete: () => setFilled(true) }
      );
    }
  }, [score, circ]);

  return (
    <div className={`relative w-36 h-36 mx-auto rounded-full transition-all duration-500${filled ? ' glow-pulse-anim' : ''}`}
      role="img" aria-label={`Specification score: ${score} out of 100`}>
      {/* Background ring */}
      <svg className="absolute inset-0 -rotate-90" width="144" height="144" viewBox="0 0 144 144">
        <circle cx="72" cy="72" r={r} fill="none" stroke="rgba(99,102,241,0.08)" strokeWidth="8" />
        <circle
          ref={circleRef}
          cx="72" cy="72" r={r}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={circ}
          style={{ filter: `drop-shadow(0 0 8px ${color}80)` }}
        />
      </svg>
      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="text-5xl font-black leading-none" style={{ color }}>
          <AnimatedNumber target={score} duration={1.6} delay={0.2} />
        </div>
        <div className="text-xs text-[#5a5a80] font-medium mt-0.5">/100</div>
      </div>
    </div>
  );
}

// Ã¢â€â‚¬Ã¢â€â‚¬ Confetti burst Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
function ConfettiDot({ color, delay }: { color: string; delay: number }) {
  const style = {
    '--x': `${(Math.random() - 0.5) * 200}px`,
    '--y': `${-(Math.random() * 120 + 40)}px`,
    '--r': `${Math.random() * 360}deg`,
    '--d': `${delay}s`,
    '--c': color,
    position: 'absolute' as const,
    left: '50%',
    top: '50%',
    width: Math.random() > 0.5 ? '6px' : '4px',
    height: Math.random() > 0.5 ? '6px' : '4px',
    borderRadius: Math.random() > 0.5 ? '50%' : '2px',
    background: color,
    animation: `confetti-fly 0.9s ease-out ${delay}s forwards`,
    opacity: 0,
  };
  return <div style={style} />;
}

export function ResultsSection() {
  const { state, resetFactory } = useFactory();
  const { pipeline } = state;
  const containerRef  = useRef<HTMLDivElement>(null);
  const heroRef       = useRef<HTMLDivElement>(null);
  const confettiRef   = useRef<HTMLDivElement>(null);
  const [showConfetti, setShowConfetti] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;
    const items = containerRef.current.querySelectorAll('.result-item');
    gsap.fromTo(items,
      { opacity: 0, y: 32, scale: 0.97 },
      { opacity: 1, y: 0, scale: 1, duration: 0.7, stagger: 0.12, ease: 'power3.out', delay: 0.1 }
    );
    // Trigger confetti
    setTimeout(() => setShowConfetti(true), 200);
    setTimeout(() => setShowConfetti(false), 2500);
  }, []);

  if (!pipeline) return null;

  const pmPhase      = pipeline.phases.find(p => p.phase === 7);
  const pmEval       = pmPhase?.pm_evaluation;
  const outputFiles  = pipeline.phases.find(p => p.phase === 8)?.output_files ?? [];
  const totalStories = pipeline.phases.find(p => p.phase === 2)?.user_stories?.length ?? 0;
  const approved     = pmEval?.status === 'APPROVED';

  const score = pmEval?.score ?? 0;
  const scoreColor =
    score >= 90 ? '#10b981' :
    score >= 80 ? '#6366f1' :
    score >= 70 ? '#fbbf24' : '#f87171';

  const CONFETTI_COLORS = ['#6366f1', '#8b5cf6', '#10b981', '#22d3ee', '#fbbf24', '#f87171', '#a78bfa'];

  return (
    <div ref={containerRef} className="space-y-5">
      {/* Ã¢â€â‚¬Ã¢â€â‚¬ Hero card Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
      <div ref={heroRef} className="result-item relative overflow-hidden rounded-3xl"
        style={{ background: 'rgba(8,8,18,0.95)', border: '1px solid rgba(16,185,129,0.2)', boxShadow: '0 0 0 1px rgba(16,185,129,0.06), 0 24px 80px rgba(0,0,0,0.5)' }}>

        {/* Ambient background */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_60%,rgba(16,185,129,0.07),transparent)]" />
        <div className="absolute inset-0 grid-bg-fine opacity-30" />
        <div className="absolute top-0 left-0 right-0 h-px"
          style={{ background: 'linear-gradient(90deg, transparent, rgba(16,185,129,0.5), rgba(99,102,241,0.3), transparent)' }} />

        {/* Confetti burst */}
        {showConfetti && (
          <div ref={confettiRef} className="absolute inset-0 overflow-hidden pointer-events-none" style={{ zIndex: 20 }}>
            <style>{`
              @keyframes confetti-fly {
                0% { transform: translate(-50%, -50%) rotate(0deg) scale(1); opacity: 1; }
                100% { transform: translate(calc(-50% + var(--x)), calc(-50% + var(--y))) rotate(var(--r)) scale(0); opacity: 0; }
              }
            `}</style>
            {Array.from({ length: 30 }).map((_, i) => (
              <ConfettiDot key={i} color={CONFETTI_COLORS[i % CONFETTI_COLORS.length]} delay={Math.random() * 0.4} />
            ))}
          </div>
        )}

        <div className="relative z-10 py-16 px-8 text-center">
          {/* Trophy icon */}
          <div className="flex items-center justify-center mb-8">
            <div className="relative">
              <div className="w-20 h-20 rounded-3xl flex items-center justify-center"
                style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)', boxShadow: '0 0 40px rgba(16,185,129,0.2), 0 0 80px rgba(16,185,129,0.08)' }}>
                <Trophy className="w-10 h-10 text-[#10b981]" />
              </div>
              {/* Orbiting rings */}
              <div className="absolute inset-0 rounded-3xl border border-[rgba(16,185,129,0.15)] scale-125 ping-ring" />
              <div className="absolute inset-0 rounded-3xl border border-[rgba(16,185,129,0.08)] scale-150" style={{ animation: 'ping-ring 1.8s ease-out 0.4s infinite' }} />
              {/* Badge */}
              <div className="absolute -top-2 -right-2 w-7 h-7 rounded-full flex items-center justify-center"
                style={{ background: 'rgba(251,191,36,0.12)', border: '1px solid rgba(251,191,36,0.3)', boxShadow: '0 0 12px rgba(251,191,36,0.3)' }}>
                <Sparkles className="w-3.5 h-3.5 text-[#fbbf24]" />
              </div>
            </div>
          </div>

          <div className="text-2xs font-black text-[#10b981] uppercase tracking-[0.2em] mb-3">
            All 8 phases complete
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-[#f0f0fc] mb-3 leading-tight tracking-tighter">
            Specification Complete
          </h2>
          <p className="text-[#5a5a80] mb-12 text-sm max-w-md mx-auto">
            Your MVP specification is ready. Take it to your engineers.
          </p>

          {/* Score ring */}
          <div className="flex flex-col items-center mb-6">
            <ScoreRing score={score} color={scoreColor} />
            <div className="mt-4 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold"
              style={approved ? {
                background: 'rgba(16,185,129,0.1)', color: '#10b981',
                border: '1px solid rgba(16,185,129,0.25)',
                boxShadow: '0 0 20px rgba(16,185,129,0.15)',
              } : {
                background: 'rgba(248,113,113,0.1)', color: '#f87171',
                border: '1px solid rgba(248,113,113,0.25)',
              }}>
              {approved ? <ThumbsUp className="w-4 h-4" /> : null}
              {pmEval?.status ?? 'APPROVED'}
            </div>
          </div>
        </div>
      </div>

      {/* Ã¢â€â‚¬Ã¢â€â‚¬ Metrics row Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
      <div className="result-item grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { icon: <BarChart2 className="w-5 h-5" />, label: 'PM Score',      value: pmEval?.score ?? 0,       sub: '/100',         color: scoreColor,  animated: true },
          { icon: <Layers className="w-5 h-5" />,    label: 'User Stories',  value: totalStories,             sub: 'generated',   color: '#8b5cf6',   animated: true },
          { icon: <RotateCcw className="w-5 h-5" />, label: 'Cycles Run',    value: pipeline.current_cycle,  sub: 'iteration(s)', color: '#fbbf24',  animated: false },
          { icon: <BookOpen className="w-5 h-5" />,  label: 'Rules Learned', value: pipeline.evolution.total_rules, sub: 'in playbooks', color: '#10b981', animated: true },
        ].map(({ icon, label, value, sub, color, animated }, idx) => (
          <div key={label}
            className="relative p-5 rounded-2xl text-center overflow-hidden group transition-all duration-300 hover:translate-y-[-2px]"
            style={{ background: 'rgba(8,8,18,0.9)', border: '1px solid rgba(99,102,241,0.1)' }}
            onMouseEnter={e => (e.currentTarget.style.borderColor = `${color}30`)}
            onMouseLeave={e => (e.currentTarget.style.borderColor = 'rgba(99,102,241,0.1)')}>
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_0%,rgba(99,102,241,0.04),transparent)]" />
            <div className="relative z-10">
              <div className="flex justify-center mb-3 transition-transform group-hover:scale-110" style={{ color }}>{icon}</div>
              <div className="text-3xl font-black mb-1 leading-none" style={{ color }}>
                {animated ? <AnimatedNumber target={value} duration={1.4} delay={idx * 0.15} /> : value}
              </div>
              <div className="text-micro text-[#5a5a80]">{sub}</div>
              <div className="text-micro text-[#353560] uppercase tracking-widest mt-1 font-bold">{label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Ã¢â€â‚¬Ã¢â€â‚¬ Score breakdown Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
      {pmEval?.breakdown && (
        <div className="result-item p-6 rounded-2xl"
          style={{ background: 'rgba(8,8,18,0.9)', border: '1px solid rgba(99,102,241,0.1)' }}>
          <div className="flex items-center gap-2.5 mb-5">
            <div className="w-8 h-8 rounded-xl flex items-center justify-center"
              style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)' }}>
              <Star className="w-4 h-4 text-[#818cf8]" />
            </div>
            <div className="text-sm font-bold text-[#f0f0fc]">Score Breakdown</div>
          </div>
          <div className="space-y-3.5">
            {Object.entries(pmEval.breakdown).map(([key, val], idx) => {
              const maxes: Record<string, number> = { requirements: 30, architecture: 25, completeness: 20, qa_compliance: 15, security: 10 };
              const max = maxes[key] ?? 30;
              const pct = (val / max) * 100;
              const barColor = pct >= 80 ? '#10b981' : pct >= 55 ? '#6366f1' : '#fbbf24';
              return (
                <div key={key} className="flex items-center gap-3 group">
                  <span className="text-xs text-[#5a5a80] capitalize w-28 flex-shrink-0 font-medium group-hover:text-[#a0a0c0] transition-colors">
                    {key.replace('_', ' ')}
                  </span>
                  <div className="flex-1 h-2 rounded-full overflow-hidden"
                    style={{ background: 'rgba(99,102,241,0.07)' }}>
                    <BarAnim pct={pct} color={barColor} delay={0.4 + idx * 0.1} />
                  </div>
                  <span className="text-xs font-bold w-12 text-right tabular-nums transition-colors"
                    style={{ color: barColor }}>{val}/{max}</span>
                </div>
              );
            })}
          </div>

          {/* Strengths */}
          {pmEval.strengths?.length > 0 && (
            <div className="mt-5 pt-4 border-t" style={{ borderColor: 'rgba(99,102,241,0.06)' }}>
              <div className="text-micro font-black text-[#10b981] uppercase tracking-widest mb-3 flex items-center gap-1.5">
                <TrendingUp className="w-3 h-3" /> Strengths
              </div>
              <div className="space-y-1.5">
                {pmEval.strengths.map((s, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-[#5a5a80]">
                    <CheckCircle2 className="w-3 h-3 text-[#10b981] mt-0.5 flex-shrink-0" />{s}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Ã¢â€â‚¬Ã¢â€â‚¬ Generated files Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
      {outputFiles.length > 0 && (
        <div className="result-item">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl flex items-center justify-center"
                style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)' }}>
                <FileCode className="w-4 h-4 text-[#10b981]" />
              </div>
              <span className="text-sm font-bold text-[#f0f0fc]">Generated Files</span>
              <span className="text-micro px-2 py-0.5 rounded-full font-black"
                style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', color: '#10b981' }}>
                {outputFiles.length} files
              </span>
            </div>
            <button
              onClick={async () => {
                if (!pipeline?.run_id) return;
                try {
                  const res = await fetch(`${API_BASE}/api/pipeline/${pipeline.run_id}/download`);
                  if (!res.ok) throw new Error(`Download failed (${res.status})`);
                  const blob = await res.blob();
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `ai-factory-${pipeline.run_id}.zip`;
                  a.click();
                  URL.revokeObjectURL(url);
                } catch {
                  alert('Download failed Ã¢â‚¬â€ please try again.');
                }
              }}
              className="group flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all"
              style={{ background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.18)', color: '#10b981' }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(16,185,129,0.12)'; e.currentTarget.style.boxShadow = '0 0 16px rgba(16,185,129,0.15)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'rgba(16,185,129,0.06)'; e.currentTarget.style.boxShadow = 'none'; }}>
              <Download className="w-3.5 h-3.5 transition-transform group-hover:-translate-y-0.5" />
              Download all
            </button>
          </div>

          <div className="grid sm:grid-cols-2 gap-2.5">
            {outputFiles.map((file, i) => {
              const colors = ['#6366f1','#8b5cf6','#a78bfa','#22d3ee','#10b981','#6366f1','#f87171','#fbbf24'];
              const c = colors[i % colors.length];
              return (
                <div key={file.filename}
                  className="group flex items-center gap-3.5 p-4 rounded-2xl overflow-hidden relative transition-all duration-200"
                  style={{ background: 'rgba(8,8,18,0.9)', border: '1px solid rgba(99,102,241,0.08)' }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = `${c}35`; e.currentTarget.style.background = `${c}05`; }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(99,102,241,0.08)'; e.currentTarget.style.background = 'rgba(8,8,18,0.9)'; }}>
                  {/* Bottom accent */}
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
                    style={{ background: `linear-gradient(90deg, transparent, ${c}50, transparent)` }} />
                  <div className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 transition-transform group-hover:scale-110"
                    style={{ background: `${c}10`, border: `1px solid ${c}25` }}>
                    <FileCode className="w-5 h-5" style={{ color: c }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-bold text-[#f0f0fc] truncate">{file.name}</div>
                    <div className="text-micro font-mono truncate mt-0.5" style={{ color: `${c}aa` }}>{file.filename}</div>
                    {file.description && (
                      <div className="text-micro text-[#5a5a80] truncate mt-0.5">{file.description}</div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Ã¢â€â‚¬Ã¢â€â‚¬ Next project CTA Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
      <div className="result-item relative p-6 rounded-2xl overflow-hidden"
        style={{ background: 'rgba(8,8,18,0.9)', border: '1px solid rgba(99,102,241,0.12)' }}>
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_80%_at_100%_50%,rgba(99,102,241,0.06),transparent)]" />
        <div className="absolute top-0 left-0 right-0 h-px"
          style={{ background: 'linear-gradient(90deg, transparent, rgba(99,102,241,0.3), transparent)' }} />
        <div className="relative z-10 flex flex-col sm:flex-row items-start sm:items-center gap-5">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1.5">
              <Zap className="w-4 h-4 text-[#6366f1]" />
              <h3 className="font-bold text-[#f0f0fc] text-sm">Ready for your next project?</h3>
            </div>
            <p className="text-xs text-[#5a5a80] leading-relaxed">
              The factory has learned from this run.
              Start your next BRD to see the improvement Ã¢â‚¬â€{' '}
              <strong className="text-[#a0a0c0]">{pipeline.evolution.total_rules} rules</strong> now live in the playbooks.
            </p>
          </div>
          <button
            onClick={resetFactory}
            className="group flex items-center gap-2.5 px-6 py-3 text-white text-sm font-bold rounded-xl transition-all flex-shrink-0 whitespace-nowrap relative overflow-hidden"
            style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', boxShadow: '0 4px 20px rgba(99,102,241,0.35)' }}
            onMouseEnter={e => (e.currentTarget.style.boxShadow = '0 8px 40px rgba(99,102,241,0.55)')}
            onMouseLeave={e => (e.currentTarget.style.boxShadow = '0 4px 20px rgba(99,102,241,0.35)')}>
            <span className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity"
              style={{ background: 'rgba(255,255,255,0.08)' }} />
            <RotateCcw className="w-4 h-4" />
            Start New Project
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </button>
        </div>
      </div>
    </div>
  );
}

// Ã¢â€â‚¬Ã¢â€â‚¬ Animated bar (for score breakdown) Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
function BarAnim({ pct, color, delay = 0 }: { pct: number; color: string; delay?: number }) {
  const barRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (barRef.current) {
      gsap.fromTo(barRef.current,
        { scaleX: 0 },
        { scaleX: pct / 100, duration: 1.3, ease: 'power3.out', delay }
      );
    }
  }, [pct, delay]);
  return (
    <div ref={barRef} className="h-full rounded-full"
      style={{ background: `linear-gradient(90deg, ${color}, ${color}cc)`, transformOrigin: '0 0', transform: 'scaleX(0)', boxShadow: `0 0 6px ${color}50` }} />
  );
}
