import { MathJaxContext } from "better-react-mathjax"
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import SearchPage from "./components/SearchPage"
import AboutPage from "./components/AboutPage"
import Header from "./components/Header"
import Footer from "./components/Footer"

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
    return (
        <MathJaxContext version={3} config={mathJaxConfig}>
            <Router>
                <div className="parchment-background">
                    <Header />
                    <Routes>
                        <Route path="/" element={<SearchPage />} />
                        <Route path="/about" element={<AboutPage />} />
                    </Routes>
                    <Footer />
                </div>
            </Router>
        </MathJaxContext>
    )
}

export default App