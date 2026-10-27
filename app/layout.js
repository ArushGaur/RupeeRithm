import './globals.css';

export const metadata = { title: 'Adviser Co-pilot' };

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
