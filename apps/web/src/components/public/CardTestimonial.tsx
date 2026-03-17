'use client';

import { cn } from '@/lib/utils';

interface CardTestimonialProps {
  quote: string;
  author?: string;
  role?: string;
  className?: string;
}

export function CardTestimonial({
  quote,
  author,
  role,
  className,
}: CardTestimonialProps) {
  return (
    <div
      className={cn(
        'card-premium p-6',
        className
      )}
    >
      <blockquote className="font-serif text-lg text-foreground leading-relaxed">
        &ldquo;{quote}&rdquo;
      </blockquote>
      {(author || role) && (
        <footer className="mt-4">
          {author && (
            <cite className="not-italic font-medium text-foreground">{author}</cite>
          )}
          {role && (
            <p className="text-sm text-muted-foreground mt-0.5">{role}</p>
          )}
        </footer>
      )}
    </div>
  );
}
