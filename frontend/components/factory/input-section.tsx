'use client';

import { useRef, useCallback, useState } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import {
  Upload, FileText, Zap, Brain, AlertCircle, X, Play,
  ArrowRight, CheckCircle2, FileCode, Sparkles,
} from 'lucide-react';
import { useFactory } from '@/lib/factory-store';
import type { PipelineMode } from '@/lib/types';

// Ã¢â€â‚¬Ã¢â€â‚¬ Constants Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

// Ã¢â€â‚¬Ã¢â€â‚¬ Animated placeholder strings for textarea Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
const PLACEHOLDERS = [
  'A SaaS platform for freelancers to track invoices and clients...',
  'An e-commerce marketplace for handmade goods with seller analytics...',
  'A real-time collaboration tool for remote engineering teams...',
  'A mobile app for local food pickup and restaurant discovery...',
];

export function InputSection() {
  const { state, dispatch, startPipeline, resumePipeline, resetFactory } = useFactory();
  const containerRef  = useRef<HTMLDivElement>(null);
  const fileInputRef  = useRef<HTMLInputElement>(null);
  const dropZoneRef   = useRef<HTMLDivElement>(null);
  const launchBtnRef  = useRef<HTMLButtonElement>(null);
  const [isDragging, setIsDragging]   = useState(false);
  const [showBanner, setShowBanner]   = useState(true);
  const [fileError, setFileError]     = useState<string | null>(null);
  const [placeholderIdx] = useState(() => Math.floor(Math.random() * PLACEHOLDERS.length));

  /* Ã¢â€â‚¬Ã¢â€â‚¬ Entrance Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
  useGSAP(() => {
    const els = containerRef.current?.querySelectorAll('.animate-in');
    if (!els) return;
    gsap.fromTo(els,
      { y: 28, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.7, stagger: 0.1, ease: 'power3.out', delay: 0.1 }
    );
  }, { scope: containerRef });

  /* Ã¢â€â‚¬Ã¢â€â‚¬ File drop spring Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
  const animateDrop = useCallback(() => {
    if (!dropZoneRef.current) return;
    gsap.fromTo(dropZoneRef.current,
      { scale: 0.96 },
      { scale: 1, duration: 0.5, ease: 'elastic.out(1,0.4)' }
    );
  }, []);

  /* Ã¢â€â‚¬Ã¢â€â‚¬ Launch button bounce Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
  const animateLaunch = useCallback(() => {
    if (!launchBtnRef.current) return;
    gsap.fromTo(launchBtnRef.current,
      { scale: 0.97 },
      { scale: 1, duration: 0.4, ease: 'elastic.out(1,0.5)' }
    );
  }, []);

  /* Ã¢â€â‚¬Ã¢â€â‚¬ Drag handlers Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
  const hasText  = state.input_text.trim().length > 0;
  const hasFile  = state.input_file !== null;
  const canStart = state.input_text.trim().length > 10 || hasFile;

  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      if (file.size > MAX_FILE_SIZE) {
        setFileError(`File too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Max 10 MB allowed.`);
        return;
      }
      setFileError(null);
      dispatch({ type: 'SET_INPUT_FILE', file });
      dispatch({ type: 'SET_INPUT_TEXT', text: '' });
      animateDrop();
    }
  }, [dispatch, animateDrop]);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!hasText) setIsDragging(true);
  }, [hasText]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > MAX_FILE_SIZE) {
        setFileError(`File too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Max 10 MB allowed.`);
        e.target.value = '';
        return;
      }
      setFileError(null);
      dispatch({ type: 'SET_INPUT_FILE', file });
      dispatch({ type: 'SET_INPUT_TEXT', text: '' });
      animateDrop();
    }
  }, [dispatch, animateDrop]);

  const handleTextChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    dispatch({ type: 'SET_INPUT_TEXT', text: e.target.value });
    if (e.target.value) dispatch({ type: 'SET_INPUT_FILE', file: null });
  }, [dispatch]);

  const handleStart = useCallback(() => {
    animateLaunch();
    startPipeline();
  }, [startPipeline, animateLaunch]);

  return (
    <div ref={containerRef} className="min-h-screen flex items-center justify-center px-5 py-24 relative">
      {/* Ambient background layers */}
      <div className="fixed inset-0 grid-bg pointer-events-none" />
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_40%,rgba(99,102,241,0.07),transparent)] pointer-events-none" />
      <div className="fixed top-[30%] left-[10%] w-96 h-96 rounded-full blur-[120px] orb-drift pointer-events-none"
        style={{ background: 'radial-gradient(circle, rgba(99,102,241,0.06) 0%, transparent 70%)' }} />
      <div className="fixed top-[50%] right-[8%] w-72 h-72 rounded-full blur-[100px] orb-drift-slow pointer-events-none"
        style={{ background: 'radial-gradient(circle, rgba(139,92,246,0.06) 0%, transparent 70%)' }} />

      <div className="relative z-10 w-full max-w-2xl xl:max-w-3xl">

        {/* Ã¢â€â‚¬Ã¢â€â‚¬ Header Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
        <div className="text-center mb-10 animate-in">
          <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full mb-6"
            style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.25)', boxShadow: '0 0 20px rgba(99,102,241,0.08)' }}>
            <span className="relative flex items-center justify-center w-2 h-2">
              <span className="absolute inline-flex w-full h-full rounded-full bg-[#6366f1] ping-ring" />
              <span className="relative w-2 h-2 rounded-full bg-[#818cf8]" />
            </span>
            <span className="text-xs font-bold text-[#818cf8] uppercase tracking-widest">AI Factory</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-[#f0f0fc] tracking-tighter mb-4 leading-tight">
            What are you <span className="text-gradient-indigo">building?</span>
          </h1>
          <p className="text-[#5a5a80] text-base md:text-lg max-w-lg mx-auto leading-relaxed">
            Paste requirements or upload a document.
            Eight agents turn it into a complete technical MVP specification.
          </p>
        </div>

        {/* Ã¢â€â‚¬Ã¢â€â‚¬ Main card Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
        <div className="animate-in relative rounded-3xl overflow-hidden"
          style={{ background: 'rgba(13,13,26,0.85)', border: '1px solid rgba(99,102,241,0.14)', backdropFilter: 'blur(20px)', boxShadow: '0 0 0 1px rgba(99,102,241,0.06), 0 24px 80px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04)' }}>
          {/* Top accent line */}
          <div className="absolute top-0 left-0 right-0 h-px"
            style={{ background: 'linear-gradient(90deg, transparent, rgba(99,102,241,0.5), rgba(139,92,246,0.5), transparent)' }} />

          <div className="p-6 md:p-8 space-y-4">

            {/* Ã¢â€â‚¬Ã¢â€â‚¬ Input methods Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
            <div className="grid md:grid-cols-[1fr_2fr] gap-3">

              {/* File Upload zone */}
              <div
                ref={dropZoneRef}
                onDragOver={(e) => e.preventDefault()}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDrop={handleFileDrop}
                onClick={() => !hasText && fileInputRef.current?.click()}
                className={`relative rounded-2xl border-2 border-dashed select-none overflow-hidden transition-all duration-300 ${
                  hasFile
                    ? 'cursor-default'
                    : hasText
                    ? 'cursor-not-allowed opacity-40 pointer-events-none'
                    : 'cursor-pointer'
                }`}
                style={{
                  background: hasFile
                    ? 'rgba(99,102,241,0.07)'
                    : isDragging
                    ? 'rgba(99,102,241,0.1)'
                    : 'rgba(8,8,15,0.5)',
                  borderColor: hasFile
                    ? 'rgba(99,102,241,0.5)'
                    : isDragging
                    ? 'rgba(129,140,248,0.7)'
                    : 'rgba(99,102,241,0.15)',
                  boxShadow: hasFile
                    ? '0 0 30px rgba(99,102,241,0.15), inset 0 0 30px rgba(99,102,241,0.04)'
                    : isDragging
                    ? '0 0 40px rgba(99,102,241,0.25), inset 0 0 40px rgba(99,102,241,0.06)'
                    : 'none',
                }}
              >
                {isDragging && <div className="absolute inset-0 shimmer pointer-events-none" />}
                <input ref={fileInputRef} type="file" accept=".pdf,.txt,.md,.png,.jpg,.jpeg" className="hidden" onChange={handleFileSelect} />

                <div className="min-h-[200px] flex flex-col items-center justify-center p-6 text-center">
                  {hasFile ? (
                    <div className="w-full space-y-3">
                      <div className="relative mx-auto w-14 h-14 rounded-2xl flex items-center justify-center"
                        style={{ background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.35)' }}>
                        <FileCode className="w-7 h-7 text-[#6366f1]" />
                        <div className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-[#10b981] flex items-center justify-center" style={{ border: '2px solid rgba(13,13,26,0.9)' }}>
                          <CheckCircle2 className="w-3 h-3 text-white" />
                        </div>
                      </div>
                      <div>
                        <div className="text-sm font-bold text-[#f0f0fc] truncate px-2">{state.input_file?.name}</div>
                        <div className="text-xs text-[#5a5a80] mt-0.5">{((state.input_file?.size ?? 0) / 1024).toFixed(1)} KB</div>
                      </div>
                      <button
                        className="flex items-center gap-1.5 text-xs text-[#5a5a80] hover:text-[#f87171] transition-colors mx-auto px-3 py-1.5 rounded-lg hover:bg-[rgba(248,113,113,0.08)]"
                        onClick={(e) => { e.stopPropagation(); dispatch({ type: 'SET_INPUT_FILE', file: null }); }}
                      >
                        <X className="w-3 h-3" /> Remove file
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className={`relative mx-auto w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300 ${isDragging ? 'scale-110' : ''}`}
                        style={{ background: isDragging ? 'rgba(99,102,241,0.15)' : 'rgba(8,8,15,0.8)', border: `1px solid ${isDragging ? 'rgba(99,102,241,0.4)' : 'rgba(99,102,241,0.12)'}` }}>
                        {isDragging
                          ? <Sparkles className="w-7 h-7 text-[#818cf8]" />
                          : <Upload className="w-7 h-7 text-[#353560]" />}
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-[#a0a0c0]">
                          {isDragging ? 'Ã¢Å“Â¦ Drop it here' : 'Drop a file'}
                        </div>
                        <div className="text-xs text-[#353560] mt-1">PDF Ã‚Â· image Ã‚Â· text Ã‚Â· markdown</div>
                      </div>
                      <div className="text-micro text-[#353560] uppercase tracking-[0.15em] font-bold">or click to browse</div>
                    </div>
                  )}
                </div>
              </div>

              {/* Text paste */}
              <div className={`relative rounded-2xl border transition-all duration-300 overflow-hidden ${
                hasFile ? 'opacity-40 pointer-events-none' : ''
              }`}
                style={{
                  background: hasText ? 'rgba(8,8,15,0.6)' : 'rgba(8,8,15,0.4)',
                  borderColor: hasText ? 'rgba(99,102,241,0.35)' : 'rgba(99,102,241,0.1)',
                  boxShadow: hasText ? '0 0 24px rgba(99,102,241,0.08), inset 0 1px 0 rgba(255,255,255,0.02)' : 'none',
                }}>
                {/* Focus glow overlay */}
                {hasText && (
                  <div className="absolute top-0 left-0 right-0 h-px"
                    style={{ background: 'linear-gradient(90deg, transparent, rgba(99,102,241,0.4), transparent)' }} />
                )}
                <textarea
                  value={state.input_text}
                  onChange={handleTextChange}
                  disabled={hasFile}
                  placeholder={`${PLACEHOLDERS[placeholderIdx]}\n\nDescribe what you're building: target users, key features, technical constraints, integrations, and any preferences.`}
                  className="w-full h-full min-h-[200px] bg-transparent text-[#c0c0e0] text-sm placeholder-[#353560] resize-none outline-none p-5 rounded-2xl leading-relaxed scrollbar-thin"
                />
                {hasText && (
                  <button
                    className="absolute top-3 right-3 w-7 h-7 rounded-full flex items-center justify-center transition-all group"
                    style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)' }}
                    onClick={() => dispatch({ type: 'SET_INPUT_TEXT', text: '' })}
                  >
                    <X className="w-3 h-3 text-[#5a5a80] group-hover:text-[#f87171] transition-colors" />
                  </button>
                )}
                {/* Character count */}
                {hasText && (
                  <div className="absolute bottom-3 right-3 text-micro text-[#353560] font-mono">
                    {state.input_text.length} chars
                  </div>
                )}
              </div>
            </div>

            {/* Ã¢â€â‚¬Ã¢â€â‚¬ File error message Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
            {fileError && (
              <div className="flex items-center gap-2.5 px-4 py-3 rounded-xl float-up"
                style={{ background: 'rgba(248,113,113,0.07)', border: '1px solid rgba(248,113,113,0.3)' }}>
                <AlertCircle className="w-4 h-4 text-[#f87171] flex-shrink-0" />
                <p className="text-xs text-[#f87171] flex-1">{fileError}</p>
                <button onClick={() => setFileError(null)}
                  className="w-5 h-5 rounded-full flex items-center justify-center text-[#f87171] hover:bg-[rgba(248,113,113,0.15)] transition-colors">
                  <X className="w-3 h-3" />
                </button>
              </div>
            )}

            {/* Ã¢â€â‚¬Ã¢â€â‚¬ Mode Selector Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
            <div className="animate-in rounded-2xl overflow-hidden"
              style={{ background: 'rgba(8,8,15,0.5)', border: '1px solid rgba(99,102,241,0.1)' }}>
              <div className="px-5 py-3 border-b" style={{ borderColor: 'rgba(99,102,241,0.08)' }}>
                <div className="text-micro font-black text-[#353560] uppercase tracking-[0.2em] flex items-center gap-2">
                  <div className="w-1 h-3 rounded-full" style={{ background: 'linear-gradient(to bottom, #6366f1, #8b5cf6)' }} />
                  Pipeline Mode
                </div>
              </div>
              <div className="p-4 grid grid-cols-2 gap-3">
                {([
                  {
                    mode: 'auto' as PipelineMode,
                    icon: Zap,
                    label: 'Fully Automated',
                    sub: 'All 8 phases run uninterrupted',
                    color: '#6366f1',
                    colorRgb: '99,102,241',
                  },
                  {
                    mode: 'guided' as PipelineMode,
                    icon: Brain,
                    label: 'Guided Review',
                    sub: 'Pause at key phases to review & edit',
                    color: '#8b5cf6',
                    colorRgb: '139,92,246',
                    recommended: true,
                  },
                ]).map(({ mode, icon: Icon, label, sub, color, colorRgb, recommended = false }) => {
                  const active = state.mode === mode;
                  return (
                    <button
                      key={mode}
                      onClick={() => {
                        dispatch({ type: 'SET_MODE', mode });
                        // little tap animation
                        gsap.fromTo(`[data-mode="${mode}"]`, { scale: 0.97 }, { scale: 1, duration: 0.3, ease: 'elastic.out(1,0.5)' });
                      }}
                      data-mode={mode}
                      className="relative p-4 rounded-xl text-left transition-all duration-250 overflow-hidden group"
                      style={{
                        background: active ? `rgba(${colorRgb},0.1)` : 'transparent',
                        border: `1px solid ${active ? `rgba(${colorRgb},0.45)` : 'rgba(99,102,241,0.1)'}`,
                        boxShadow: active ? `0 0 20px rgba(${colorRgb},0.12), inset 0 1px 0 rgba(255,255,255,0.04)` : 'none',
                      }}
                    >
                      {active && (
                        <div className="absolute top-0 left-0 right-0 h-px"
                          style={{ background: `linear-gradient(90deg, transparent, rgba(${colorRgb},0.6), transparent)` }} />
                      )}
                      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                        style={{ background: `radial-gradient(ellipse at top right, rgba(${colorRgb},0.05), transparent)` }} />
                      <div className="relative z-10">
                        <div className="flex items-center gap-2.5 mb-2">
                          <div className="w-8 h-8 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110"
                            style={{ background: active ? `rgba(${colorRgb},0.2)` : 'rgba(99,102,241,0.06)', border: `1px solid rgba(${colorRgb},${active ? '0.4' : '0.1'})` }}>
                            <Icon className="w-4 h-4" style={{ color: active ? color : '#353560' }} />
                          </div>
                          <span className={`text-sm font-bold transition-colors ${active ? 'text-[#f0f0fc]' : 'text-[#5a5a80]'}`}>{label}</span>
                          {recommended && (
                            <span className="ml-auto text-micro px-1.5 py-0.5 rounded font-black uppercase tracking-widest"
                              style={{ background: `rgba(${colorRgb},0.15)`, color }}>
                              Rec
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-[#5a5a80] leading-tight pl-[42px]">{sub}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Ã¢â€â‚¬Ã¢â€â‚¬ Resume banner Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
            {showBanner && state.stage === 'paused' && state.pipeline && (
              <div className="animate-in flex items-start gap-3 p-4 rounded-2xl"
                style={{ background: 'rgba(251,191,36,0.05)', border: '1px solid rgba(251,191,36,0.22)' }}>
                <AlertCircle className="w-4 h-4 text-[#fbbf24] mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-bold text-[#fbbf24] mb-0.5">
                    Previous run found (Phase {state.pipeline.paused_at_phase})
                  </div>
                  <div className="text-xs text-[#5a5a80]">Interrupted Ã¢â‚¬â€ resume or start fresh</div>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <button onClick={resumePipeline}
                    className="text-xs px-3 py-1.5 rounded-xl font-bold transition-all hover:brightness-110"
                    style={{ background: 'rgba(251,191,36,0.12)', border: '1px solid rgba(251,191,36,0.3)', color: '#fbbf24' }}>
                    Resume
                  </button>
                  <button onClick={() => { resetFactory(); setShowBanner(false); }}
                    className="text-xs px-3 py-1.5 rounded-xl font-semibold transition-all"
                    style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.18)', color: '#818cf8' }}>
                    Discard
                  </button>
                </div>
              </div>
            )}

            {/* Ã¢â€â‚¬Ã¢â€â‚¬ Launch Button Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
            <div className="animate-in">
              <button
                ref={launchBtnRef}
                onClick={handleStart}
                disabled={!canStart}
                className={`group w-full flex items-center justify-center gap-3 py-4 px-8 rounded-2xl font-bold text-base relative overflow-hidden transition-all duration-300 ${
                  canStart ? 'cursor-pointer text-white' : 'cursor-not-allowed'
                }`}
                style={canStart ? {
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  boxShadow: '0 0 0 1px rgba(99,102,241,0.3), 0 8px 40px rgba(99,102,241,0.35)',
                } : {
                  background: 'rgba(13,13,26,0.8)',
                  border: '1px solid rgba(99,102,241,0.08)',
                  color: '#353560',
                }}
              >
                {/* Shine sweep on hover */}
                {canStart && (
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    style={{ background: 'linear-gradient(135deg, rgba(255,255,255,0.1), transparent 60%)' }} />
                )}
                {/* Glow on hover */}
                {canStart && (
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                    style={{ boxShadow: '0 0 60px rgba(99,102,241,0.5)' }} />
                )}
                <span className="relative z-10 flex items-center gap-3">
                  {canStart ? (
                    <>
                      <Play className="w-5 h-5" strokeWidth={2.5} />
                      Start the pipeline
                      <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1.5" />
                    </>
                  ) : (
                    <>
                      <FileText className="w-5 h-5 opacity-40" />
                      Start the pipeline
                    </>
                  )}
                </span>
              </button>
              {!canStart && (
                <p className="text-center text-xs text-[#353560] mt-2.5">
                  Paste your requirements or upload a file to begin
                </p>
              )}
            </div>

          </div>
        </div>

        {/* Ã¢â€â‚¬Ã¢â€â‚¬ Info chips Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */}
        <div className="mt-5 flex flex-wrap justify-center gap-3 animate-in">
          {[
            { icon: 'Ã°Å¸â€â€™', text: 'Your own API keys' },
            { icon: 'Ã¢Å¡Â¡', text: '8-phase pipeline' },
            { icon: 'Ã°Å¸Â§Â ', text: 'Self-improving agents' },
          ].map(({ icon, text }) => (
            <div key={text} className="flex items-center gap-1.5 text-xs text-[#353560] px-3 py-1.5 rounded-full"
              style={{ background: 'rgba(13,13,26,0.6)', border: '1px solid rgba(99,102,241,0.08)' }}>
              <span>{icon}</span>
              <span>{text}</span>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}
