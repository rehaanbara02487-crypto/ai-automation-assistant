import { cn } from "@/lib/utils";
import type { ButtonHTMLAttributes } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
};

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex h-11 items-center justify-center gap-2 rounded-md px-4 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-sky disabled:cursor-not-allowed disabled:opacity-60",
        variant === "primary" && "bg-ink text-white hover:bg-black dark:bg-paper dark:text-ink",
        variant === "secondary" && "border border-ink/10 bg-white text-ink hover:bg-ink/5 dark:border-white/10 dark:bg-white/10 dark:text-white",
        variant === "ghost" && "bg-transparent text-ink hover:bg-ink/5 dark:text-white dark:hover:bg-white/10",
        className
      )}
      {...props}
    />
  );
}

