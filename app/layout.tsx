import "./globals.css";
import { Metadata } from "next";
import { Toaster } from "sonner";
import { Inter as FontSans } from "next/font/google";
import { cn } from "@/lib/utils";
import { ThemeProvider } from "next-themes";

const fontSans = FontSans({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://iqkiller-vercel.vercel.app"),
  title: "IQKiller - AI Interview Preparation",
  description: "AI-powered interview preparation platform. Upload your resume, analyze job postings, and get personalized interview questions and strategies.",
  icons: {
    icon: '/favicon.ico'
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
      </body>
    </html>
  );
} 