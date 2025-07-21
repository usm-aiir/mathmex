import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import SearchPage from "./pages/SearchPage"
import AboutPage from "./pages/AboutPage"
import Header from "./components/Header"
import Footer from "./components/Footer"
import HelpModal, { shouldShowFirstTimePopup } from "./components/HelpModal"
import React, { useState } from "react"

/**
 * App.tsx
 *
 * The root component for the MathMex frontend application. Sets up global providers (MathJax, Router),
 * renders the main layout, and handles global modals and navigation.
 */
// MathJax configuration for rendering LaTeX math expressions throughout the app


/**
 * Root application component.
 *
 * - Provides MathJax context for math rendering
 * - Sets up React Router for navigation
 * - Handles global Help modal state
 *
 * @returns {JSX.Element} The rendered application
 */
function App() {
    // State to control visibility of the Help modal (shows on first visit)
    const [showHelp, setShowHelp] = React.useState(shouldShowFirstTimePopup());

    // State to control search history sidebar
    const [isHistoryOpen, setIsHistoryOpen] = useState(false)

    /**
     * Opens the Help modal.
     */
    const handleOpenHelp = () => setShowHelp(true);
    /**
     * Closes the Help modal.
     */
    const handleCloseHelp = () => setShowHelp(false);

    return (
        <Router>
            {/* Main application background and layout */}
            <div className="parchment-background">
                <Header onOpenHistorySidebar={() => setIsHistoryOpen(true)} />
                <Routes>
                    {/* Main search page route */}
                    <Route path="/" element={<SearchPage isHistoryOpen={isHistoryOpen} setIsHistoryOpen={setIsHistoryOpen} />} />
                    {/* About page route */}
                    <Route path="/about" element={<AboutPage />} />
                </Routes>
                {/* Footer with Help button */}
                <Footer onHelpClick={handleOpenHelp} />
                {/* Global Help modal */}
                <HelpModal open={showHelp} onClose={handleCloseHelp} />
            </div>
        </Router>
    )
}

export default App