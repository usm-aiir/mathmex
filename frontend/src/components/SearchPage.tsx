"use client"

// @ts-ignore
// Import styles and dependencies

import styles from "./SearchPage.module.css"
import { useState, useEffect, useRef, useCallback, ReactNode } from "react"
import { History, Keyboard, Search } from "lucide-react"
import Header from "./Header.tsx"
import Footer from "./Footer.tsx"
import InputField from "./InputField.tsx"
import MathKeyboard from "./MathKeyboard.tsx"
import HistoryPanel from "./HistoryPanel.tsx"
import ResultsPanel from "./ResultsPanel.tsx"
import { keyboardLayout } from "../lib/constants.ts"
import { formatDate } from "../lib/utils.ts"
import type { MathField } from "react-mathquill"

// Types for search history and results.
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

// Main SearchPage component.
export default function SearchPage() {
    // State variables for UI and data
    const [latex, setLatex] = useState<string>("")
    const [isKeyboardVisible, setIsKeyboardVisible] = useState<boolean>(false)
    const [isHistoryVisible, setIsHistoryVisible] = useState<boolean>(false)
    const [searchResults, setSearchResults] = useState<SearchResult[]>([])
    const [isLoading, setIsLoading] = useState<boolean>(false)
    const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([])
    const [placeholderMessage, setPlaceholderMessage] = useState<ReactNode>(null)

    const mathFieldRef = useRef<MathField | null>(null)

    // Add keyboard shortcut handler
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
                e.preventDefault()
                setIsKeyboardVisible(!isKeyboardVisible)
                if (!isKeyboardVisible) setIsHistoryVisible(false)
            }
        }

        window.addEventListener('keydown', handleKeyDown)
        return () => window.removeEventListener('keydown', handleKeyDown)
    }, [isKeyboardVisible])

    // Load search history and set placeholder on mount
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

    // Helper to update and persist search history
    const updateAndStoreHistory = (newHistory: SearchHistoryItem[]) => {
        setSearchHistory(newHistory)
        sessionStorage.setItem("mathMexSearchHistory", JSON.stringify(newHistory))
    }

   // Add a new query to history, keeping max 15 items
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

  // Main search function 
    const performSearch = useCallback(() => {
        const currentLatex = latex.trim()
        if (!currentLatex) return

        setIsLoading(true)
        setSearchResults([])
        addToHistory(currentLatex)
        if (isKeyboardVisible) setIsKeyboardVisible(false)
        if (isHistoryVisible) setIsHistoryVisible(false)

        // Call backend API instead of mockSearch
        fetch("http://localhost:5000/api/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ latex: currentLatex }),
        })
            .then((res) => res.json())
            .then((data) => {
                setSearchResults(data.results || [])
                setIsLoading(false)
            })
            .catch(() => {
                setSearchResults([])
                setIsLoading(false)
            })
    }, [latex, searchHistory, isKeyboardVisible, isHistoryVisible])

    // Handle math keyboard key press
    const handleKeyPress = (keyLatex: string) => {
        mathFieldRef.current?.write(keyLatex)
        mathFieldRef.current?.focus()
    }

    //Fill input with example and trigger search
    const handleExampleClick = (formula: string) => {
        setLatex(formula)
        setTimeout(() => {
            performSearch()
        }, 0)
    }

    //Clear search history
    const clearHistory = () => {
        updateAndStoreHistory([])
    }

    //Handle click on a history item
    const handleHistoryItemClick = (itemLatex: string) => {
        setLatex(itemLatex)
        setIsHistoryVisible(false)
        setTimeout(() => {
            performSearch()
        }, 0)
    }

    // Render the search page with header, input, results, and footer
    return (
        <>
            <Header />
            <main className="container">
                <div className="scroll-decoration top"></div>
                <section className={styles.searchSection}>
                    <div className={styles.searchContainer}>
                        <div className={styles.searchInputContainer}>
                            <InputField latex={latex} setLatex={setLatex} mathFieldRef={mathFieldRef} onEnter={performSearch} />
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
                                    title="Toggle Math Keyboard (CTRL+K)"
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
