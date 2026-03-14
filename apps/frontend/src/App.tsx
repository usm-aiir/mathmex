import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import SearchPage from "./pages/SearchPage"
import AboutPage from "./pages/AboutPage"
import ErrorPage from "./pages/ErrorPage"
import Header from "./components/Header"
import Footer from "./components/Footer"
import HelpModal, { shouldShowFirstTimePopup } from "./components/HelpModal"
import React, { useState, useEffect } from "react"
import { API_BASE } from "./lib/api"

/**
 * App.tsx
 *
 * The root component for the MathMex frontend application. Checks backend health on load;
 * if down, shows maintenance page immediately. Otherwise renders the main app.
 */

function App() {
    const [showHelp, setShowHelp] = React.useState(shouldShowFirstTimePopup());
    const [isHistoryOpen, setIsHistoryOpen] = useState(false)
    const [backendUp, setBackendUp] = useState<boolean | null>(null)

    useEffect(() => {
        fetch(`${API_BASE}/health`)
            .then(res => setBackendUp(res.ok))
            .catch(() => setBackendUp(false))
    }, [])

    const handleOpenHelp = () => setShowHelp(true);
    const handleCloseHelp = () => setShowHelp(false);

    if (backendUp === null) {
        return (
            <div className="primary-content" style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "60vh" }}>
                <p style={{ color: "var(--primary-text, #374151)" }}>Loading…</p>
            </div>
        )
    }

    if (!backendUp) {
        return <ErrorPage />
    }

    return (
        <Router>
            <div className="primary-content">
                <Header onOpenHistorySidebar={() => setIsHistoryOpen(true)} />
                <Routes>
                    <Route path="/" element={<SearchPage isHistoryOpen={isHistoryOpen} setIsHistoryOpen={setIsHistoryOpen} />} />
                    <Route path="/search" element={<SearchPage isHistoryOpen={isHistoryOpen} setIsHistoryOpen={setIsHistoryOpen} />} />
                    <Route path="/about" element={<AboutPage />} />
                    <Route path="/error" element={<ErrorPage />} />
                </Routes>
            </div>
            <Footer onHelpClick={handleOpenHelp} />
            <HelpModal open={showHelp} onClose={handleCloseHelp} />
        </Router>
    )
}

export default App