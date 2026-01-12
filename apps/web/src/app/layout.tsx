import type { Metadata } from 'next';
import { Manrope, Space_Grotesk } from 'next/font/google';

import PageTransition from '@/components/PageTransition';
import ParticleField from '@/components/ParticleField';
import './globals.css';

const manrope = Manrope({ subsets: ['latin'], variable: '--font-sans' });
const spaceGrotesk = Space_Grotesk({ subsets: ['latin'], variable: '--font-display' });

export const metadata: Metadata = {
  title: 'Regulus',
  description: 'Talk to your codebase with graph intelligence and RAG.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${manrope.variable} ${spaceGrotesk.variable}`}>
      <body className="min-h-screen bg-canvas text-text">
        <div className="relative min-h-screen overflow-hidden">
          <ParticleField />
          <PageTransition>{children}</PageTransition>
        </div>
      </body>
    </html>
  );
}
