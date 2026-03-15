'use client';

import { HelpCircle } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';
import { useHelp } from '@/contexts/HelpContext';

interface HelpIconProps {
  /** Tooltip text shown on hover */
  content: string;
  /** Optional: open help center to this article on click */
  articleId?: string;
  /** Callback when user clicks (overrides articleId if provided) */
  onClick?: () => void;
  className?: string;
  /** Accessible label */
  'aria-label'?: string;
}

/**
 * Contextual help icon. Shows tooltip on hover. Click opens help center to articleId if set.
 */
export function HelpIcon({
  content,
  articleId,
  onClick,
  className,
  'aria-label': ariaLabel = 'Help',
}: HelpIconProps) {
  const { openHelpCenter } = useHelp();

  const handleClick = () => {
    if (onClick) onClick();
    else if (articleId) openHelpCenter(articleId);
  };

  const icon = (
    <button
      type="button"
      onClick={handleClick}
      aria-label={ariaLabel}
      className={cn(
        'inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
        className
      )}
    >
      <HelpCircle className="h-4 w-4" />
    </button>
  );

  return (
    <Tooltip>
      <TooltipTrigger asChild>{icon}</TooltipTrigger>
      <TooltipContent side="top" className="max-w-xs">
        {content}
      </TooltipContent>
    </Tooltip>
  );
}
