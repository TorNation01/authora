'use client';

import { ReactNode } from 'react';
import { useParams } from 'next/navigation';
import { BibleNav, BookNav } from '@/components/bible/nav';

export default function BibleLayout({ children }: { children: ReactNode }) {
  const params = useParams<{ id: string; bookId: string }>();
  const projectId = params?.id as string;
  const bookId = params?.bookId as string;

  return (
    <div className="max-w-5xl p-6 lg:p-8">
      <BookNav projectId={projectId} bookId={bookId} className="mb-6" />
      <BibleNav projectId={projectId} bookId={bookId} />
      {children}
    </div>
  );
}
