import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SURG-3D Surgical Instrument 3D Pipeline",
  description: "Backend for ZED 2i / Phone Video -> 3D Surgical Instrument (.glb) -> Automated Explainer Video (.mp4)",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}