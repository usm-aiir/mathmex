/**
 * main.tsx
 *
 * Entry point for the MathMex frontend React application.
 * Mounts the App component to the DOM and enables React StrictMode.
 */
import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import App from "./App.tsx"
import "./styles/global.css"
import "mathlive";

// Mount the root React component (App) inside StrictMode for highlighting potential problems
createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <App />
    </StrictMode>,
)
