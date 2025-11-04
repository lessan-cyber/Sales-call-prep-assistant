import type { Metadata } from "next";
import { Space_Mono } from "next/font/google";
import "./globals.css";

import { cn } from "@/lib/utils";
import Link from "next/link";
import { AuthProvider } from "@/components/providers/auth-provider";

const spaceMono = Space_Mono({
  subsets: ["latin"],
  weight: ["400", "700"],
});

export const metadata: Metadata = {
  title: "AI Sales Call Prep Assistant",
  description: "Prepare for sales calls in minutes, not hours.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased",
          spaceMono.className
        )}
      >
        <nav className="flex items-center justify-between p-4 bg-gray-800 text-white">
          <Link href="/" className="text-lg font-bold">
            Sales Prep AI
          </Link>
          <div className="space-x-4">
            <Link href="/new-prep" className="hover:underline">
              New Prep
            </Link>
            <Link href="/profile" className="hover:underline">
              Profile
            </Link>
          </div>
        </nav>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
