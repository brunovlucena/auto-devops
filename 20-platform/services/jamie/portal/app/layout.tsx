import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Jamie - AI DevOps Copilot',
  description: 'Your friendly IT buddy meets AI-powered automation - The personable face of DevOps',
  keywords: ['AI', 'DevOps', 'Kubernetes', 'Prometheus', 'Loki', 'ChatGPT', 'Infrastructure'],
  authors: [{ name: 'Jamie AI Team' }],
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full antialiased`}>
        {children}
      </body>
    </html>
  )
} 