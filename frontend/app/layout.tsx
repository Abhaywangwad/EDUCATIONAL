import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Manrope, Source_Sans_3 } from "next/font/google";
import "./globals.css";

const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-display"
});

const sourceSans = Source_Sans_3({
  subsets: ["latin"],
  variable: "--font-body"
});

export const metadata: Metadata = {
  title: "HLGS",
  description: "Multi-role education platform for human-like grading, student submissions, and parent-friendly reports."
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${manrope.variable} ${sourceSans.variable}`}>{children}</body>
    </html>
  );
}
