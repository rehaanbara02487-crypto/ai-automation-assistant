import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  tone?: "neutral" | "success" | "warning" | "danger" | "info";
};

export function Badge({ className, tone = "neutral", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-bold",
        tone === "neutral" && "border-ink/10 bg-white/60 text-ink/70 dark:border-white/10 dark:bg-white/10 dark:text-white/70",
        tone === "success" && "border-mint/30 bg-mint/15 text-mint",
        tone === "warning" && "border-saffron/30 bg-saffron/20 text-ink dark:text-white",
        tone === "danger" && "border-rose/30 bg-rose/15 text-rose",
        tone === "info" && "border-sky/30 bg-sky/15 text-sky",
        className
      )}
      {...props}
    />
  );
}

