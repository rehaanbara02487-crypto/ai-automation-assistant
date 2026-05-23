"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bot, Cable, CreditCard, LayoutDashboard, PlusCircle, Settings, UserRound } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/builder", label: "Create", icon: PlusCircle },
  { href: "/integrations", label: "Apps", icon: Cable },
  { href: "/pricing", label: "Pricing", icon: CreditCard },
  { href: "/settings", label: "Settings", icon: Settings }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-paper text-ink dark:bg-[#111] dark:text-white">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-ink/10 bg-white p-4 dark:border-white/10 dark:bg-white/5 lg:block">
        <Link href="/dashboard" className="flex items-center gap-2 text-sm font-black">
          <span className="flex h-9 w-9 items-center justify-center rounded-md bg-ink text-white dark:bg-paper dark:text-ink">
            <Bot className="h-5 w-5" />
          </span>
          BeingAI Assistant
        </Link>
        <nav className="mt-8 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold text-ink/65 hover:bg-ink/5 hover:text-ink dark:text-white/65 dark:hover:bg-white/10 dark:hover:text-white",
                pathname === item.href && "bg-ink text-white hover:bg-ink hover:text-white dark:bg-white dark:text-ink dark:hover:bg-white"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <div className="lg:pl-64">
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-ink/10 bg-paper/85 px-4 backdrop-blur dark:border-white/10 dark:bg-[#111]/85 sm:px-6">
          <div>
            <p className="text-xs font-bold uppercase text-ink/45 dark:text-white/45">Workspace</p>
            <p className="text-sm font-bold">Operations assistant</p>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <span className="flex h-9 w-9 items-center justify-center rounded-md border border-ink/10 bg-white dark:border-white/10 dark:bg-white/10" title="Workspace user">
              <UserRound className="h-4 w-4" />
            </span>
          </div>
        </header>
        <div className="border-b border-ink/10 bg-white px-2 py-2 dark:border-white/10 dark:bg-white/5 lg:hidden">
          <nav className="flex overflow-x-auto">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex min-w-fit items-center gap-2 rounded-md px-3 py-2 text-sm font-semibold",
                  pathname === item.href ? "bg-ink text-white dark:bg-white dark:text-ink" : "text-ink/65 dark:text-white/65"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">{children}</main>
      </div>
    </div>
  );
}
