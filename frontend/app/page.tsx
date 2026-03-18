'use client';

import { type ComponentType, type SVGProps, useEffect, useRef, useState } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Link from 'next/link';
import {
  ArrowRight, Zap, Brain, GitBranch, FileText, Shield,
  RefreshCw, ChevronDown, Cpu, Layers, FlaskConical,
  CheckCheck, Sparkles, TrendingUp, Lock, Code2,
  Eye, BookOpen, MessageCircle, FileCode, AlertTriangle, Wrench, Star, PackageCheck,
  Server, Monitor, DollarSign, List,
} from 'lucide-react';
import { ScanEyeIcon, MessagesSquareIcon, FolderGit2Icon, FileBadgeIcon } from '@/components/ui/icons';

gsap.registerPlugin(ScrollTrigger);

const PHASES: { n: string; name: string; agent: string; color: string; Icon: ComponentType<SVGProps<SVGSVGElement>>; desc: string }[] = [
  { n: '01', name: 'Document Parsing',    agent: 'VisionAgent',   color: '#22d3ee', Icon: ScanEyeIcon,        desc: 'Gemini reads your doc - extracts features, personas, ambiguities. Nothing is guessed.' },
  { n: '02', name: 'User Stories + Arch', agent: 'PM + TechLead', color: '#6366f1', Icon: BookOpen,           desc: 'PM writes user stories. TechLead designs the architecture. Both debate until aligned.' },
  { n: '03', name: 'Clarifications',      agent: 'DevTeam + PM',  color: '#8b5cf6', Icon: MessagesSquareIcon, desc: 'Dev raises real questions. PM resolves them. No silently ignoring ambiguities.' },
  { n: '04', name: 'Draft Specs',         agent: 'DevTeam',       color: '#a78bfa', Icon: FolderGit2Icon,     desc: 'Full backend and frontend specifications written, not summarized.' },
  { n: '05', name: 'QA Analysis',         agent: 'QAAgent',       color: '#f87171', Icon: AlertTriangle,      desc: 'Issues sorted by severity: critical -> high -> medium -> low -> security flags.' },
  { n: '06', name: 'Fixes Applied',       agent: 'DevTeam',       color: '#fb923c', Icon: Wrench,             desc: 'Every QA issue addressed. Specs revised. Team checks the fix made sense.' },
  { n: '07', name: 'PM Evaluation',       agent: 'PM + Coach',    color: '#fbbf24', Icon: Star,               desc: 'PM scores the output /100. Below 85 -> Coach extracts lessons -> retry starts.' },
  { n: '08', name: 'Output Saved',        agent: 'System',        color: '#10b981', Icon: FileBadgeIcon,      desc: '8 Markdown files ready: Executive Summary through Cost Estimation.' },
];

const OUTPUT_FILES: { Icon: ComponentType<SVGProps<SVGSVGElement>>; name: string; color: string }[] = [
  { Icon: FileText,   name: 'Executive Summary',  color: '#6366f1' },
  { Icon: Sparkles,   name: 'Master Prompt',      color: '#8b5cf6' },
  { Icon: List,       name: 'User Stories',       color: '#a78bfa' },
  { Icon: GitBranch,  name: 'Architecture',       color: '#22d3ee' },
  { Icon: Server,     name: 'Backend Spec',       color: '#10b981' },
  { Icon: Monitor,    name: 'Frontend Spec',      color: '#6366f1' },
  { Icon: Shield,     name: 'QA Report',          color: '#f87171' },
  { Icon: DollarSign, name: 'Cost Estimation',    color: '#fbbf24' },
];

/* Ã¢â€â‚¬Ã¢â€â‚¬ Particle canvas Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
function ParticleField() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let W = canvas.width  = window.innerWidth;
    let H = canvas.height = window.innerHeight;

    const particles = Array.from({ length: 70 }, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 1.2 + 0.3,
      vx: (Math.random() - 0.5) * 0.18,
      vy: (Math.random() - 0.5) * 0.18,
      alpha: Math.random() * 0.4 + 0.1,
    }));

    let animId: number;
    let frame = 0;

    function draw() {
      ctx!.clearRect(0, 0, W, H);
      frame++;
      for (const p of particles) {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
        if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
        const pulse = 0.8 + 0.2 * Math.sin(frame * 0.02 + p.x);
        ctx!.beginPath();
        ctx!.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx!.fillStyle = `rgba(99,102,241,${p.alpha * pulse})`;
        ctx!.fill();
      }
      // draw connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 100) {
            ctx!.beginPath();
            ctx!.moveTo(particles[i].x, particles[i].y);
            ctx!.lineTo(particles[j].x, particles[j].y);
            ctx!.strokeStyle = `rgba(99,102,241,${0.08 * (1 - dist / 100)})`;
            ctx!.lineWidth = 0.5;
            ctx!.stroke();
          }
        }
      }
      animId = requestAnimationFrame(draw);
    }

    draw();
    const onResize = () => {
      W = canvas.width  = window.innerWidth;
      H = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', onResize);
    return () => { cancelAnimationFrame(animId); window.removeEventListener('resize', onResize); };
  }, []);
  return <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" style={{ opacity: 0.6 }} />;
}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Magnetic button Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
function MagneticButton({ href, children, className, style }: { href: string; children: React.ReactNode; className?: string; style?: React.CSSProperties }) {
  const btnRef = useRef<HTMLAnchorElement>(null);

  const onMove = (e: React.MouseEvent<HTMLAnchorElement>) => {
    const el = btnRef.current; if (!el) return;
    const r  = el.getBoundingClientRect();
    const x  = e.clientX - r.left - r.width  / 2;
    const y  = e.clientY - r.top  - r.height / 2;
    gsap.to(el, { x: x * 0.25, y: y * 0.25, duration: 0.4, ease: 'power2.out' });
  };
  const onLeave = () => gsap.to(btnRef.current, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1,0.4)' });

  return (
    <Link ref={btnRef} href={href} className={className} style={style} onMouseMove={onMove} onMouseLeave={onLeave}>
      {children}
    </Link>
  );
}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Nav Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
function Nav() {
  const navRef   = useRef<HTMLElement>(null);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    if (!navRef.current) return;
    gsap.to(navRef.current, {
      background: scrolled ? 'rgba(2,2,8,0.92)' : 'transparent',
      borderBottomColor: scrolled ? 'rgba(99,102,241,0.15)' : 'rgba(99,102,241,0)',
      duration: 0.4,
    });
  }, [scrolled]);

  return (
    <nav
      ref={navRef}
      style={{ backdropFilter: scrolled ? 'blur(24px)' : 'none', borderBottom: '1px solid transparent', transition: 'backdrop-filter 0.4s' }}
      className="fixed top-0 left-0 right-0 z-50 px-6 md:px-8 py-4 flex items-center justify-between"
    >
      <div className="flex items-center gap-3">
        <div className="relative w-9 h-9 rounded-xl flex items-center justify-center"
          style={{ background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', boxShadow: '0 0 20px rgba(99,102,241,0.45)' }}>
          <Zap className="w-4.5 h-4.5 text-white" strokeWidth={2.5} style={{ width: 18, height: 18 }} />
          <div className="absolute inset-0 rounded-xl" style={{ background: 'linear-gradient(135deg, rgba(255,255,255,0.15), transparent)' }} />
        </div>
        <div>
          <div className="text-sm font-bold text-white tracking-tight leading-none">The AI Factory</div>
          <div className="text-micro text-[#5a5a80] uppercase tracking-widest leading-none mt-0.5">Multi-Agent MVP Generator</div>
        </div>
      </div>

      <div className="hidden md:flex items-center gap-1 p-1 rounded-xl"
        style={{ background: 'rgba(13,13,26,0.7)', border: '1px solid rgba(99,102,241,0.12)', backdropFilter: 'blur(8px)' }}>
        {['pipeline', 'evolution', 'modes', 'output'].map(id => (
          <a key={id} href={`#${id}`}
            className="px-4 py-1.5 rounded-lg text-xs text-[#5a5a80] hover:text-[#f0f0fc] hover:bg-[rgba(99,102,241,0.08)] transition-all capitalize tracking-wide font-medium">
            {id}
          </a>
        ))}
      </div>

      <MagneticButton href="/factory"
        className="group relative flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white overflow-hidden"
        style={{ background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', boxShadow: '0 0 24px rgba(99,102,241,0.4)' }}>
        <span className="relative z-10 flex items-center gap-2">
          Launch <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
        </span>
        <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg, rgba(255,255,255,0.1), transparent)' }} />
      </MagneticButton>
    </nav>
  );
}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Hero Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
function Hero() {
  const heroRef   = useRef<HTMLElement>(null);
  const headRef   = useRef<HTMLHeadingElement>(null);
  const subRef    = useRef<HTMLParagraphElement>(null);
  const ctaRef    = useRef<HTMLDivElement>(null);
  const statsRef  = useRef<HTMLDivElement>(null);
  const gridRef   = useRef<HTMLDivElement>(null);
  const orb1Ref   = useRef<HTMLDivElement>(null);
  const orb2Ref   = useRef<HTMLDivElement>(null);
  const orb3Ref   = useRef<HTMLDivElement>(null);
  const chipRef   = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    // Initial stagger entrance
    const tl = gsap.timeline({ delay: 0.1 });
    tl.from(chipRef.current,  { y: -20, opacity: 0, duration: 0.6, ease: 'power3.out' })
      .from(headRef.current,  { y: 60, opacity: 0, duration: 1.2, ease: 'power4.out' }, '-=0.3')
      .from(subRef.current,   { y: 30, opacity: 0, duration: 0.9, ease: 'power3.out' }, '-=0.7')
      .from(ctaRef.current,   { y: 20, opacity: 0, duration: 0.7, ease: 'power3.out' }, '-=0.5')
      .from(statsRef.current?.querySelectorAll('.stat-item') ?? [], {
        y: 20, opacity: 0, duration: 0.6, stagger: 0.08, ease: 'power2.out',
      }, '-=0.4');

    // Parallax
    gsap.to(gridRef.current, {
      yPercent: 30, ease: 'none',
      scrollTrigger: { trigger: heroRef.current, start: 'top top', end: 'bottom top', scrub: true },
    });
    gsap.to(orb1Ref.current, {
      y: -80, ease: 'none',
      scrollTrigger: { trigger: heroRef.current, start: 'top top', end: 'bottom top', scrub: 1.5 },
    });
    gsap.to(orb2Ref.current, {
      y: -50, ease: 'none',
      scrollTrigger: { trigger: heroRef.current, start: 'top top', end: 'bottom top', scrub: 2 },
    });
  }, { scope: heroRef });

  const stats = [
    { v: '8',  s: '',     l: 'AI Agent Phases' },
    { v: '3',  s: 'x',    l: 'Self-Improvement Cycles' },
    { v: '85', s: '+',   l: 'Min PM Score to Ship' },
    { v: '8',  s: '',     l: 'Markdown Files Out' },
  ];

  return (
    <section ref={heroRef} className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden px-6 pt-24 pb-16">
      {/* Layers */}
      <div ref={gridRef} className="absolute inset-0 grid-bg" />
      <div className="absolute inset-0 dot-bg opacity-30" />
      <ParticleField />

      {/* Radial glows */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_90%_60%_at_50%_30%,rgba(99,102,241,0.12),transparent)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_40%_30%_at_80%_70%,rgba(139,92,246,0.08),transparent)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_30%_20%_at_20%_60%,rgba(34,211,238,0.05),transparent)]" />

      {/* Top fade */}
      <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-[#020208] to-transparent" />

      {/* Ambient orbs */}
      <div ref={orb1Ref} className="absolute top-[15%] left-[8%] w-[600px] h-[600px] rounded-full blur-[120px] orb-drift"
        style={{ background: 'radial-gradient(circle, rgba(99,102,241,0.07) 0%, transparent 70%)' }} />
      <div ref={orb2Ref} className="absolute top-[35%] right-[5%] w-[450px] h-[450px] rounded-full blur-[100px] orb-drift-slow"
        style={{ background: 'radial-gradient(circle, rgba(139,92,246,0.07) 0%, transparent 70%)' }} />
      <div ref={orb3Ref} className="absolute bottom-[10%] left-[35%] w-[300px] h-[300px] rounded-full blur-[80px]"
        style={{ background: 'radial-gradient(circle, rgba(34,211,238,0.05) 0%, transparent 70%)' }} />

      {/* Content */}
      <div className="relative z-10 text-center max-w-5xl mx-auto w-full">

        {/* Badge chip */}
        <div ref={chipRef} className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full mb-8"
          style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.28)', boxShadow: '0 0 20px rgba(99,102,241,0.1)' }}>
          <span className="relative flex items-center justify-center w-2 h-2">
            <span className="absolute inline-flex w-full h-full rounded-full bg-[#6366f1] ping-ring" />
            <span className="relative w-2 h-2 rounded-full bg-[#818cf8]" />
          </span>
          <span className="text-xs font-bold text-[#818cf8] uppercase tracking-widest">Multi-Agent MVP Generator</span>
          <span className="hidden sm:inline text-xs text-[#5a5a80]">&middot;</span>
          <span className="hidden sm:inline text-xs text-[#5a5a80]">Powered by Gemini</span>
        </div>

        {/* Headline */}
        <h1 ref={headRef} className="text-5xl sm:text-7xl lg:text-[92px] font-black tracking-tighter leading-[0.92] mb-6">
          <span className="text-gradient-hero gradient-animate block">Turn raw requirements</span>
          <span className="text-[#f0f0fc] block">into production</span>
          <span className="relative inline-block">
            <span className="text-gradient-indigo gradient-animate">specs.</span>
            <span className="absolute -right-4 bottom-1 w-3 h-3 rounded-full bg-[#6366f1] dot-pulse opacity-70" />
          </span>
        </h1>

        {/* Subtext */}
        <p ref={subRef} className="text-lg md:text-xl text-[#5a5a80] max-w-2xl mx-auto leading-relaxed mb-10">
          Eight AI agents collaborate, argue, self-evaluate, and learn in real time.
          You get a complete technical MVP package -
          <em className="text-[#a0a0c0] not-italic font-medium"> not a draft, a production-grade spec your team can ship from day one.</em>
        </p>

        {/* CTAs */}
        <div ref={ctaRef} className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20">
          <MagneticButton href="/factory"
            className="group relative flex items-center gap-3 px-8 py-4 rounded-2xl text-base font-bold text-white overflow-hidden btn-primary"
            style={{ boxShadow: '0 0 0 1px rgba(99,102,241,0.4), 0 8px 40px rgba(99,102,241,0.4)' }}>
            <span className="relative z-10 flex items-center gap-3">
              <Zap className="w-5 h-5" strokeWidth={2.5} />
              Build your MVP spec
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1.5" />
            </span>
          </MagneticButton>
          <a href="#pipeline"
            className="flex items-center gap-2.5 px-8 py-4 rounded-2xl text-base font-semibold btn-ghost">
            How it works
            <ChevronDown className="w-4 h-4 animate-bounce" />
          </a>
        </div>

        {/* Stats */}
        <div ref={statsRef} className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
          {stats.map(({ v, s, l }) => (
            <div key={l} className="stat-item relative p-5 rounded-2xl text-center overflow-hidden"
              style={{ background: 'rgba(13,13,26,0.8)', border: '1px solid rgba(99,102,241,0.12)', backdropFilter: 'blur(8px)' }}>
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_0%,rgba(99,102,241,0.07),transparent)]" />
              <div className="relative z-10">
                <div className="text-4xl font-black leading-none mb-1">
                  <span className="text-gradient-indigo">{v}</span>
                  <span className="text-xl text-[#5a5a80]">{s}</span>
                </div>
                <div className="text-micro text-[#5a5a80] uppercase tracking-widest leading-tight">{l}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Floating accent cards */}
      <div className="absolute left-4 xl:left-12 top-1/2 -translate-y-1/2 hidden xl:block">
        <div className="glass p-4 rounded-2xl w-52 shadow-2xl">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.3)' }}>
              <Brain className="w-4 h-4 text-[#818cf8]" />
            </div>
            <span className="text-xs font-bold text-[#f0f0fc]">Agents Active</span>
          </div>
          <div className="space-y-2">
            {['PMAgent', 'DevTeam', 'QAAgent'].map((a, i) => (
              <div key={a} className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: ['#6366f1','#a78bfa','#f87171'][i], animation: 'pulse-dot 1.6s ease-in-out infinite', animationDelay: `${i * 0.3}s` }} />
                <span className="text-2xs text-[#5a5a80] font-mono">{a}</span>
                <span className="ml-auto text-micro text-[#10b981] font-bold uppercase">LIVE</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="absolute right-4 xl:right-12 top-1/2 -translate-y-1/2 hidden xl:block">
        <div className="glass p-4 rounded-2xl w-52 shadow-2xl" style={{ borderColor: 'rgba(16,185,129,0.2)' }}>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.3)' }}>
              <Shield className="w-4 h-4 text-[#10b981]" />
            </div>
            <span className="text-xs font-bold text-[#f0f0fc]">PM Gatekeeper</span>
          </div>
          <div className="flex items-baseline gap-1 mb-1">
            <span className="text-3xl font-black text-[#10b981]">85</span>
            <span className="text-sm text-[#5a5a80]">/100 min</span>
          </div>
          <p className="text-micro text-[#5a5a80] leading-relaxed">Below threshold -&gt; Coach learns -&gt; pipeline retries</p>
        </div>
      </div>

      {/* Scroll cue */}
      <a href="#pipeline" className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-[#353560] hover:text-[#a0a0c0] transition-all group z-10">
        <span className="text-micro uppercase tracking-[0.2em] font-bold group-hover:text-[#818cf8] transition-colors">Explore Pipeline</span>
        <div className="w-5 h-8 rounded-full border border-[rgba(99,102,241,0.25)] flex items-start justify-center pt-1.5 group-hover:border-[rgba(99,102,241,0.5)] transition-colors">
          <div className="w-1 h-2 rounded-full bg-[#6366f1] animate-bounce" />
        </div>
      </a>
    </section>
  );
}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Ticker Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
function Ticker() {
  const items = ['VisionAgent parsing requirements', 'PMAgent writing user stories', 'TechLead designing architecture', 'DevTeam drafting backend spec', 'QAAgent running analysis', 'Coach updating playbooks', 'PM evaluating score', 'System saving outputs'];
  return (
    <div className="relative overflow-hidden py-3 border-y" style={{ borderColor: 'rgba(99,102,241,0.1)', background: 'rgba(13,13,26,0.5)' }}>
      <div className="absolute left-0 top-0 bottom-0 w-16 z-10" style={{ background: 'linear-gradient(to right, #020208, transparent)' }} />
      <div className="absolute right-0 top-0 bottom-0 w-16 z-10" style={{ background: 'linear-gradient(to left, #020208, transparent)' }} />
      <div className="flex gap-8 whitespace-nowrap">
        <div className="flex gap-8 ticker-anim">
          {[...items, ...items].map((item, i) => (
            <span key={i} className="flex items-center gap-2 text-2xs text-[#353560] uppercase tracking-widest font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-[#6366f1]" />
              {item}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Pipeline Section Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
function PipelineSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const headRef    = useRef<HTMLDivElement>(null);
  const timelineRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    gsap.from(headRef.current, {
      y: 40, opacity: 0, duration: 1,
      scrollTrigger: { trigger: headRef.current, start: 'top 88%', toggleActions: 'play none none none' },
    });

    const cards = timelineRef.current?.querySelectorAll('.phase-item');
    if (cards) {
      gsap.from(cards, {
        opacity: 0, x: (i) => i % 2 === 0 ? -40 : 40,
        duration: 0.7, stagger: 0.1, ease: 'power3.out',
        scrollTrigger: { trigger: timelineRef.current, start: 'top 80%', toggleActions: 'play none none none' },
      });
    }
  }, { scope: sectionRef });

  return (
    <section id="pipeline" ref={sectionRef} className="relative py-32 px-6 overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_50%_60%_at_15%_50%,rgba(99,102,241,0.05),transparent)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_40%_50%_at_85%_50%,rgba(139,92,246,0.04),transparent)]" />

      <div className="max-w-6xl mx-auto relative z-10">
        {/* Header */}
        <div ref={headRef} className="text-center mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6"
            style={{ background: 'rgba(99,102,241,0.07)', border: '1px solid rgba(99,102,241,0.2)' }}>
            <GitBranch className="w-3.5 h-3.5 text-[#6366f1]" />
            <span className="text-2xs font-bold text-[#818cf8] uppercase tracking-widest">The Pipeline</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-[#f0f0fc] tracking-tighter mb-5 leading-tight">
            Eight phases.<br />
            <span className="text-gradient-indigo">Every step is real work.</span>
          </h2>
          <p className="text-[#5a5a80] max-w-2xl mx-auto text-lg leading-relaxed">
            Nothing is skipped, abbreviated, or hallucinated into confidence.
            Each agent receives only what the previous one produced.
          </p>
        </div>

        {/* Timeline grid */}
        <div ref={timelineRef} className="relative">
          {/* Center spine */}
          <div className="absolute left-1/2 top-0 bottom-0 w-px hidden md:block"
            style={{ background: 'linear-gradient(to bottom, transparent, rgba(99,102,241,0.3) 10%, rgba(99,102,241,0.3) 90%, transparent)' }} />

          <div className="grid md:grid-cols-2 gap-3 md:gap-6">
            {PHASES.map((phase, i) => (
              <div key={phase.n}
                className={`phase-item group relative ${i % 2 === 0 ? 'md:pr-8' : 'md:pl-8 md:col-start-2'} ${i % 2 !== 0 ? '' : ''}`}>
                {/* Timeline dot Ã¢â‚¬â€ only on md+ */}
                <div className="hidden md:flex absolute items-center justify-center"
                  style={{
                    [i % 2 === 0 ? 'right' : 'left']: '-24px',
                    top: '50%', transform: 'translateY(-50%)',
                    width: 12, height: 12, borderRadius: '50%',
                    background: phase.color, boxShadow: `0 0 12px ${phase.color}80`,
                  }} />

                <div className="relative p-5 rounded-2xl overflow-hidden card-hover cursor-default"
                  style={{ background: 'rgba(13,13,26,0.85)', border: `1px solid rgba(99,102,241,0.1)`, backdropFilter: 'blur(8px)' }}>
                  {/* Hover corner glow */}
                  <div className="absolute top-0 right-0 w-40 h-40 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-3xl"
                    style={{ background: `${phase.color}18` }} />
                  {/* Left accent line */}
                  <div className="absolute left-0 top-0 bottom-0 w-0.5 rounded-r-full"
                    style={{ background: `linear-gradient(to bottom, transparent, ${phase.color}80, transparent)` }} />

                  <div className="relative z-10 flex items-start gap-4">
                    <div className="flex-shrink-0 w-12 h-12 rounded-2xl flex flex-col items-center justify-center"
                      style={{ background: `${phase.color}18`, border: `1px solid ${phase.color}35`, boxShadow: `0 0 16px ${phase.color}25` }}>
                      <phase.Icon className="w-5 h-5" style={{ color: phase.color }} />
                      <span className="text-micro font-black text-white/50 mt-0.5">{phase.n}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                        <h3 className="font-bold text-sm text-[#f0f0fc] leading-tight">{phase.name}</h3>
                        <span className="text-micro font-mono font-bold px-2 py-0.5 rounded-md border"
                          style={{ color: phase.color, background: `${phase.color}12`, borderColor: `${phase.color}30` }}>
                          {phase.agent}
                        </span>
                      </div>
                      <p className="text-xs text-[#5a5a80] leading-relaxed">{phase.desc}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom callout */}
        <div className="mt-16 relative p-8 rounded-3xl overflow-hidden"
          style={{ background: 'rgba(8,8,15,0.9)', border: '1px solid rgba(139,92,246,0.2)', backdropFilter: 'blur(16px)' }}>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_70%_80%_at_50%_50%,rgba(139,92,246,0.06),transparent)]" />
          <div className="absolute top-0 left-0 right-0 h-px" style={{ background: 'linear-gradient(90deg, transparent, rgba(139,92,246,0.5), transparent)' }} />
          <div className="relative z-10 text-center">
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-4"
              style={{ background: 'rgba(139,92,246,0.12)', border: '1px solid rgba(139,92,246,0.25)', boxShadow: '0 0 20px rgba(139,92,246,0.15)' }}>
              <FlaskConical className="w-6 h-6 text-[#a78bfa]" />
            </div>
            <h3 className="text-xl font-bold text-[#f0f0fc] mb-2">Agents debate in the open</h3>
            <p className="text-[#5a5a80] max-w-2xl mx-auto text-sm leading-relaxed">
              After phases 2 and 5, the team holds a live discussion - you see which agents are involved,
              what the debate is about, and what conclusion they reach. No black boxes.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Evolution Section Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
function EvolutionSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const headRef    = useRef<HTMLDivElement>(null);
  const cycleRef   = useRef<HTMLDivElement>(null);
  const cardsRef   = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    gsap.from(headRef.current, {
      y: 40, opacity: 0, duration: 1,
      scrollTrigger: { trigger: headRef.current, start: 'top 86%', toggleActions: 'play none none none' },
    });
    gsap.from(cycleRef.current, {
      x: -50, opacity: 0, duration: 0.9, ease: 'power3.out',
      scrollTrigger: { trigger: cycleRef.current, start: 'top 80%', toggleActions: 'play none none none' },
    });
    gsap.from(cardsRef.current?.querySelectorAll('.evo-card') ?? [], {
      y: 30, opacity: 0, duration: 0.7, stagger: 0.15, ease: 'power3.out',
      scrollTrigger: { trigger: cardsRef.current, start: 'top 82%', toggleActions: 'play none none none' },
    });
  }, { scope: sectionRef });

  const cycleSteps = [
    { icon: <AlertTriangle className="w-5 h-5" />, label: 'PM rejects below 85', sub: 'Spec does not meet quality bar', color: '#f87171' },
    { icon: <Brain className="w-5 h-5" />,         label: 'Coach extracts lessons', sub: 'Specific rules written to each playbook', color: '#a78bfa' },
    { icon: <BookOpen className="w-5 h-5" />,      label: 'Playbooks updated', sub: 'Every agent learns from the failure', color: '#818cf8' },
    { icon: <RefreshCw className="w-5 h-5" />,     label: 'Pipeline retries', sub: 'Phase 4 restarts with failure memory', color: '#fbbf24' },
  ];

  return (
    <section id="evolution" ref={sectionRef} className="relative py-32 px-6 overflow-hidden">
      {/* Big blurred circle */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[600px] rounded-full blur-[120px]"
        style={{ background: 'radial-gradient(circle, rgba(99,102,241,0.05) 0%, transparent 70%)' }} />

      <div className="max-w-6xl mx-auto relative z-10">
        <div ref={headRef} className="max-w-3xl mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6"
            style={{ background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.22)' }}>
            <Brain className="w-3.5 h-3.5 text-[#a78bfa]" />
            <span className="text-2xs font-bold text-[#a78bfa] uppercase tracking-widest">Self-Evolution</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-[#f0f0fc] tracking-tighter mb-5 leading-tight">
            The system gets smarter<br />
            <span className="text-gradient-indigo">every time it fails.</span>
          </h2>
          <p className="text-[#5a5a80] text-lg leading-relaxed">
            When the PM rejects a spec, a Coach agent dissects why, writes specific rules into each agent&apos;s
            permanent playbook, and the pipeline retries - informed by every previous mistake.
            <strong className="text-[#a0a0c0] font-medium"> The lessons stay forever.</strong>
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 items-start">
          {/* Cycle diagram */}
          <div ref={cycleRef} className="relative rounded-3xl overflow-hidden"
            style={{ background: 'rgba(13,13,26,0.9)', border: '1px solid rgba(139,92,246,0.2)', backdropFilter: 'blur(16px)' }}>
            <div className="absolute top-0 left-0 right-0 h-px" style={{ background: 'linear-gradient(90deg, transparent, rgba(139,92,246,0.5), transparent)' }} />
            <div className="p-7">
              <div className="text-micro font-bold text-[#5a5a80] uppercase tracking-widest mb-6 flex items-center gap-2">
                <RefreshCw className="w-3 h-3 text-[#6366f1]" />
                Rejection -&gt; Learn -&gt; Retry Loop
              </div>
              <div className="relative space-y-2">
                <div className="absolute left-[22px] top-8 bottom-8 w-px"
                  style={{ background: 'linear-gradient(to bottom, #f87171, #a78bfa, #818cf8, #fbbf24)', opacity: 0.4 }} />
                {cycleSteps.map((step, i) => (
                  <div key={i} className="group flex items-start gap-4 p-3 rounded-2xl transition-all hover:bg-[rgba(99,102,241,0.04)]">
                    <div className="w-11 h-11 rounded-xl flex items-center justify-center text-xl flex-shrink-0 z-10 transition-transform group-hover:scale-110"
                      style={{ background: `${step.color}12`, border: `1px solid ${step.color}30` }}>
                      <span style={{ color: step.color }}>{step.icon}</span>
                    </div>
                    <div className="flex-1 pt-1">
                      <div className="text-sm font-bold mb-0.5" style={{ color: step.color }}>{step.label}</div>
                      <div className="text-xs text-[#5a5a80]">{step.sub}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Feature cards */}
          <div ref={cardsRef} className="space-y-3">
            {[
              {
                icon: <RefreshCw className="w-5 h-5 text-[#6366f1]" />,
                color: '#6366f1',
                title: 'Up to 3 retry cycles',
                desc: 'Phases 4-7 repeat on rejection. Each restart carries previous cycle\'s rejection notes directly into the draft prompts.',
              },
              {
                icon: <FileText className="w-5 h-5 text-[#8b5cf6]" />,
                color: '#8b5cf6',
                title: 'Persistent playbooks',
                desc: 'Rules are not session memory - they are written to Markdown files. PM, TechLead, DevTeam, QA, and Coach each have their own accumulating playbook.',
              },
              {
                icon: <TrendingUp className="w-5 h-5 text-[#10b981]" />,
                color: '#10b981',
                title: 'Measurable evolution',
                desc: 'The app tracks total rules per playbook - learned vs. hand-written - so you always know exactly how experienced your AI team has become.',
              },
              {
                icon: <Lock className="w-5 h-5 text-[#fbbf24]" />,
                color: '#fbbf24',
                title: 'Lessons persist across projects',
                desc: 'When you start a new project, all previous lesson playbooks are still active. Your AI team remembers every failure.',
              },
            ].map(({ icon, color, title, desc }) => (
              <div key={title} className="evo-card group relative p-5 rounded-2xl overflow-hidden card-hover cursor-default"
                style={{ background: 'rgba(13,13,26,0.85)', border: `1px solid ${color}18`, backdropFilter: 'blur(8px)' }}>
                <div className="absolute right-0 top-0 bottom-0 w-1 rounded-l-full opacity-40"
                  style={{ background: `linear-gradient(to bottom, transparent, ${color}, transparent)` }} />
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-transform group-hover:scale-110"
                    style={{ background: `${color}12`, border: `1px solid ${color}25` }}>
                    {icon}
                  </div>
                  <div>
                    <h4 className="font-bold text-sm text-[#f0f0fc] mb-1">{title}</h4>
                    <p className="text-xs text-[#5a5a80] leading-relaxed">{desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Modes Section Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
function ModesSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const headRef    = useRef<HTMLDivElement>(null);
  const cardsRef   = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    gsap.from(headRef.current, {
      y: 40, opacity: 0, duration: 1,
      scrollTrigger: { trigger: headRef.current, start: 'top 86%', toggleActions: 'play none none none' },
    });
    gsap.from(cardsRef.current?.querySelectorAll('.mode-card') ?? [], {
      y: 50, opacity: 0, duration: 0.8, stagger: 0.2, ease: 'power3.out',
      scrollTrigger: { trigger: cardsRef.current, start: 'top 82%', toggleActions: 'play none none none' },
    });
  }, { scope: sectionRef });

  return (
    <section id="modes" ref={sectionRef} className="relative py-32 px-6">
      <div className="max-w-6xl mx-auto">
        <div ref={headRef} className="text-center mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6"
            style={{ background: 'rgba(99,102,241,0.07)', border: '1px solid rgba(99,102,241,0.18)' }}>
            <Layers className="w-3.5 h-3.5 text-[#6366f1]" />
            <span className="text-2xs font-bold text-[#818cf8] uppercase tracking-widest">Operating Modes</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-[#f0f0fc] tracking-tighter mb-5 leading-tight">
            Your level of control.<br />
            <span className="text-gradient-indigo">Your choice.</span>
          </h2>
          <p className="text-[#5a5a80] max-w-xl mx-auto text-lg leading-relaxed">
            Pick the mode at the start. It changes not just speed - it changes your entire experience.
          </p>
        </div>

        <div ref={cardsRef} className="grid md:grid-cols-2 gap-6">
          {/* Auto */}
          <div className="mode-card group relative p-8 rounded-3xl overflow-hidden card-hover"
            style={{ background: 'rgba(13,13,26,0.9)', border: '1px solid rgba(99,102,241,0.18)', backdropFilter: 'blur(16px)' }}>
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_70%_60%_at_90%_10%,rgba(99,102,241,0.08),transparent)]" />
            <div className="absolute bottom-0 right-0 w-48 h-48 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700"
              style={{ background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)' }} />
            <div className="relative z-10">
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-6 transition-transform group-hover:scale-110"
                style={{ background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.3)', boxShadow: '0 0 20px rgba(99,102,241,0.15)' }}>
                <Zap className="w-7 h-7 text-[#6366f1]" strokeWidth={2} />
              </div>
              <h3 className="text-2xl font-black text-[#f0f0fc] mb-3">Fully Automated</h3>
              <p className="text-[#5a5a80] mb-6 leading-relaxed text-sm">
                Fire and watch. All 8 phases run uninterrupted. Every agent output streams live -
                discussions, evaluations, retry cycles - no action needed from you.
              </p>
              <ul className="space-y-3">
                {['All 8 phases run end-to-end without pause', 'Real-time agent output streams to screen', 'Retries happen automatically on rejection', 'Best for trusted requirements documents'].map(item => (
                  <li key={item} className="flex items-start gap-3 text-sm text-[#5a5a80]">
                    <CheckCheck className="w-4 h-4 text-[#6366f1] mt-0.5 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Guided - featured */}
          <div className="mode-card group relative p-8 rounded-3xl overflow-hidden card-hover"
            style={{ background: 'rgba(13,13,26,0.9)', border: '1px solid rgba(139,92,246,0.35)', backdropFilter: 'blur(16px)', boxShadow: '0 0 0 1px rgba(139,92,246,0.1), 0 8px 40px rgba(139,92,246,0.1)' }}>
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_70%_60%_at_90%_10%,rgba(139,92,246,0.1),transparent)]" />
            <div className="absolute top-0 left-0 right-0 h-px" style={{ background: 'linear-gradient(90deg, transparent, rgba(139,92,246,0.6), transparent)' }} />
            <div className="absolute bottom-0 right-0 w-48 h-48 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700"
              style={{ background: 'radial-gradient(circle, rgba(139,92,246,0.2) 0%, transparent 70%)' }} />
            <div className="absolute top-4 right-4 px-3 py-1 rounded-full text-micro font-black uppercase tracking-widest"
              style={{ background: 'linear-gradient(135deg, rgba(139,92,246,0.2), rgba(99,102,241,0.15))', border: '1px solid rgba(139,92,246,0.35)', color: '#a78bfa' }}>
              Recommended
            </div>
            <div className="relative z-10">
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-6 transition-transform group-hover:scale-110"
                style={{ background: 'rgba(139,92,246,0.12)', border: '1px solid rgba(139,92,246,0.35)', boxShadow: '0 0 24px rgba(139,92,246,0.2)' }}>
                <Brain className="w-7 h-7 text-[#8b5cf6]" strokeWidth={2} />
              </div>
              <h3 className="text-2xl font-black text-[#f0f0fc] mb-3">Guided Review</h3>
              <p className="text-[#5a5a80] mb-6 leading-relaxed text-sm">
                The pipeline pauses at critical junctures. Review architecture, edit draft specs,
                validate QA findings - then continue. Your judgment shapes the output.
              </p>
              <ul className="space-y-3">
                {['Pauses after Phase 2 to review architecture', 'Editable draft specs before QA runs', 'Review QA issues before fixes apply', 'Edit final specs before PM scores them'].map(item => (
                  <li key={item} className="flex items-start gap-3 text-sm text-[#5a5a80]">
                    <CheckCheck className="w-4 h-4 text-[#8b5cf6] mt-0.5 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Output Section Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
function OutputSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const headRef    = useRef<HTMLDivElement>(null);
  const filesRef   = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    gsap.from(headRef.current, {
      y: 40, opacity: 0, duration: 1,
      scrollTrigger: { trigger: headRef.current, start: 'top 86%', toggleActions: 'play none none none' },
    });
    gsap.from(filesRef.current?.querySelectorAll('.file-card') ?? [], {
      y: 30, opacity: 0, scale: 0.95, duration: 0.55, stagger: 0.07, ease: 'power3.out',
      scrollTrigger: { trigger: filesRef.current, start: 'top 82%', toggleActions: 'play none none none' },
    });
  }, { scope: sectionRef });

  return (
    <section id="output" ref={sectionRef} className="relative py-32 px-6 overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_70%_50%,rgba(16,185,129,0.05),transparent)]" />

      <div className="max-w-6xl mx-auto relative z-10">
        <div ref={headRef} className="text-center mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6"
            style={{ background: 'rgba(16,185,129,0.07)', border: '1px solid rgba(16,185,129,0.22)' }}>
            <FileText className="w-3.5 h-3.5 text-[#10b981]" />
            <span className="text-2xs font-bold text-[#34d399] uppercase tracking-widest">The Output</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-[#f0f0fc] tracking-tighter mb-5 leading-tight">
            Eight files.<br />
            <span className="text-gradient-emerald">Ready for your dev team.</span>
          </h2>
          <p className="text-[#5a5a80] max-w-xl mx-auto text-lg leading-relaxed">
            Not a presentation. Not a summary.
            A structured, version-controlled folder your engineers can read on day one.
          </p>
        </div>

        <div ref={filesRef} className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {OUTPUT_FILES.map((file, i) => (
            <div key={file.name}
              className="file-card group relative p-6 rounded-2xl overflow-hidden card-hover cursor-default"
              style={{ background: 'rgba(13,13,26,0.88)', border: `1px solid ${file.color}15`, backdropFilter: 'blur(8px)' }}>
              <div className="absolute top-0 right-0 w-24 h-24 blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                style={{ background: `${file.color}25` }} />
              <div className="absolute bottom-0 left-0 right-0 h-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                style={{ background: `linear-gradient(90deg, transparent, ${file.color}60, transparent)` }} />
              <div className="relative z-10">
                <file.Icon className="w-8 h-8 mb-4 transition-transform duration-300 group-hover:scale-110 group-hover:-translate-y-1" style={{ color: file.color }} />
                <div className="text-micro font-black mb-2 font-mono uppercase tracking-widest"
                  style={{ color: file.color }}>{String(i).padStart(2, '0')}</div>
                <h4 className="font-bold text-sm text-[#f0f0fc] leading-tight">{file.name}</h4>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* Ã¢â€â‚¬Ã¢â€â‚¬ CTA Section Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
function CTASection() {
  const sectionRef = useRef<HTMLElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    gsap.from(contentRef.current, {
      y: 60, opacity: 0, duration: 1.2, ease: 'power3.out',
      scrollTrigger: { trigger: contentRef.current, start: 'top 82%', toggleActions: 'play none none none' },
    });
  }, { scope: sectionRef });

  return (
    <section ref={sectionRef} className="relative py-40 px-6 overflow-hidden">
      <div className="absolute inset-0 grid-bg opacity-50" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_70%_at_50%_50%,rgba(99,102,241,0.1),transparent)]" />
      <div className="absolute top-0 left-0 right-0 h-40 bg-gradient-to-b from-[#020208] to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 h-40 bg-gradient-to-t from-[#020208] to-transparent" />

      {/* Decorative rings */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full"
        style={{ border: '1px solid rgba(99,102,241,0.06)', animation: 'breath 6s ease-in-out infinite' }} />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full"
        style={{ border: '1px solid rgba(99,102,241,0.04)', animation: 'breath 6s ease-in-out 1s infinite' }} />

      <div ref={contentRef} className="relative z-10 max-w-3xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-8"
          style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.22)', boxShadow: '0 0 20px rgba(99,102,241,0.08)' }}>
          <Cpu className="w-3.5 h-3.5 text-[#6366f1]" />
          <span className="text-2xs font-bold text-[#818cf8] uppercase tracking-widest">Start Building</span>
        </div>
        <h2 className="text-5xl md:text-7xl font-black tracking-tighter text-[#f0f0fc] mb-6 leading-tight">
          Your requirements.<br />
          <span className="text-gradient-indigo">Their specs.</span>
        </h2>
        <p className="text-xl text-[#5a5a80] mb-12 leading-relaxed max-w-2xl mx-auto">
          Paste your requirements or upload a document.
          Watch eight agents build your complete technical MVP package.
        </p>
        <MagneticButton href="/factory"
          className="group inline-flex items-center gap-3 px-10 py-5 rounded-2xl text-lg font-bold text-white overflow-hidden btn-primary"
          style={{ boxShadow: '0 0 0 1px rgba(99,102,241,0.4), 0 12px 60px rgba(99,102,241,0.5)' }}>
          <span className="relative z-10 flex items-center gap-3">
            <Sparkles className="w-5 h-5 transition-transform group-hover:rotate-12" />
            Start building your spec
            <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1.5" />
          </span>
        </MagneticButton>
        <p className="mt-5 text-sm text-[#353560]">No account required. Bring your own API keys.</p>
      </div>
    </section>
  );
}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Footer Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
function Footer() {
  return (
    <footer style={{ borderTop: '1px solid rgba(99,102,241,0.08)' }} className="px-8 py-8">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg,#6366f1,#8b5cf6)' }}>
            <Zap className="w-4 h-4 text-white" strokeWidth={2.5} />
          </div>
          <span className="text-sm font-bold text-[#5a5a80]">The AI Factory</span>
        </div>
        <div className="flex items-center gap-6 text-xs text-[#353560]">
          <span className="flex items-center gap-1.5">
            <Code2 className="w-3 h-3" /> Multi-agent architecture
          </span>
          <span className="flex items-center gap-1.5">
            <Brain className="w-3 h-3" /> Self-evolving
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-[#353560]">
          <span className="relative flex items-center justify-center w-2 h-2">
            <span className="absolute inline-flex w-full h-full rounded-full bg-[#10b981] ping-ring" />
            <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
          </span>
          <span>All systems operational</span>
        </div>
      </div>
    </footer>
  );
}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Page Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ */
export default function LandingPage() {
  return (
    <main className="bg-[#020208] min-h-screen">
      <Nav />
      <Hero />
      <Ticker />
      <PipelineSection />
      <EvolutionSection />
      <ModesSection />
      <OutputSection />
      <CTASection />
      <Footer />
    </main>
  );
}
