import { MathJaxContext } from "better-react-mathjax"
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import SearchPage from "./components/SearchPage"
import AboutPage from "./components/AboutPage"
import Header from "./components/Header"
import Footer from "./components/Footer"
import HelpModal, { shouldShowFirstTimePopup } from "./components/HelpModal"
import React from "react"

const mathJaxConfig = {
    tex: {
        inlineMath: [
            ["$", "$"],
            ["$$", "$$"],
        ],
        displayMath: [
            ["$$", "$$"],
            ["\\[", "\\]"],
        ],
        processEscapes: true,
        processEnvironments: true,
    },
    options: {
        skipHtmlTags: ["script", "noscript", "style", "textarea", "pre"],
    },
}

function App() {
    const [showHelp, setShowHelp] = React.useState(shouldShowFirstTimePopup());

    const handleOpenHelp = () => setShowHelp(true);
    const handleCloseHelp = () => setShowHelp(false);

    return (
        <MathJaxContext version={3} config={mathJaxConfig}>
            <Router>
                <div className="parchment-background">
                    <Header />
                    <Routes>
                        <Route path="/" element={<SearchPage />} />
                        <Route path="/about" element={<AboutPage />} />
                    </Routes>
                    <Footer onHelpClick={handleOpenHelp} />
                    <HelpModal open={showHelp} onClose={handleCloseHelp} />
                </div>
            </Router>
        </MathJaxContext>
    )
}

export default App