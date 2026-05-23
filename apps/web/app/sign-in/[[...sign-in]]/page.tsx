import { SignIn } from "@clerk/nextjs";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function SignInPage() {
  if (!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-paper px-4 dark:bg-[#111]">
        <div className="max-w-sm rounded-lg border border-ink/10 bg-white p-6 text-center shadow-soft dark:border-white/10 dark:bg-white/10">
          <h1 className="text-2xl font-black">Auth is ready</h1>
          <p className="mt-2 text-sm text-ink/65 dark:text-white/65">Add Clerk keys in the environment to enable hosted login.</p>
          <Link href="/dashboard">
            <Button className="mt-5">Continue demo</Button>
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-paper px-4 dark:bg-[#111]">
      <SignIn routing="path" path="/sign-in" signUpUrl="/sign-up" />
    </main>
  );
}
