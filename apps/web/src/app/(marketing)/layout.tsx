import { MarketingNav } from '@/components/marketing/MarketingNav';
import { MarketingFooter } from '@/components/marketing/MarketingFooter';

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen min-h-dvh flex-col bg-background text-foreground">
      <MarketingNav />
      <main className="flex-1 w-full min-w-0 overflow-x-hidden">{children}</main>
      <MarketingFooter />
    </div>
  );
}
