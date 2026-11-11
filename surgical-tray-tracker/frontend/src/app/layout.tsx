import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SurgTrace AI | Surgical Instrument Tray Tracking & Missing Item Detection",
  description: "Real-time computer vision surgical tray audit and instrument utilization analytics",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-teal-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
