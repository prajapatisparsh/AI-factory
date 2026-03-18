'use client';

import { useRef, useState, useEffect, memo, useCallback } from 'react';
import gsap from 'gsap';
import {
  CheckCircle2, Clock, Loader2, Pause, ChevronDown, ChevronRight,
  MessageSquare, BookOpen, AlertTriangle, Shield, Edit3, Play,
  RotateCcw, ThumbsUp, ThumbsDown, FileCode, Zap, Star, Terminal,
  Cpu, Wifi, WifiOff,
} from 'lucide-react';
import { MarkdownRenderer } from '@/components/ui/markdown-renderer';
import { useFactory } from '@/lib/factory-store';
import type {
  PhaseResult, UserStory, QAReport, PMEvaluation,
  DiscussionEvent, ClarificationQA, CoachEvent, DocumentAnalysis,
} from '@/lib/types';
import { PHASE_META } from '@/lib/types';

// â”€â”€ Agent color palette â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const AGENT_COLORS: Record<string, { text: string; bg: string; border: string; glow: string }> = {
  VisionAgent:   { text: '#22d3ee', bg: 'rgba(34,211,238,0.08)',   border: 'rgba(34,211,238,0.22)',  glow: 'rgba(34,211,238,0.3)' },
  PMAgent:       { text: '#6366f1', bg: 'rgba(99,102,241,0.08)',   border: 'rgba(99,102,241,0.22)',  glow: 'rgba(99,102,241,0.35)' },
  TechLeadAgent: { text: '#8b5cf6', bg: 'rgba(139,92,246,0.08)',   border: 'rgba(139,92,246,0.22)',  glow: 'rgba(139,92,246,0.3)' },
  DevTeamAgent:  { text: '#a78bfa', bg: 'rgba(167,139,250,0.08)',  border: 'rgba(167,139,250,0.22)', glow: 'rgba(167,139,250,0.3)' },
  QAAgent:       { text: '#f87171', bg: 'rgba(248,113,113,0.08)',  border: 'rgba(248,113,113,0.22)', glow: 'rgba(248,113,113,0.3)' },
  CoachAgent:    { text: '#fbbf24', bg: 'rgba(251,191,36,0.08)',   border: 'rgba(251,191,36,0.22)',  glow: 'rgba(251,191,36,0.3)' },
  System:        { text: '#10b981', bg: 'rgba(16,185,129,0.08)',   border: 'rgba(16,185,129,0.22)',  glow: 'rgba(16,185,129,0.3)' },
};

function agentColor(agent: string) {
  for (const [key, val] of Object.entries(AGENT_COLORS)) {
    if (agent.toLowerCase().includes(key.toLowerCase())) return val;
  }
  return { text: '#818cf8', bg: 'rgba(129,140,248,0.08)', border: 'rgba(129,140,248,0.22)', glow: 'rgba(129,140,248,0.3)' };
}

// â”€â”€ Phase status icon â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function PhaseStatusIcon({ status }: { status: PhaseResult['status'] }) {
  if (status === 'complete') return <CheckCircle2 className="w-4 h-4 text-[#10b981] flex-shrink-0" aria-label="Phase complete" />;
  if (status === 'running')  return <Loader2 className="w-4 h-4 text-[#818cf8] animate-spin flex-shrink-0" aria-label="Phase running" />;
  if (status === 'paused')   return <Pause className="w-4 h-4 text-[#fbbf24] flex-shrink-0" aria-label="Phase paused" />;
  return <Clock className="w-4 h-4 flex-shrink-0" style={{ color: 'rgba(99,102,241,0.18)' }} aria-label="Phase pending" />;
}

// â”€â”€ Section label â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function SectionLabel({ label, color = '#6366f1', icon }: { label: string; color?: string; icon?: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2 mb-3">
      <div className="w-1 h-4 rounded-full" style={{ background: `linear-gradient(to bottom, ${color}, transparent)` }} />
      {icon}
      <span className="text-micro font-black uppercase tracking-[0.18em]" style={{ color: `${color}cc` }}>{label}</span>
    </div>
  );
}

// â”€â”€ Stat chip â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function StatChip({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="p-3.5 rounded-2xl text-center transition-all hover:brightness-110"
      style={{ background: `${color}08`, border: `1px solid ${color}1a` }}>
      <div className="text-micro font-black uppercase tracking-widest mb-1.5"
        style={{ color: `${color}80` }}>{label}</div>
      <div className="text-xl font-black leading-none capitalize"
        style={{ color }}>{value}</div>
    </div>
  );
}

// â”€â”€ Document Analysis â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function DocumentAnalysisOutput({ data }: { data: DocumentAnalysis }) {
  return (
    <div className="space-y-5 float-up">
      <div className="grid sm:grid-cols-3 gap-2.5">
        <StatChip label="Project Type" value={data.project_type.replace('_', ' ')} color="#22d3ee" />
        <StatChip label="Features Found" value={String(data.features.length)} color="#6366f1" />
        <StatChip label="Personas" value={String(data.personas.length)} color="#8b5cf6" />
      </div>

      <div>
        <SectionLabel label="Extracted Features" color="#6366f1" />
        <div className="flex flex-wrap gap-1.5">
          {data.features.map((f) => (
            <span key={f} className="text-2xs px-2.5 py-1 rounded-lg font-semibold transition-all hover:brightness-125"
              style={{ background: 'rgba(99,102,241,0.08)', color: '#818cf8', border: '1px solid rgba(99,102,241,0.15)' }}>
              {f}
            </span>
          ))}
        </div>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        <div>
          <SectionLabel label="Personas" color="#8b5cf6" />
          <div className="space-y-1.5">
            {data.personas.map((p) => (
              <div key={p} className="flex items-center gap-2 text-sm text-[#a0a0c0]">
                <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: '#8b5cf6' }} />{p}
              </div>
            ))}
          </div>
        </div>
        {data.ambiguities.length > 0 && (
          <div>
            <SectionLabel label="Ambiguities" color="#fbbf24"
              icon={<AlertTriangle className="w-3 h-3 text-[#fbbf2466]" />} />
            <div className="space-y-1.5">
              {data.ambiguities.map((a, i) => (
                <div key={i} className="text-2xs text-[#6a6a8a] flex items-start gap-2">
                  <span className="w-1 h-1 rounded-full mt-1.5 flex-shrink-0" style={{ background: 'rgba(251,191,36,0.5)' }} />{a}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// â”€â”€ User Stories â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function UserStoriesOutput({ stories, architecture }: { stories: UserStory[]; architecture?: string }) {
  const [activeTab, setActiveTab] = useState<'stories' | 'arch'>('stories');
  const PRIORITY_STYLES: Record<string, { color: string; bg: string }> = {
    Critical: { color: '#f87171', bg: 'rgba(248,113,113,0.08)' },
    High:     { color: '#fbbf24', bg: 'rgba(251,191,36,0.08)' },
    Medium:   { color: '#818cf8', bg: 'rgba(129,140,248,0.08)' },
    Low:      { color: '#5a5a80', bg: 'rgba(99,102,241,0.04)' },
  };

  return (
    <div className="float-up">
      {/* Tabs */}
      <div className="flex gap-1 mb-4 p-1 rounded-xl w-fit"
        style={{ background: 'rgba(5,5,12,0.8)', border: '1px solid rgba(99,102,241,0.08)' }}>
        {(['stories', 'arch'] as const).map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            className="px-4 py-1.5 rounded-lg text-xs font-bold transition-all"
            style={activeTab === tab ? {
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              color: 'white',
              boxShadow: '0 2px 12px rgba(99,102,241,0.35)',
            } : { color: '#5a5a80' }}>
            {tab === 'stories' ? `Stories (${stories.length})` : 'Architecture'}
          </button>
        ))}
      </div>

      {activeTab === 'stories' ? (
        <div className="space-y-2">
          {stories.map((story) => {
            const ps = PRIORITY_STYLES[story.priority] ?? PRIORITY_STYLES.Low;
            return (
              <div key={story.id}
                className="group p-4 rounded-2xl overflow-hidden transition-all duration-200 hover:translate-x-0.5"
                style={{ background: 'rgba(8,8,18,0.7)', border: '1px solid rgba(99,102,241,0.08)' }}
                onMouseEnter={e => (e.currentTarget.style.borderColor = 'rgba(99,102,241,0.25)')}
                onMouseLeave={e => (e.currentTarget.style.borderColor = 'rgba(99,102,241,0.08)')}
              >
                {/* Left accent */}
                <div className="flex items-start gap-3">
                  <div className="w-0.5 rounded-full self-stretch flex-shrink-0 mt-0.5"
                    style={{ background: ps.color, minHeight: '32px', opacity: 0.7 }} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1.5">
                      <span className="text-micro font-mono font-black px-1.5 py-0.5 rounded"
                        style={{ color: '#6366f1', background: 'rgba(99,102,241,0.12)' }}>{story.id}</span>
                      <h4 className="text-sm font-bold text-[#f0f0fc] flex-1">{story.title}</h4>
                      <span className="text-micro px-2 py-0.5 rounded-full font-black uppercase tracking-widest"
                        style={{ color: ps.color, background: ps.bg }}>
                        {story.priority}
                      </span>
                    </div>
                    <p className="text-xs text-[#5a5a80] mb-3 leading-relaxed">
                      As a <strong className="text-[#a0a0c0]">{story.user_role}</strong>, I want to{' '}
                      <strong className="text-[#a0a0c0]">{story.action}</strong> so that{' '}
                      <strong className="text-[#a0a0c0]">{story.benefit}</strong>
                    </p>
                    <div className="space-y-1">
                      {story.acceptance_criteria.map((c, i) => (
                        <div key={i} className="flex items-start gap-2 text-2xs text-[#5a5a80]">
                          <CheckCircle2 className="w-3 h-3 text-[#10b981] mt-0.5 flex-shrink-0" />{c}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : architecture ? (
        <div
          className="p-5 rounded-2xl max-h-[500px] overflow-y-auto overscroll-contain scrollbar-thin"
          onWheel={(e) => e.stopPropagation()}
          style={{ background: 'rgba(8,8,18,0.7)', border: '1px solid rgba(99,102,241,0.1)' }}>
          <MarkdownRenderer content={architecture} />
        </div>
      ) : null}
    </div>
  );
}

// â”€â”€ Agent Discussion â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function DiscussionBlock({ discussion }: { discussion: DiscussionEvent }) {
  const [expanded, setExpanded] = useState(true);
  const [mounted, setMounted]   = useState(true); // stays true during close animation
  const bodyRef = useRef<HTMLDivElement>(null);

  const toggle = () => {
    if (expanded) {
      // Collapse: animate out, THEN unmount so GSAP finishes on a real DOM node
      if (bodyRef.current) {
        gsap.to(bodyRef.current, {
          height: 0, opacity: 0, duration: 0.25, ease: 'power2.in',
          onComplete: () => setMounted(false),
        });
      } else {
        setMounted(false);
      }
      setExpanded(false);
    } else {
      // Expand: mount first, then animate in on next frame
      setMounted(true);
      setExpanded(true);
      requestAnimationFrame(() => {
        if (bodyRef.current) {
          gsap.fromTo(bodyRef.current,
            { height: 0, opacity: 0 },
            { height: 'auto', opacity: 1, duration: 0.3, ease: 'power2.out' }
          );
        }
      });
    }
  };

  return (
    <div className="mt-4 rounded-2xl overflow-hidden float-up"
      style={{ background: 'rgba(139,92,246,0.03)', border: '1px solid rgba(139,92,246,0.18)' }}>
      {/* Accent line */}
      <div className="absolute top-0 left-0 right-0 h-px"
        style={{ background: 'linear-gradient(90deg, transparent, rgba(139,92,246,0.5), transparent)' }} />

      <button onClick={toggle}
        className="w-full flex items-center justify-between px-5 py-3.5 transition-colors"
        style={{ background: 'rgba(139,92,246,0.02)' }}
        onMouseEnter={e => (e.currentTarget.style.background = 'rgba(139,92,246,0.05)')}
        onMouseLeave={e => (e.currentTarget.style.background = 'rgba(139,92,246,0.02)')}>
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-xl flex items-center justify-center"
            style={{ background: 'rgba(139,92,246,0.1)', border: '1px solid rgba(139,92,246,0.2)' }}>
            <MessageSquare className="w-3.5 h-3.5 text-[#a78bfa]" />
          </div>
          <div>
            <span className="text-sm font-bold text-[#a78bfa]">Agent Discussion</span>
            <span className="text-xs text-[#5a5a80] ml-2 hidden sm:inline">{discussion.agents.join(' • ')}</span>
          </div>
        </div>
        <div className="transition-transform duration-200" style={{ transform: expanded ? 'rotate(0)' : 'rotate(-90deg)' }}>
          <ChevronDown className="w-4 h-4 text-[#5a5a80]" />
        </div>
      </button>

      {mounted && (
        <div ref={bodyRef} className="px-5 pb-5">
          <div className="text-micro text-[#5a5a80] mb-4 italic px-1">Topic: {discussion.topic}</div>
          <div className="space-y-3">
            {discussion.messages.map((msg, i) => {
              const ac = agentColor(msg.agent);
              const isRight = i % 2 !== 0;
              return (
                <div key={i} className={`flex gap-2.5 ${isRight ? 'flex-row-reverse' : ''}`}>
                  {/* Avatar */}
                  <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-black flex-shrink-0"
                    style={{ background: ac.bg, color: ac.text, border: `1px solid ${ac.border}`, boxShadow: `0 0 10px ${ac.glow}` }}>
                    {msg.agent.charAt(0)}
                  </div>
                  {/* Bubble */}
                  <div className={`p-3 ${isRight ? 'rounded-[16px_4px_16px_16px]' : 'rounded-[4px_16px_16px_16px]'}`}
                    style={{ maxWidth: 'clamp(200px, 78%, 480px)', background: 'rgba(10,10,22,0.9)', border: `1px solid ${ac.border}` }}>
                    <div className="text-micro font-black uppercase tracking-widest mb-1" style={{ color: ac.text }}>
                      {msg.agent}
                    </div>
                    <div className="text-xs text-[#a0a0c0] leading-relaxed">{msg.content}</div>
                  </div>
                </div>
              );
            })}
          </div>
          {discussion.consensus && (
            <div className="mt-4 p-3.5 rounded-xl"
              style={{ background: 'rgba(16,185,129,0.04)', border: '1px solid rgba(16,185,129,0.15)' }}>
              <div className="text-micro font-black text-[#10b981] uppercase tracking-widest mb-1.5">Consensus reached</div>
              <div className="text-xs text-[#5a5a80] leading-relaxed">{discussion.consensus}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// â”€â”€ Clarifications â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function ClarificationsOutput({ items }: { items: ClarificationQA[] }) {
  const safeItems = Array.isArray(items) ? items : [];
  return (
    <div className="space-y-2.5 float-up">
      {safeItems.map((item) => (
        <div key={item.id} className="rounded-2xl overflow-hidden"
          style={{ background: 'rgba(8,8,18,0.7)', border: '1px solid rgba(99,102,241,0.1)' }}>
          <div className="px-4 py-3.5">
            <div className="flex items-start gap-2.5">
              <span className="text-micro font-mono font-black px-1.5 py-0.5 rounded flex-shrink-0"
                style={{ color: '#6366f1', background: 'rgba(99,102,241,0.1)' }}>{item.id}</span>
              <div className="text-sm font-semibold text-[#e0e0f0] leading-snug">{item.question}</div>
            </div>
            {item.context && (
              <div className="text-xs text-[#5a5a80] mt-1.5 ml-9 leading-relaxed">{item.context}</div>
            )}
          </div>
          {item.answer && (
            <div className="px-4 py-3 border-t" style={{ borderColor: 'rgba(16,185,129,0.1)', background: 'rgba(16,185,129,0.02)' }}>
              <div className="text-micro font-black text-[#10b981] uppercase tracking-widest mb-1.5">Answer</div>
              <div className="text-xs text-[#5a5a80] leading-relaxed">{item.answer}</div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// â”€â”€ Spec Output â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function SpecOutput({ backendSpec, frontendSpec, editable = false, onSave }: {
  backendSpec?: string; frontendSpec?: string; editable?: boolean;
  onSave?: (backend: string, frontend: string) => void;
}) {
  const [activeTab, setActiveTab]     = useState<'backend' | 'frontend'>('backend');
  const [editBackend, setEditBackend]   = useState(backendSpec ?? '');
  const [editFrontend, setEditFrontend] = useState(frontendSpec ?? '');
  const [isEditing, setIsEditing]     = useState(false);

  useEffect(() => { setEditBackend(backendSpec ?? ''); }, [backendSpec]);
  useEffect(() => { setEditFrontend(frontendSpec ?? ''); }, [frontendSpec]);

  const handleToggleEdit = () => {
    if (isEditing && onSave) onSave(editBackend, editFrontend);
    setIsEditing(!isEditing);
  };

  const tabs = [
    { id: 'backend',  label: 'Backend' },
    { id: 'frontend', label: 'Frontend' },
  ] as const;

  return (
    <div className="float-up">
      <div className="flex items-center justify-between mb-3">
        <div className="flex gap-1 p-1 rounded-xl w-fit"
          style={{ background: 'rgba(5,5,12,0.8)', border: '1px solid rgba(99,102,241,0.08)' }}>
          {tabs.map((tab) => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className="px-4 py-1.5 rounded-lg text-xs font-bold transition-all"
              style={activeTab === tab.id ? {
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                color: 'white',
                boxShadow: '0 2px 12px rgba(99,102,241,0.35)',
              } : { color: '#5a5a80' }}>
              {tab.label}
            </button>
          ))}
        </div>
        {editable && (
          <button onClick={handleToggleEdit}
            className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-xl transition-all font-semibold"
            style={isEditing ? {
              background: 'rgba(99,102,241,0.12)', color: '#818cf8',
              border: '1px solid rgba(99,102,241,0.3)',
              boxShadow: '0 0 12px rgba(99,102,241,0.15)',
            } : {
              background: 'transparent', color: '#5a5a80',
              border: '1px solid rgba(99,102,241,0.1)',
            }}>
            <Edit3 className="w-3 h-3" />
            {isEditing ? 'Save changes' : 'Edit spec'}
          </button>
        )}
      </div>
      <div
        className="rounded-2xl max-h-[500px] overflow-y-auto overscroll-contain scrollbar-thin"
        onWheel={(e) => e.stopPropagation()}
        style={{ background: 'rgba(5,5,12,0.9)', border: '1px solid rgba(99,102,241,0.1)' }}>
        {isEditing ? (
          <textarea
            value={activeTab === 'backend' ? editBackend : editFrontend}
            onChange={(e) => activeTab === 'backend' ? setEditBackend(e.target.value) : setEditFrontend(e.target.value)}
            className="w-full h-[500px] bg-transparent text-[#a0a0c0] text-xs p-5 outline-none resize-none font-mono leading-relaxed scrollbar-thin"
          />
        ) : (
          <div className="p-5">
            <MarkdownRenderer content={activeTab === 'backend' ? (backendSpec ?? '') : (frontendSpec ?? '')} />
          </div>
        )}
      </div>
    </div>
  );
}

// â”€â”€ QA Report â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function QAReportOutput({ report }: { report: QAReport }) {
  const severities = [
    { label: 'Critical', items: report.critical, color: '#f87171' },
    { label: 'High',     items: report.high,     color: '#fbbf24' },
    { label: 'Medium',   items: report.medium,   color: '#818cf8' },
    { label: 'Low',      items: report.low,      color: '#5a5a80' },
  ];
  const [expanded, setExpanded] = useState<string[]>([]);
  const toggleSev = (l: string) =>
    setExpanded(e => e.includes(l) ? e.filter(x => x !== l) : [...e, l]);

  return (
    <div className="float-up space-y-4">
      {/* Summary tiles */}
      <div className="grid grid-cols-4 gap-2">
        {severities.map(({ label, items, color }) => (
          <button key={label} onClick={() => toggleSev(label)}
            className="p-3 rounded-2xl text-center transition-all hover:brightness-110 active:scale-95"
            style={{ background: `${color}07`, border: `1px solid ${color}20` }}>
            <div className="text-2xl font-black mb-0.5" style={{ color }}>{items.length}</div>
            <div className="text-micro font-black uppercase tracking-widest" style={{ color }}>{label}</div>
          </button>
        ))}
      </div>

      {/* Issue lists */}
      {severities.filter(s => s.items.length > 0).map(({ label, items, color }) => (
        <div key={label}>
          <button onClick={() => toggleSev(label)}
            className="w-full flex items-center gap-2 mb-2 group">
            <span className="w-2 h-2 rounded-full" style={{ background: color }} />
            <span className="text-micro font-black uppercase tracking-widest" style={{ color }}>{label} Issues ({items.length})</span>
            <div className="ml-auto transition-transform" style={{ transform: expanded.includes(label) ? 'rotate(180deg)' : 'rotate(0)' }}>
              <ChevronDown className="w-3 h-3" style={{ color }} />
            </div>
          </button>
          {expanded.includes(label) && (
            <div className="space-y-1.5">
              {items.map((issue) => (
                <div key={issue.id} className="p-3 rounded-xl"
                  style={{ background: `${color}05`, border: `1px solid ${color}18` }}>
                  <div className="flex items-start gap-2.5">
                    <span className="text-micro font-mono font-black px-1.5 py-0.5 rounded flex-shrink-0"
                      style={{ background: `${color}18`, color }}>
                      {issue.id}
                    </span>
                    <div>
                      <div className="text-xs font-semibold text-[#e0e0f0]">{issue.desc}</div>
                      <div className="text-micro text-[#5a5a80] mt-0.5">{issue.location}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}

      {/* Security flags */}
      {report.security_flags.length > 0 && (
        <div>
          <SectionLabel label="Security Flags" color="#f87171"
            icon={<Shield className="w-3 h-3 text-[#f8717166]" />} />
          <div className="space-y-1.5">
            {report.security_flags.map((flag, i) => (
              <div key={i} className="flex items-start gap-2 p-2.5 rounded-xl"
                style={{ background: 'rgba(248,113,113,0.04)', border: '1px solid rgba(248,113,113,0.12)' }}>
                <Shield className="w-3 h-3 text-[#f87171] mt-0.5 flex-shrink-0" />
                <span className="text-xs text-[#a0a0c0]">{flag}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// â”€â”€ PM Evaluation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const SCORE_MAX: Record<string, number> = {
  requirements: 30, architecture: 25, completeness: 20,
  qa_compliance: 15, security: 10,
};

function AnimatedBar({ pct, color, delay = 0 }: { pct: number; color: string; delay?: number }) {
  const barRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (barRef.current) {
      gsap.fromTo(barRef.current,
        { width: '0%' },
        { width: `${pct}%`, duration: 1.2, ease: 'power3.out', delay }
      );
    }
  }, [pct, delay]);
  return (
    <div ref={barRef} className="h-full rounded-full" style={{ background: color, width: 0 }} />
  );
}

function PMEvaluationOutput({ evaluation, coachEvent }: { evaluation: PMEvaluation; coachEvent?: CoachEvent }) {
  const approved   = evaluation.status === 'APPROVED';
  const scoreColor = approved ? '#10b981' : evaluation.score >= 70 ? '#fbbf24' : '#f87171';
  const scoreRef   = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scoreRef.current) {
      gsap.fromTo(scoreRef.current,
        { scale: 0.5, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.8, ease: 'back.out(1.7)' }
      );
    }
  }, []);

  return (
    <div className="float-up space-y-4">
      {/* Score hero */}
      <div className="p-6 rounded-2xl relative overflow-hidden"
        style={{ borderColor: approved ? 'rgba(16,185,129,0.2)' : 'rgba(248,113,113,0.2)',
          border: `1px solid ${approved ? 'rgba(16,185,129,0.2)' : 'rgba(248,113,113,0.2)'}`,
          background: approved ? 'rgba(16,185,129,0.03)' : 'rgba(248,113,113,0.03)' }}>
        {/* Glowing radial */}
        <div className="absolute inset-0 pointer-events-none"
          style={{ background: `radial-gradient(ellipse 60% 60% at 15% 50%, ${scoreColor}06, transparent)` }} />

        <div className="relative z-10 flex items-start gap-6 mb-5">
          {/* Big score */}
          <div className="text-center">
            <div ref={scoreRef} className="text-7xl font-black leading-none" style={{ color: scoreColor }}>
              {evaluation.score}
            </div>
            <div className="text-sm text-[#5a5a80] mt-1">/100</div>
          </div>

          <div className="flex-1 pt-1">
            {/* Status badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl text-sm font-bold mb-4"
              style={approved ? { background: 'rgba(16,185,129,0.1)', color: '#10b981', border: '1px solid rgba(16,185,129,0.25)' }
                              : { background: 'rgba(248,113,113,0.1)', color: '#f87171', border: '1px solid rgba(248,113,113,0.25)' }}>
              {approved ? <ThumbsUp className="w-4 h-4" /> : <ThumbsDown className="w-4 h-4" />}
              {evaluation.status}
            </div>

            {/* Breakdown bars */}
            <div className="space-y-2">
              {Object.entries(evaluation.breakdown).map(([key, val], idx) => {
                const max = SCORE_MAX[key] ?? 30;
                const pct = (val / max) * 100;
                const barColor = pct >= 80 ? '#10b981' : pct >= 55 ? '#818cf8' : '#fbbf24';
                return (
                  <div key={key} className="flex items-center gap-3">
                    <span className="text-micro text-[#5a5a80] capitalize w-24 flex-shrink-0 font-medium">
                      {key.replace('_', ' ')}
                    </span>
                    <div className="flex-1 h-1.5 rounded-full overflow-hidden"
                      style={{ background: 'rgba(99,102,241,0.07)' }}>
                      <AnimatedBar pct={pct} color={barColor} delay={0.3 + idx * 0.12} />
                    </div>
                    <span className="text-xs font-bold w-8 text-right tabular-nums" style={{ color: barColor }}>
                      {val}/{max}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Strengths */}
        {evaluation.strengths.length > 0 && (
          <div className="mb-4">
            <SectionLabel label="Strengths" color="#10b981" icon={<Star className="w-3 h-3 text-[#10b98166]" />} />
            <div className="space-y-1">
              {evaluation.strengths.map((s, i) => (
                <div key={i} className="flex items-start gap-2 text-xs text-[#5a5a80]">
                  <CheckCircle2 className="w-3 h-3 text-[#10b981] mt-0.5 flex-shrink-0" />{s}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Feedback */}
        {!approved && evaluation.scolding && (
          <div className="p-3.5 rounded-xl"
            style={{ background: 'rgba(248,113,113,0.05)', border: '1px solid rgba(248,113,113,0.15)' }}>
            <div className="text-micro font-black text-[#f87171] uppercase tracking-widest mb-1.5">PM Feedback</div>
            <p className="text-xs text-[#a0a0c0] leading-relaxed">{evaluation.scolding}</p>
          </div>
        )}
      </div>

      {coachEvent && <CoachEventBlock event={coachEvent} />}
    </div>
  );
}

// â”€â”€ Coach Event â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function CoachEventBlock({ event }: { event: CoachEvent }) {
  return (
    <div className="p-5 rounded-2xl relative overflow-hidden float-up"
      style={{ background: 'rgba(251,191,36,0.02)', border: '1px solid rgba(251,191,36,0.2)' }}>
      <div className="absolute top-0 left-0 right-0 h-px"
        style={{ background: 'linear-gradient(90deg, transparent, rgba(251,191,36,0.5), transparent)' }} />
      <div className="flex items-center gap-2.5 mb-3">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center"
          style={{ background: 'rgba(251,191,36,0.08)', border: '1px solid rgba(251,191,36,0.2)', boxShadow: '0 0 12px rgba(251,191,36,0.15)' }}>
          <BookOpen className="w-4 h-4 text-[#fbbf24]" />
        </div>
        <div>
          <div className="text-sm font-bold text-[#fbbf24]">Coach Agent</div>
          <div className="text-micro text-[#5a5a80]">Extracting lessons</div>
        </div>
      </div>
      <p className="text-xs text-[#5a5a80] mb-4 leading-relaxed">{event.message}</p>
      <div className="space-y-2">
        {event.rules_extracted.map((rule, i) => (
          <div key={i} className="flex items-start gap-3 p-3 rounded-xl"
            style={{ background: 'rgba(251,191,36,0.04)', border: '1px solid rgba(251,191,36,0.1)' }}>
            <div className="w-5 h-5 rounded-full flex items-center justify-center text-micro font-black text-[#fbbf24] flex-shrink-0"
              style={{ background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.2)' }}>
              {i + 1}
            </div>
            <div>
              <div className="text-xs text-[#e0e0f0] leading-relaxed">{rule.rule}</div>
              <div className="text-micro text-[#5a5a80] mt-0.5">-&gt; {rule.target_playbook}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-3 flex items-center gap-2 flex-wrap">
        <span className="text-micro text-[#5a5a80]">Playbooks updated:</span>
        {event.playbooks_updated.map(p => (
          <span key={p} className="text-micro px-1.5 py-0.5 rounded font-semibold"
            style={{ background: 'rgba(251,191,36,0.08)', border: '1px solid rgba(251,191,36,0.15)', color: '#fbbf24' }}>
            {p}
          </span>
        ))}
      </div>
    </div>
  );
}

// â”€â”€ Output Files â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function OutputFilesOutput({ files }: { files: { name: string; filename: string; description: string; exists?: boolean }[] }) {
  const COLORS = ['#6366f1','#8b5cf6','#a78bfa','#22d3ee','#10b981','#6366f1','#f87171','#fbbf24'];
  return (
    <div className="float-up grid sm:grid-cols-2 gap-2">
      {files.map((file, i) => {
        const c = COLORS[i % COLORS.length];
        return (
          <div key={file.filename}
            className="flex items-center gap-3 p-3.5 rounded-xl group transition-all duration-200 hover:translate-x-0.5"
            style={{ background: 'rgba(8,8,18,0.7)', border: '1px solid rgba(99,102,241,0.08)' }}
            onMouseEnter={e => (e.currentTarget.style.borderColor = `${c}40`)}
            onMouseLeave={e => (e.currentTarget.style.borderColor = 'rgba(99,102,241,0.08)')}>
            <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-transform group-hover:scale-110"
              style={{ background: `${c}10`, border: `1px solid ${c}25` }}>
              <FileCode className="w-4 h-4" style={{ color: c }} />
            </div>
            <div className="min-w-0">
              <div className="text-xs font-bold text-[#f0f0fc] truncate">{file.name}</div>
              <div className="text-micro font-mono truncate mt-0.5" style={{ color: `${c}aa` }}>{file.filename}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// â”€â”€ Guided Pause â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function GuidedPauseBlock({ phase, onContinue }: { phase: number; onContinue: () => void }) {
  const btnRef = useRef<HTMLButtonElement>(null);
  const messages: Record<number, string> = {
    2: 'Review the architecture and user stories above. Continue or edit the architecture before QA runs.',
    4: 'Review draft specs. Edit the backend and frontend specs before QA analysis begins.',
    5: 'Review QA findings above. Approve to apply all recommended fixes.',
    6: 'Review fixed specifications. These will be sent to PM for scoring.',
  };

  const handleClick = () => {
    if (btnRef.current) {
      gsap.fromTo(btnRef.current, { scale: 0.95 }, { scale: 1, duration: 0.4, ease: 'elastic.out(1,0.5)' });
    }
    onContinue();
  };

  return (
    <div className="mt-5 p-5 rounded-2xl relative overflow-hidden float-up"
      style={{ background: 'rgba(251,191,36,0.03)', border: '2px solid rgba(251,191,36,0.35)' }}>
      {/* Scanning line */}
      <div className="absolute top-0 left-0 right-0 h-0.5"
        style={{ background: 'linear-gradient(90deg, transparent, rgba(251,191,36,0.6), transparent)' }} />

      <div className="flex items-center gap-2.5 mb-2">
        <div className="w-7 h-7 rounded-lg flex items-center justify-center"
          style={{ background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.25)' }}>
          <Pause className="w-3.5 h-3.5 text-[#fbbf24]" />
        </div>
        <span className="text-sm font-bold text-[#fbbf24]">Awaiting your review</span>
      </div>

      <p className="text-xs text-[#5a5a80] mb-5 leading-relaxed ml-9">
        {messages[phase] ?? 'Review above and continue when ready.'}
      </p>

      <div className="flex items-center gap-3 ml-9">
        <button ref={btnRef} onClick={handleClick}
          className="group flex items-center gap-2 px-5 py-2.5 text-white text-sm font-bold rounded-xl transition-all overflow-hidden relative"
          style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', boxShadow: '0 4px 20px rgba(99,102,241,0.4)' }}>
          <span className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity"
            style={{ background: 'rgba(255,255,255,0.08)' }} />
          <Play className="w-3.5 h-3.5" />
          Continue pipeline
        </button>
        <button className="text-xs text-[#5a5a80] hover:text-[#f87171] transition-colors flex items-center gap-1.5 px-3 py-2 rounded-lg hover:bg-[rgba(248,113,113,0.06)]">
          <RotateCcw className="w-3 h-3" /> Restart
        </button>
      </div>
    </div>
  );
}

// â”€â”€ Live Terminal Log â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function TerminalLog({ log }: { log?: string }) {
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [log]);

  if (!log) return null;
  const lines = log.split('\n').filter(Boolean).slice(-12);
  return (
    <div className="mt-4 rounded-2xl overflow-hidden"
      style={{ background: 'rgba(2,4,8,0.95)', border: '1px solid rgba(16,185,129,0.15)' }}>
      {/* Terminal titlebar */}
      <div className="flex items-center gap-2 px-4 py-2.5 border-b"
        style={{ borderColor: 'rgba(16,185,129,0.1)', background: 'rgba(5,8,15,0.8)' }}>
        <Terminal className="w-3.5 h-3.5 text-[#10b981]" />
        <span className="text-micro font-mono font-bold text-[#10b981] uppercase tracking-widest">Agent Output</span>
        <span className="ml-auto w-1.5 h-1.5 rounded-full bg-[#10b981] dot-pulse" />
      </div>
      <div ref={logRef} className="p-4 max-h-44 overflow-y-auto overscroll-contain scrollbar-thin space-y-0.5" onWheel={(e) => e.stopPropagation()}>
        {lines.map((line, i) => (
          <div key={i} className={`text-2xs font-mono leading-relaxed log-enter ${i === lines.length - 1 ? 'text-[#e0e0f0]' : 'text-[#3a5a3a]'}`}>
            <span className="text-[#1a4a2a] select-none mr-2">&gt;</span>{line}
          </div>
        ))}
        <div className="text-2xs font-mono text-[#10b981] cursor-blink" />
      </div>
    </div>
  );
}

// â”€â”€ Phase connector spine â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function PhaseConnector({ status }: { status: PhaseResult['status'] }) {
  const color =
    status === 'complete' ? '#10b981' :
    status === 'running'  ? '#6366f1' :
    status === 'paused'   ? '#fbbf24' : 'rgba(99,102,241,0.08)';

  return (
    <div className="absolute left-[22px] -bottom-2 w-px h-2 z-10 transition-all duration-500"
      style={{ background: color }} />
  );
}

// â”€â”€ Phase Card â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const PhaseCard = memo(function PhaseCard({
  phase, isPaused, onContinue, onSaveSpecs, isLast, collapsed, onToggleCollapse,
}: {
  phase: PhaseResult; isPaused: boolean; onContinue: () => void;
  onSaveSpecs?: (phaseNum: number, backend: string, frontend: string) => void;
  isLast: boolean;
  collapsed: boolean;
  onToggleCollapse: () => void;
}) {
  const cardRef    = useRef<HTMLDivElement>(null);
  const bodyRef = useRef<HTMLDivElement>(null);
  const prevStatus = useRef(phase.status);

  // Scroll into view + entrance animation when phase becomes running
  useEffect(() => {
    if (phase.status === 'running' && prevStatus.current !== 'running' && cardRef.current) {
      cardRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      gsap.fromTo(cardRef.current,
        { borderColor: 'rgba(99,102,241,0.06)', boxShadow: 'none' },
        { borderColor: 'rgba(99,102,241,0.55)', boxShadow: '0 0 32px rgba(99,102,241,0.18)', duration: 0.5, ease: 'power2.out' }
      );
    }
    prevStatus.current = phase.status;
  }, [phase.status]);

  const meta    = PHASE_META[phase.phase - 1];
  const isActive = phase.status !== 'pending';

  const borderColor =
    phase.status === 'running'  ? 'rgba(99,102,241,0.5)' :
    phase.status === 'complete' ? 'rgba(16,185,129,0.2)' :
    phase.status === 'paused'   ? 'rgba(251,191,36,0.4)' :
    'rgba(99,102,241,0.05)';

  const glowStyle =
    phase.status === 'running' ? '0 0 0 1px rgba(99,102,241,0.15), 0 8px 40px rgba(99,102,241,0.12), 0 0 60px rgba(99,102,241,0.06)' :
    phase.status === 'paused'  ? '0 0 24px rgba(251,191,36,0.1)' : 'none';

  const hasBody = phase.status === 'running' || phase.status === 'complete' || phase.status === 'paused';

  useEffect(() => {
    if (!bodyRef.current || !hasBody) return;
    if (collapsed) {
      gsap.to(bodyRef.current, { height: 0, opacity: 0, duration: 0.25, ease: 'power2.inOut' });
    } else {
      gsap.set(bodyRef.current, { height: 'auto' });
      const targetHeight = bodyRef.current.offsetHeight;
      gsap.fromTo(bodyRef.current,
        { height: 0, opacity: 0 },
        {
          height: targetHeight,
          opacity: 1,
          duration: 0.3,
          ease: 'power2.out',
          onComplete: () => {
            gsap.set(bodyRef.current, { height: 'auto' });
          },
        }
      );
    }
  }, [collapsed, hasBody]);

  return (
    <div ref={cardRef} className="relative">
      {/* Vertical connector to next */}
      {!isLast && (
        <div className="absolute left-[28px] top-[52px] w-0.5 h-[calc(100%_+_8px)] z-0 transition-all duration-700"
          style={{
            background: phase.status === 'complete'
              ? 'linear-gradient(to bottom, rgba(16,185,129,0.5), rgba(16,185,129,0.08))'
              : phase.status === 'running'
              ? 'linear-gradient(to bottom, rgba(99,102,241,0.6), rgba(99,102,241,0.08))'
              : 'linear-gradient(to bottom, rgba(99,102,241,0.06), transparent)',
          }} />
      )}

      <div
        className={`relative z-10 rounded-2xl overflow-hidden transition-all duration-500${phase.status === 'running' ? ' glow-pulse-anim' : ''}`}
        style={{
          background: phase.status === 'pending' ? 'rgba(5,5,12,0.6)' : 'rgba(8,8,18,0.92)',
          border: `1px solid ${borderColor}`,
          boxShadow: glowStyle,
          opacity: phase.status === 'pending' ? 0.4 : 1,
        }}
      >
        {/* Scanning progress bar (running only) */}
        {phase.status === 'running' && (
          <div className="absolute top-0 left-0 right-0 h-0.5 overflow-hidden">
            <div className="h-full shimmer-fast" style={{ background: 'linear-gradient(90deg, transparent, #818cf8, #a78bfa, transparent)' }} />
          </div>
        )}
        {/* Complete top accent */}
        {phase.status === 'complete' && (
          <div className="absolute top-0 left-0 right-0 h-px"
            style={{ background: 'linear-gradient(90deg, transparent, rgba(16,185,129,0.4), transparent)' }} />
        )}

        {/* Header */}
        <div className="flex items-center gap-4 px-5 py-4">
          {/* Phase number bubble */}
          <div className="w-11 h-11 rounded-xl flex flex-col items-center justify-center flex-shrink-0 text-xs font-black transition-all duration-500 relative"
            style={phase.status === 'complete' ? {
              background: 'rgba(16,185,129,0.1)', color: '#10b981',
              border: '1px solid rgba(16,185,129,0.25)',
              boxShadow: '0 0 16px rgba(16,185,129,0.15)',
            } : phase.status === 'running' ? {
              background: 'rgba(99,102,241,0.12)', color: '#818cf8',
              border: '1px solid rgba(99,102,241,0.4)',
              boxShadow: '0 0 20px rgba(99,102,241,0.2)',
            } : phase.status === 'paused' ? {
              background: 'rgba(251,191,36,0.1)', color: '#fbbf24',
              border: '1px solid rgba(251,191,36,0.3)',
            } : {
              background: 'rgba(99,102,241,0.03)', color: 'rgba(99,102,241,0.2)',
              border: '1px solid rgba(99,102,241,0.05)',
            }}>
            {String(phase.phase).padStart(2, '0')}
            {/* Pulse ring for running */}
            {phase.status === 'running' && (
              <div className="absolute inset-0 rounded-xl border border-[rgba(99,102,241,0.4)] ping-ring" />
            )}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-0.5">
              <h3 className="font-bold text-sm transition-colors"
                style={{ color: isActive ? '#f0f0fc' : 'rgba(99,102,241,0.25)' }}>
                {phase.name}
              </h3>
              {meta?.agent && isActive && (
                <span className="text-micro font-mono font-black px-2 py-0.5 rounded-md hidden sm:inline"
                  style={(() => {
                    const ac = agentColor(meta.agent);
                    return { color: ac.text, background: ac.bg, border: `1px solid ${ac.border}` };
                  })()}>
                  {meta.agent}
                </span>
              )}
            </div>
            <div className="text-xs truncate"
              style={{ color: isActive ? '#5a5a80' : 'rgba(99,102,241,0.12)' }}>
              {meta?.description}
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            {phase.status === 'running' && (
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-micro font-black uppercase tracking-widest"
                style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)', color: '#818cf8' }}>
                <span className="w-1.5 h-1.5 rounded-full bg-[#6366f1] dot-pulse" />
                live
              </div>
            )}
            {hasBody && (
              <button
                onClick={onToggleCollapse}
                aria-label={collapsed ? `Expand phase ${phase.phase}` : `Collapse phase ${phase.phase}`}
                className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors hover:bg-[rgba(99,102,241,0.08)]"
              >
                <ChevronDown className="w-4 h-4 text-[#818cf8] transition-transform duration-200" style={{ transform: collapsed ? 'rotate(-90deg)' : 'rotate(0deg)' }} />
              </button>
            )}
            <PhaseStatusIcon status={phase.status} />
          </div>
        </div>

        {hasBody && (
          <div ref={bodyRef} className="overflow-hidden" style={{ height: collapsed ? 0 : 'auto', opacity: collapsed ? 0 : 1 }}>
            {/* Output area */}
            {(phase.status === 'complete' || phase.status === 'paused') && (
              <div className="px-5 pb-5 pt-4 border-t" style={{ borderColor: 'rgba(99,102,241,0.06)' }}>
                {phase.phase === 1 && phase.document_analysis && (
                  <DocumentAnalysisOutput data={phase.document_analysis} />
                )}
                {phase.phase === 2 && phase.user_stories && (
                  <UserStoriesOutput stories={phase.user_stories} architecture={phase.architecture} />
                )}
                {phase.phase === 2 && phase.discussion && (
                  <DiscussionBlock discussion={phase.discussion} />
                )}
                {phase.phase === 3 && phase.clarifications && (
                  <ClarificationsOutput items={phase.clarifications} />
                )}
                {phase.phase === 4 && (
                  <SpecOutput
                    backendSpec={phase.backend_spec}
                    frontendSpec={phase.frontend_spec}
                    editable={isPaused && phase.status === 'paused'}
                    onSave={onSaveSpecs ? (b, f) => onSaveSpecs(phase.phase, b, f) : undefined}
                  />
                )}
                {phase.phase === 5 && phase.qa_report && (
                  <QAReportOutput report={phase.qa_report} />
                )}
                {phase.phase === 5 && phase.qa_discussion && (
                  <DiscussionBlock discussion={phase.qa_discussion} />
                )}
                {phase.phase === 6 && (
                  <SpecOutput
                    backendSpec={phase.backend_spec}
                    frontendSpec={phase.frontend_spec}
                    editable={isPaused && phase.status === 'paused'}
                    onSave={onSaveSpecs ? (b, f) => onSaveSpecs(phase.phase, b, f) : undefined}
                  />
                )}
                {phase.phase === 7 && phase.pm_evaluation && (
                  <PMEvaluationOutput evaluation={phase.pm_evaluation} coachEvent={phase.coach_event} />
                )}
                {phase.phase === 8 && phase.output_files && (
                  <OutputFilesOutput files={phase.output_files} />
                )}
                {phase.status === 'paused' && isPaused && (
                  <GuidedPauseBlock phase={phase.phase} onContinue={onContinue} />
                )}
              </div>
            )}

            {/* Running: show streaming log if available */}
            {phase.status === 'running' && (
              <div className="px-5 pb-4 pt-2 border-t" style={{ borderColor: 'rgba(99,102,241,0.06)' }}>
                <TerminalLog log={(phase as unknown as { raw_log?: string }).raw_log} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
});

// â”€â”€ Main Pipeline View â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export function PipelineView() {
  const { state, resumePipeline, dispatch } = useFactory();
  const { pipeline } = state;
  const headerRef = useRef<HTMLDivElement>(null);
  const [collapsedPhases, setCollapsedPhases] = useState<Record<number, boolean>>({});

  useEffect(() => {
    if (headerRef.current) {
      gsap.fromTo(headerRef.current,
        { y: -12, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.5, ease: 'power3.out' }
      );
    }
  }, []);

  if (!pipeline) return null;

  const isPaused        = state.stage === 'paused';
  const completedCount  = pipeline.phases.filter(p => p.status === 'complete').length;
  const progressPct     = Math.round((completedCount / 8) * 100);
  const runningPhase    = pipeline.phases.find(p => p.status === 'running');

  const handleSaveSpecs = useCallback((phaseNum: number, backend: string, frontend: string) => {
    dispatch({ type: 'PHASE_UPDATE', phase: phaseNum, result: { backend_spec: backend, frontend_spec: frontend } });
  }, [dispatch]);

  const togglePhase = useCallback((phaseNum: number) => {
    setCollapsedPhases(prev => ({ ...prev, [phaseNum]: !prev[phaseNum] }));
  }, []);

  return (
    <div className="space-y-3">
      {/* â”€â”€ Command header â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <div ref={headerRef}
        className="relative rounded-2xl overflow-hidden"
        style={{ background: 'rgba(8,8,18,0.95)', border: '1px solid rgba(99,102,241,0.14)', backdropFilter: 'blur(16px)' }}>
        {/* Top glow line */}
        <div className="absolute top-0 left-0 right-0 h-px"
          style={{ background: 'linear-gradient(90deg, transparent, rgba(99,102,241,0.5), rgba(139,92,246,0.5), transparent)' }} />

        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="relative w-9 h-9 rounded-xl flex items-center justify-center"
                style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)' }}>
                <Cpu className="w-4 h-4 text-[#818cf8]" />
                {state.stage === 'running' && (
                  <div className="absolute inset-0 rounded-xl border border-[rgba(99,102,241,0.4)] ping-ring" />
                )}
              </div>
              <div>
                <div className="text-sm font-bold text-[#f0f0fc] flex items-center gap-2">
                  Live Pipeline
                  {state.stage === 'running' && (
                    <span className="inline-flex items-center gap-1 text-micro font-black px-2 py-0.5 rounded-full uppercase tracking-widest"
                      style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)', color: '#818cf8' }}>
                      <Wifi className="w-2.5 h-2.5" /> streaming
                    </span>
                  )}
                  {state.stage === 'paused' && (
                    <span className="inline-flex items-center gap-1 text-micro font-black px-2 py-0.5 rounded-full uppercase tracking-widest"
                      style={{ background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.25)', color: '#fbbf24' }}>
                      <Pause className="w-2.5 h-2.5" /> paused
                    </span>
                  )}
                </div>
                <div className="text-micro text-[#5a5a80] flex items-center gap-1.5 mt-0.5">
                  <span>Phase {pipeline.current_phase} of 8</span>
                  {pipeline.retry_count > 0 && (
                    <span className="text-[#fbbf24]"> • Cycle {pipeline.current_cycle}</span>
                  )}
                  {runningPhase && (
                    <span className="text-[#818cf8]"> • {runningPhase.name}</span>
                  )}
                </div>
              </div>
            </div>

            {/* Phase dots strip */}
            <div className="hidden sm:flex items-center gap-1.5">
              {pipeline.phases.map((p) => (
                <div key={p.phase}
                  title={`Phase ${p.phase}: ${p.name}`}
                  className="rounded-full transition-all duration-500 cursor-default"
                  style={{
                    width: p.status === 'running' ? 28 : 8,
                    height: 8,
                    background:
                      p.status === 'complete' ? '#10b981' :
                      p.status === 'running'  ? 'linear-gradient(90deg, #6366f1, #8b5cf6)' :
                      p.status === 'paused'   ? '#fbbf24' :
                      'rgba(99,102,241,0.08)',
                    boxShadow: p.status === 'running' ? '0 0 8px rgba(99,102,241,0.5)' : 'none',
                  }} />
              ))}
              <span className="text-micro font-mono font-black text-[#6366f1] ml-0.5">{progressPct}%</span>
            </div>
          </div>

          {/* Progress bar */}
          <div className="relative h-1.5 rounded-full overflow-hidden"
            style={{ background: 'rgba(99,102,241,0.07)' }}>
            <div className="absolute inset-y-0 left-0 rounded-full transition-all duration-1000"
              style={{
                width: `${progressPct}%`,
                background: 'linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa)',
                boxShadow: '0 0 8px rgba(99,102,241,0.4)',
              }} />
            {/* Shimmer overlay on running */}
            {state.stage === 'running' && (
              <div className="absolute inset-0" style={{ background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent)', backgroundSize: '200% 100%', animation: 'shimmer 2s linear infinite' }} />
            )}
          </div>
        </div>
      </div>

      {/* â”€â”€ Phase cards â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <div className="space-y-2">
        {pipeline.phases.map((phase, i) => (
          <PhaseCard
            key={phase.phase}
            phase={phase}
            isPaused={isPaused && pipeline.paused_at_phase === phase.phase}
            onContinue={resumePipeline}
            onSaveSpecs={handleSaveSpecs}
            isLast={i === pipeline.phases.length - 1}
            collapsed={Boolean(collapsedPhases[phase.phase])}
            onToggleCollapse={() => togglePhase(phase.phase)}
          />
        ))}
      </div>
    </div>
  );
}
