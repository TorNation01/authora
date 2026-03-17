'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';

export type CTAVariant = 'primary' | 'secondary';

interface CTAButtonProps {
  href: string;
  label: string;
  variant?: CTAVariant;
  showArrow?: boolean;
  analyticsId: string;
  className?: string;
  size?: 'default' | 'sm' | 'lg';
}

export function CTAButton({
  href,
  label,
  variant = 'primary',
  showArrow = variant === 'primary',
  analyticsId,
  className,
  size = 'lg',
}: CTAButtonProps) {
  const baseClasses =
    'min-w-[200px] h-12 text-base font-semibold transition-all duration-200';
  const primaryClasses =
    'shadow-[var(--glow-gold-subtle)] hover:shadow-[var(--glow-gold)]';
  const secondaryClasses =
    'border-white/20 hover:border-white/30 hover:bg-white/5';

  return (
    <Button
      asChild
      size={size}
      variant={variant === 'primary' ? 'default' : 'outline'}
      className={`${baseClasses} ${
        variant === 'primary' ? primaryClasses : secondaryClasses
      } ${className ?? ''}`}
      data-analytics={analyticsId}
    >
      <Link href={href}>
        {label}
        {showArrow && <ArrowRight className="ml-2 h-4 w-4 shrink-0" />}
      </Link>
    </Button>
  );
}
