'use client';

import * as React from 'react';
import Link from 'next/link';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import { ArrowRight } from 'lucide-react';

const publicButtonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-md font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary:
          'bg-primary text-primary-foreground hover:bg-primary/90 shadow-glow-gold-subtle hover:shadow-glow-gold',
        secondary:
          'border border-white/20 bg-transparent hover:border-white/30 hover:bg-white/5 text-foreground',
        tertiary:
          'text-primary hover:underline underline-offset-4 bg-transparent',
        ghost: 'text-muted-foreground hover:text-foreground hover:bg-white/5',
      },
      size: {
        sm: 'h-9 px-4 text-sm',
        default: 'h-11 px-6 text-sm',
        lg: 'h-12 px-8 text-base',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'default',
    },
  }
);

export interface PublicButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof publicButtonVariants> {
  asChild?: boolean;
  href?: string;
  showArrow?: boolean;
}

const PublicButton = React.forwardRef<HTMLButtonElement, PublicButtonProps>(
  (
    {
      className,
      variant,
      size,
      asChild = false,
      href,
      showArrow = false,
      children,
      ...props
    },
    ref
  ) => {
    const content = (
      <>
        {children}
        {showArrow && <ArrowRight className="ml-2 h-4 w-4 shrink-0" />}
      </>
    );

    const classNames = cn(publicButtonVariants({ variant, size, className }));

    if (asChild) {
      return (
        <Slot ref={ref} className={classNames} {...props}>
          {children}
        </Slot>
      );
    }

    if (href) {
      return (
        <Link href={href} className={classNames}>
          {content}
        </Link>
      );
    }

    return (
      <button ref={ref} className={classNames} {...props}>
        {content}
      </button>
    );
  }
);
PublicButton.displayName = 'PublicButton';

export { PublicButton, publicButtonVariants };
