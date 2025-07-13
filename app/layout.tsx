import "./globals.css";
import { Metadata } from "next";
import { Toaster } from "sonner";
import { Inter as FontSans } from "next/font/google";
import { cn } from "@/lib/utils";
import { ThemeProvider } from "next-themes";
import { SpeedInsights } from "@vercel/speed-insights/next";
import { Analytics } from "@vercel/analytics/next";

const fontSans = FontSans({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: {
    default: "IQKiller - AI Interview Preparation Platform",
    template: "%s | IQKiller"
  },
  description: "Get AI-powered, personalized interview preparation. Upload your resume, analyze job postings, and receive tailored questions with comprehensive coaching guides. Ace your next interview with IQKiller.",
  keywords: [
    "interview preparation",
    "AI interview coach",
    "job interview questions",
    "resume analysis",
    "career coaching",
    "interview practice",
    "job preparation",
    "interview guide",
    "technical interviews",
    "behavioral questions"
  ],
  authors: [{ name: "IQKiller Team" }],
  creator: "IQKiller",
  publisher: "IQKiller",
  metadataBase: new URL("https://iqkiller.vercel.app"),
  
  // Open Graph metadata
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://iqkiller.vercel.app",
    siteName: "IQKiller - AI Interview Preparation",
    title: "IQKiller - AI Interview Preparation Platform",
    description: "Get AI-powered, personalized interview preparation. Upload your resume, analyze job postings, and receive tailored questions with comprehensive coaching guides.",
    images: [
      {
        url: "/api/og?title=IQKiller - AI Interview Preparation Platform&description=Get AI-powered, personalized interview preparation",
        width: 1200,
        height: 630,
        alt: "IQKiller - AI Interview Preparation Platform",
        type: "image/png",
      }
    ],
  },
  
  // Twitter Card metadata
  twitter: {
    card: "summary_large_image",
    site: "@IQKiller",
    creator: "@IQKiller",
    title: "IQKiller - AI Interview Preparation Platform",
    description: "Get AI-powered, personalized interview preparation. Upload your resume, analyze job postings, and receive tailored questions with comprehensive coaching guides.",
    images: ["/api/og?title=IQKiller&description=AI Interview Preparation Platform"],
  },
  
  // Additional metadata
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  
  // Verification and other meta tags
  verification: {
    google: "your-google-verification-code", // Add your actual verification code
  },
  
  // App-specific metadata
  applicationName: "IQKiller",
  category: "career development",
  
  // Icons
  icons: {
    icon: [
      {
        url: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="50" fill="%233b82f6">IQ</text></svg>',
        type: 'image/svg+xml',
      }
    ],
    apple: [
      {
        url: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 180"><rect width="180" height="180" fill="%233b82f6" rx="20"/><text x="50%" y="50%" text-anchor="middle" dy=".3em" font-size="60" fill="white" font-family="system-ui">IQ</text></svg>',
        sizes: '180x180',
        type: 'image/svg+xml',
      }
    ],
  },
  
  // Additional Open Graph properties
  other: {
    "og:type": "website",
    "og:locale": "en_US",
    "article:author": "IQKiller Team",
    "article:section": "Career Development",
    "article:tag": "interview preparation, AI coaching, career development",
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head />
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased",
          fontSans.variable
        )}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <main className="relative flex min-h-screen flex-col">
            <div className="flex-1">
              <Toaster position="top-center" />
              {children}
            </div>
          </main>
        </ThemeProvider>
        <SpeedInsights />
        <Analytics />
      </body>
    </html>
  );
} 