import Link from "next/link";
import { Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";

export function LandingNav() {
  return (
    <header className="sticky top-0 z-30 border-b border-ink/10 bg-paper/85 backdrop-blur dark:border-white/10 dark:bg-[#111]/85">
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2 text-sm font-bold">
          <span className="flex h-9 w-9 items-center justify-center rounded-md bg-ink text-white dark:bg-paper dark:text-ink">
            <Bot className="h-5 w-5" />
          </span>
          BeingAI Assistant
        </Link>
        <div className="flex items-center gap-2">
          <Link href="/pricing" className="hidden text-sm font-medium text-ink/70 hover:text-ink dark:text-white/70 dark:hover:text-white sm:block">
            Pricing
          </Link>
          <ThemeToggle />
          <Link href="/sign-in">
            <Button variant="secondary">Login</Button>
          </Link>
          <Link href="/sign-up">
            <Button>Start free</Button>
          </Link>
        </div>
      </nav>
    </header>
  );
}
