import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "h-10 w-full rounded-lg border border-slate-700/80 bg-slate-900/80 px-3.5 text-sm text-slate-100 placeholder:text-slate-500 outline-none transition duration-150 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-50",
        className,
      )}
      {...props}
    />
  ),
);
Input.displayName = "Input";
