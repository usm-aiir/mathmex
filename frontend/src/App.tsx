import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import SearchPage from "./components/SearchPage"
import AboutPage from "./components/AboutPage"
import Header from "./components/Header"
import Footer from "./components/Footer"
import HelpModal, { shouldShowFirstTimePopup } from "./components/HelpModal"
import React from "react"
import SurveyPage from "./components/SurveyPage";

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
                <Header />
                <Routes>
                    {/* Main search page route */}
                    <Route path="/" element={<SearchPage />} />
                    {/* About page route */}
                    <Route path="/about" element={<AboutPage />} />
                    {/* Catch-all route for 404 Not Found */}
                    <Route path="*" element={<SearchPage />} />
                    {/* Survey page route */}
                    <Route path="/survey" element={<SurveyPage />} />
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