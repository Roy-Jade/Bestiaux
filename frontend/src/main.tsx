import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Layout } from "./functions/core/components/Layout";
import { HomePage } from "./functions/core/pages/HomePage";

const rootElement = document.getElementById("root");
if (!rootElement) throw new Error("Root element not found");

createRoot(rootElement).render(
  <StrictMode>
    <Layout>
      <HomePage />
    </Layout>
  </StrictMode>,
);
