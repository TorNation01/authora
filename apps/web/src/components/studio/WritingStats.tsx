'use client';

interface WritingStatsProps {
  wordCount: number;
  readingTimeMinutes?: number;
  className?: string;
}

const WPM = 200;

export function WritingStats({ wordCount, readingTimeMinutes, className }: WritingStatsProps) {
  const readingTime = readingTimeMinutes ?? Math.ceil(wordCount / WPM);

  return (
    <div className={className}>
      <span className="text-sm text-muted-foreground">
        {wordCount.toLocaleString()} words
      </span>
      <span className="mx-2 text-muted-foreground/50">·</span>
      <span className="text-sm text-muted-foreground">
        ~{readingTime} min read
      </span>
    </div>
  );
}
