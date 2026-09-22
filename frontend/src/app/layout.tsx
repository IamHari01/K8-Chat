import type { Metadata } from "next";
import "./globals.css";
const geistSansVariable = "--font-geist-sans";
const geistMonoVariable = "--font-geist-mono";

export const metadata: Metadata = {
  title: "K8 Chat — Enterprise AI Assistant",
  description: "Enterprise Kubernetes RAG & Security Gateway",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSansVariable} ${geistMonoVariable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
