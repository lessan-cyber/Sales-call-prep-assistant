"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export default function Home() {
  const router = useRouter();

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-4xl flex-col items-center justify-center py-32 px-16 bg-white dark:bg-black">
        <div className="flex flex-col items-center gap-8 text-center">
          <h1 className="text-5xl font-bold leading-tight tracking-tight text-black dark:text-zinc-50">
            AI Sales Call Prep Assistant
          </h1>
          <p className="max-w-2xl text-xl leading-8 text-zinc-600 dark:text-zinc-400">
            Prepare for sales calls in minutes, not hours. Our AI researches your prospects
            and generates personalized talking points tailored to their business.
          </p>
          <div className="flex gap-4 mt-8">
            <Button
              size="lg"
              onClick={() => router.push("/new-prep")}
              className="px-8"
            >
              Create New Prep
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={() => router.push("/profile")}
              className="px-8"
            >
              View Profile
            </Button>
          </div>
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
            <div>
              <h3 className="text-lg font-semibold mb-2">⚡ Fast</h3>
              <p className="text-zinc-600 dark:text-zinc-400">
                Generate comprehensive prep reports in under 5 minutes with our AI-powered research.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">🎯 Targeted</h3>
              <p className="text-zinc-600 dark:text-zinc-400">
                Get talking points that connect your portfolio to each prospect's specific challenges.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">💡 Insightful</h3>
              <p className="text-zinc-600 dark:text-zinc-400">
                Access company intelligence, decision maker profiles, and strategic questions.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
