export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen min-h-dvh bg-background text-foreground w-full">
      {children}
    </div>
  );
}
