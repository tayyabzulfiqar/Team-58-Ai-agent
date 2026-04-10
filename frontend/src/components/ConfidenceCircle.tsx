import { useEffect, useState } from "react";

interface Props {
  score: number;
}

export function ConfidenceCircle({ score }: Props) {
  const [animated, setAnimated] = useState(0);
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (animated / 100) * circumference;

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(score), 300);
    return () => clearTimeout(timer);
  }, [score]);

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative w-28 h-28">
        <svg className="w-full h-full -rotate-90 relative" viewBox="0 0 100 100">
          <defs>
            <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="hsl(263 70% 68%)" />
              <stop offset="100%" stopColor="hsl(217 91% 60%)" />
            </linearGradient>
          </defs>
          <circle cx="50" cy="50" r={radius} fill="none" stroke="hsl(220 14% 94%)" strokeWidth="4" />
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke="url(#progressGradient)"
            strokeWidth="4.5"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-foreground">{animated}%</span>
        </div>
      </div>
      <p className="text-[10px] font-semibold text-muted-foreground tracking-[0.12em] uppercase">Operational</p>
    </div>
  );
}
