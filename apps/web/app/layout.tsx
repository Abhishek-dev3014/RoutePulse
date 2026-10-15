import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "RoutePulse · Campus transport intelligence",
  description: "Observe, predict and optimize your campus shuttle network.",
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
