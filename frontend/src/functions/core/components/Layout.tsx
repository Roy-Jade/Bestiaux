import type { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div>
      <header>
        <nav>
          <h1>Bestiaux</h1>
        </nav>
      </header>
      {children}
      <footer>
        <p>Bestiaux — 2026</p>
      </footer>
    </div>
  );
}
