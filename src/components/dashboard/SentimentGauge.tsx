import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface SentimentGaugeProps {
  value: number; // 0-100
  size?: "sm" | "md" | "lg";
}

export function SentimentGauge({ value, size = "md" }: SentimentGaugeProps) {
  const clampedValue = Math.min(100, Math.max(0, value));
  
  // Calculate color based on value (green to yellow to red)
  const getColor = (val: number) => {
    if (val >= 70) return "hsl(142, 76%, 46%)"; // success green
    if (val >= 40) return "hsl(38, 92%, 50%)"; // warning yellow
    return "hsl(0, 84%, 60%)"; // destructive red
  };

  const getSentimentLabel = (val: number) => {
    if (val >= 70) return "Positive";
    if (val >= 40) return "Neutral";
    return "Negative";
  };

  const sizeStyles = {
    sm: { container: "w-24 h-24", text: "text-lg", label: "text-xs" },
    md: { container: "w-32 h-32", text: "text-2xl", label: "text-sm" },
    lg: { container: "w-40 h-40", text: "text-3xl", label: "text-base" },
  };

  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (clampedValue / 100) * circumference;

  return (
    <div className={cn("relative", sizeStyles[size].container)}>
      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
        {/* Background circle */}
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth="8"
          className="opacity-30"
        />
        {/* Animated progress circle */}
        <motion.circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke={getColor(clampedValue)}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1, ease: "easeOut" }}
          style={{
            filter: `drop-shadow(0 0 8px ${getColor(clampedValue)})`,
          }}
        />
      </svg>
      
      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          className={cn("font-bold", sizeStyles[size].text)}
          style={{ color: getColor(clampedValue) }}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.3 }}
        >
          {clampedValue}
        </motion.span>
        <span className={cn("text-muted-foreground", sizeStyles[size].label)}>
          {getSentimentLabel(clampedValue)}
        </span>
      </div>
    </div>
  );
}
