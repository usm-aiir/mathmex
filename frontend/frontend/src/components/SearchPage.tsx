"use client"

// @ts-ignore
import styles from "./SearchPage.module.css"
import { useState, useEffect, useRef, useCallback, ReactNode } from "react"
import { History, Keyboard, Search } from "lucide-react"
import Header from "./Header.tsx"
import Footer from "./Footer.tsx"
import MathInputField from "./MathInputField"
import MathKeyboard from "./MathKeyboard"
import HistoryPanel from "./HistoryPanel.tsx"
import ResultsPanel from "./ResultsPanel.tsx"
import { keyboardLayout, mockSearch } from "../lib/constants"
import { formatDate } from "../lib/utils"
import type { MathField } from "react-mathquill"

interface SearchHistoryItem {
    latex: string
    timestamp: number
}

interface SearchResult {
    title: string
    formula: string
    description: string
    tags: string[]
    year: string
}

export default function SearchPage() {
    const [latex, setLatex] = useState<string>("")
    const [isKeyboardVisible, setIsKeyboardVisible] = useState<boolean>(false)
    const [isHistoryVisible, setIsHistoryVisible] = useState<boolean>(false)
    const [searchResults, setSearchResults] = useState<SearchResult[]>([])
    const [isLoading, setIsLoading] = useState<boolean>(false)
    const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([])
    const [placeholderMessage, setPlaceholderMessage] = useState<ReactNode>(null)

    const mathFieldRef = useRef<MathField | null>(null)

    useEffect(() => {
        const storedHistory = sessionStorage.getItem("mathMexSearchHistory")
        if (storedHistory) {
            setSearchHistory(JSON.parse(storedHistory))
        }
        setPlaceholderMessage(
            <div className={styles.resultsPlaceholderMessage}>
                <p>Enter a mathematical theorem or formula to search</p>
                <p>
                    Example: Try searching for{" "}
                    <span
                        className="example"
                        onClick={() =>
                            handleExampleClick(
                                "\\oint_C \\vec{F} \\cdot d\\vec{r} = \\iint_S (\\nabla \\times \\vec{F}) \\cdot d\\vec{S}",
                            )
                        }
                    >
            Stokes' Theorem
          </span>{" "}
                    or{" "}
                    <span className="example" onClick={() => handleExampleClick("e^{i\\pi} + 1 = 0")}>
            Euler's Identity
          </span>
                </p>
            </div>,
        )
    }, [])

    const updateAndStoreHistory = (newHistory: SearchHistoryItem[]) => {
        setSearchHistory(newHistory)
        sessionStorage.setItem("mathMexSearchHistory", JSON.stringify(newHistory))
    }

    const addToHistory = (query: string) => {
        if (!query) return
        const newItem: SearchHistoryItem = { latex: query, timestamp: Date.now() }
        let updatedHistory = searchHistory.filter((item) => item.latex !== query)
        updatedHistory.push(newItem)
        if (updatedHistory.length > 15) {
            updatedHistory = updatedHistory.slice(-15)
        }
        updateAndStoreHistory(updatedHistory)
    }

    const performSearch = useCallback(() => {
        const currentLatex = latex.trim()
        if (!currentLatex) return

        setIsLoading(true)
        setSearchResults([])
        addToHistory(currentLatex)
        if (isKeyboardVisible) setIsKeyboardVisible(false)
        if (isHistoryVisible) setIsHistoryVisible(false)

        setTimeout(() => {
            const results = mockSearch(currentLatex)
            setSearchResults(results)
            setIsLoading(false)
        }, 1500)
    }, [latex, searchHistory, isKeyboardVisible, isHistoryVisible])

    const handleKeyPress = (keyLatex: string) => {
        mathFieldRef.current?.write(keyLatex)
        mathFieldRef.current?.focus()
    }

    const handleExampleClick = (formula: string) => {
        setLatex(formula)
        setTimeout(() => {
            performSearch()
        }, 0)
    }

    const clearHistory = () => {
        updateAndStoreHistory([])
    }

    const handleHistoryItemClick = (itemLatex: string) => {
        setLatex(itemLatex)
        setIsHistoryVisible(false)
        setTimeout(() => {
            performSearch()
        }, 0)
    }

    return (
        <>
            <Header />
            <main className="container">
                <div className="scroll-decoration top"></div>
                <section className={styles.searchSection}>
                    <div className={styles.searchContainer}>
                        <div className={styles.searchInputContainer}>
                            <MathInputField latex={latex} setLatex={setLatex} mathFieldRef={mathFieldRef} onEnter={performSearch} />
                            <button className={styles.searchButton} onClick={performSearch} disabled={isLoading}>
                                <Search size={18} />
                                <span>{isLoading ? "Searching..." : "Search"}</span>
                            </button>
                        </div>

                        <div className={styles.searchControls}>
                            <div className={styles.keyboardToggleContainer}>
                                <button
                                    className={styles.controlButton}
                                    aria-label="Search history"
                                    onClick={() => {
                                        setIsHistoryVisible(!isHistoryVisible)
                                        if (!isHistoryVisible) setIsKeyboardVisible(false)
                                    }}
                                >
                                    <History size={20} />
                                </button>
                                <button
                                    className={styles.controlButton}
                                    aria-label="Toggle keyboard"
                                    onClick={() => {
                                        setIsKeyboardVisible(!isKeyboardVisible)
                                        if (!isKeyboardVisible) setIsHistoryVisible(false)
                                    }}
                                >
                                    <Keyboard size={20} />
                                </button>
                            </div>
                        </div>
                    </div>

                    {isHistoryVisible && (
                        <HistoryPanel
                            history={searchHistory.slice().reverse()}
                            onClearHistory={clearHistory}
                            onHistoryItemClick={handleHistoryItemClick}
                            formatDate={formatDate}
                        />
                    )}

                    {isKeyboardVisible && <MathKeyboard layout={keyboardLayout} onKeyPress={handleKeyPress} />}
                </section>

                <ResultsPanel results={searchResults} isLoading={isLoading} placeholderMessage={placeholderMessage} />

                <div className="scroll-decoration bottom"></div>
            </main>
            <Footer />
        </>
    )
}
