import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Todo Web Application',
  description: 'A multi-user todo application with authentication',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">{children}</body>
    </html>
  );
}