import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import { LenisProvider } from '@/components/lenis-provider';

const geistSans = Geist({ variable: '--font-geist-sans', subsets: ['latin'] });
const geistMono = Geist_Mono({ variable: '--font-geist-mono', subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'The AI Factory — Spec at Machine Speed',
  description:
    'Transform raw business requirements into a production-ready MVP specification package using a self-evolving multi-agent AI pipeline.',
  openGraph: {
    title: 'The AI Factory',
    description: 'Eight AI agents. One complete spec. Smarter every run.',
    type: 'website',
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-[#05050a] text-[#f1f1f8]`}>
        <LenisProvider>
          {children}
        </LenisProvider>
      </body>
    </html>
  );
}
