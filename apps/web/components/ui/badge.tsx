import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md px-2 py-0.5 text-2xs font-medium uppercase tracking-wider transition-colors",
  {
    variants: {
      variant: {
        default: "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30",
        secondary: "bg-slate-800 text-slate-300 border border-slate-700",
        outline: "border border-slate-700 bg-transparent text-slate-300",
        success: "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30",
        warning: "bg-amber-500/20 text-amber-300 border border-amber-500/30",
        danger: "bg-rose-500/20 text-rose-300 border border-rose-500/30",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
