import { MathJaxContext } from "better-react-mathjax"
import SearchPage from "./components/SearchPage.tsx"

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
            <div className="parchment-background">
                <SearchPage />
            </div>
        </MathJaxContext>
    )
}

export default App