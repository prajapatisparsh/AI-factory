'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownRendererProps {
  content: string;
  className?: string;
  compact?: boolean;
}

export function MarkdownRenderer({ content, className = '', compact = false }: MarkdownRendererProps) {
  return (
    <div
      className={`prose-custom ${compact ? 'prose-compact' : ''} ${className}`}
      style={ {
        color: '#c8c8e8',
        lineHeight: compact ? 1.6 : 1.8,
        fontSize: compact ? '0.8125rem' : '0.875rem',
        fontFamily: 'var(--font-geist-sans)',
        overflowWrap: 'break-word',
        minWidth: 0,
      } }
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 style={{ color: '#f1f1f8', fontSize: compact ? '1.1rem' : '1.25rem', fontWeight: 700, marginBottom: '0.75rem', marginTop: '1.5rem', borderBottom: '1px solid rgba(99,102,241,0.2)', paddingBottom: '0.5rem' }}>
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 style={{ color: '#e8e8f8', fontSize: compact ? '1rem' : '1.1rem', fontWeight: 600, marginBottom: '0.5rem', marginTop: '1.25rem' }}>
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 style={{ color: '#d8d8f0', fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.4rem', marginTop: '1rem' }}>
              {children}
            </h3>
          ),
          p: ({ children }) => (
            <p style={{ marginBottom: '0.75rem', color: '#b8b8d8' }}>
              {children}
            </p>
          ),
          ul: ({ children }) => (
            <ul style={{ paddingLeft: '1.25rem', marginBottom: '0.75rem', listStyleType: 'disc' }}>
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol style={{ paddingLeft: '1.25rem', marginBottom: '0.75rem', listStyleType: 'decimal' }}>
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li style={{ marginBottom: '0.25rem', color: '#b8b8d8' }}>
              {children}
            </li>
          ),
          code: ({ inline, children, ...props }: { inline?: boolean; children?: React.ReactNode } & React.HTMLAttributes<HTMLElement>) => (
            inline
              ? <code style={{ background: 'rgba(99,102,241,0.12)', color: '#818cf8', padding: '0.1em 0.4em', borderRadius: '4px', fontSize: '0.85em', fontFamily: 'var(--font-geist-mono)', wordBreak: 'break-word', overflowWrap: 'break-word' }} {...props}>{children}</code>
              : <code style={{ display: 'block', background: '#0d0d18', color: '#a5b4fc', padding: '1rem', borderRadius: '8px', fontSize: '0.8125rem', fontFamily: 'var(--font-geist-mono)', border: '1px solid rgba(99,102,241,0.15)', overflowX: 'auto', marginBottom: '0.75rem', lineHeight: 1.6, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }} {...props}>{children}</code>
          ),
          pre: ({ children }) => (
            <pre style={{ margin: '0 0 0.75rem 0', background: 'transparent' }}>
              {children}
            </pre>
          ),
          blockquote: ({ children }) => (
            <blockquote style={{ borderLeft: '3px solid #6366f1', paddingLeft: '1rem', color: '#8888aa', fontStyle: 'italic', margin: '0.75rem 0' }}>
              {children}
            </blockquote>
          ),
          strong: ({ children }) => (
            <strong style={{ color: '#e8e8f8', fontWeight: 600 }}>
              {children}
            </strong>
          ),
          em: ({ children }) => (
            <em style={{ color: '#a5b4fc', fontStyle: 'italic' }}>
              {children}
            </em>
          ),
          hr: () => (
            <hr style={{ border: 'none', borderTop: '1px solid rgba(99,102,241,0.15)', margin: '1.25rem 0' }} />
          ),
          img: ({ src, alt }) => (
            <img src={src} alt={alt ?? ''} style={{ maxWidth: '100%', height: 'auto', borderRadius: '8px', margin: '0.75rem 0' }} />
          ),
          table: ({ children }) => (
            <div style={{ overflowX: 'auto', marginBottom: '0.75rem', WebkitOverflowScrolling: 'touch' as React.CSSProperties['WebkitOverflowScrolling'] }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem', tableLayout: 'fixed' }}>
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead style={{ background: 'rgba(99,102,241,0.08)' }}>
              {children}
            </thead>
          ),
          th: ({ children }) => (
            <th style={{ padding: '0.5rem 0.75rem', textAlign: 'left', color: '#f1f1f8', fontWeight: 600, borderBottom: '1px solid rgba(99,102,241,0.2)', fontSize: '0.8125rem', whiteSpace: 'normal', wordBreak: 'break-word' }}>
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td style={{ padding: '0.4rem 0.75rem', color: '#b8b8d8', borderBottom: '1px solid rgba(99,102,241,0.08)', fontSize: '0.8125rem', whiteSpace: 'normal', wordBreak: 'break-word' }}>
              {children}
            </td>
          ),
          a: ({ href, children }) => (
            <a href={href} style={{ color: '#818cf8', textDecoration: 'underline', textUnderlineOffset: '3px', transition: 'color 0.15s ease' }} target="_blank" rel="noopener noreferrer"
              onMouseEnter={e => ((e.currentTarget as HTMLAnchorElement).style.color = '#a5b4fc')}
              onMouseLeave={e => ((e.currentTarget as HTMLAnchorElement).style.color = '#818cf8')}>
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
