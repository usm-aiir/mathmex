/// <reference path="../types/window.d.ts" />
"use client"

// @ts-ignore
import styles from "./SearchPage.module.css";
import { useState, useEffect, useRef, useCallback, ReactNode } from "react"
import { History, Keyboard, Mic, Search, Square } from "lucide-react"
import HistoryPanel from "./HistoryPanel.tsx"
import ResultsPanel from "./ResultsPanel.tsx"
import { keyboardLayout } from "../lib/constants.ts"
import { formatDate } from "../lib/utils.ts"
import { addStyles, EditableMathField } from "react-mathquill"
import MathKeyboard from "./MathKeyboard.tsx"
addStyles(); // MathQuill styles

// --- Types ---
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

// --- Main SearchPage Component ---
export default function SearchPage() {
    // --- State Hooks ---
    const [latex, setLatex] = useState<string>("") // The LaTeX string in the search bar
    const [lastFunctionLatex, setLastFunctionLatex] = useState<string>("") // Last inserted function/operator
    const [isKeyboardVisible, setIsKeyboardVisible] = useState<boolean>(false)
    const [isHistoryVisible, setIsHistoryVisible] = useState<boolean>(false)
    const [isListening, setIsListening] = useState<boolean>(false)
    const [transcript, setTranscript] = useState<string>("")
    const [searchResults, setSearchResults] = useState<SearchResult[]>([])
    const [isLoading, setIsLoading] = useState<boolean>(false)
    const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([])
    const [placeholderMessage, setPlaceholderMessage] = useState<ReactNode>(null)
    const [isMathMode, setIsMathMode] = useState<boolean>(true) // true = math mode, false = text mode

    // Ref to hold the MathQuill field instance
    const mathFieldRef = useRef<any>(null)
    const recognitionRef = useRef<SpeechRecognition | null>(null)

    // --- Send transcript to backend when listening stops ---
    useEffect(() => {
        if (!isListening && transcript) {
            speechToLatex(transcript)
            setTranscript("") // Clear transcript after sending
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isListening])

    // --- Load search history and set placeholder on mount ---
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
        // eslint-disable-next-line
    }, [])

    // --- Speech-to-LaTeX ---
    const toggleSpeechRecognition = () => {
        if (isListening) {
            recognitionRef.current?.stop()
            return
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
        if (!SpeechRecognition) {
            console.error("Speech recognition not supported in this browser.")
            return
        }

        const recognition = new SpeechRecognition()
        recognition.continuous = true
        recognition.interimResults = true
        recognition.lang = "en-US"
        recognitionRef.current = recognition

        recognition.onresult = (event: SpeechRecognitionEvent) => {
            let interimTranscript = ""
            let finalTranscript = ""
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcriptPart = event.results[i][0].transcript
                if (event.results[i].isFinal) {
                    finalTranscript += transcriptPart
                } else {
                    interimTranscript += transcriptPart
                }
            }
            setTranscript(finalTranscript)
        }

        recognition.onend = () => {
            setIsListening(false)
            recognitionRef.current = null
        }

        recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
            console.error("Speech recognition error:", event.error)
            setIsListening(false)
        }

        recognition.start()
        setIsListening(true)
    }

    const speechToLatex = (text: string) => {
        fetch("https://api.mathmex.com/speech-to-latex", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ text }),
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.latex && mathFieldRef.current) {
                    mathFieldRef.current.write(data.latex)
                    mathFieldRef.current.focus()
                }
            })
            .catch((err) => {
                console.error("Error converting speech to LaTeX", err);
            });
    };

    // --- Helpers for search history ---
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

    // --- Main search function: sends LaTeX and last function/operator to backend ---
    const performSearch = useCallback(() => {
        const currentLatex = latex.trim();
        if (!currentLatex && !lastFunctionLatex) return;

        setIsLoading(true)
        setSearchResults([])
        addToHistory(currentLatex)
        if (isKeyboardVisible) setIsKeyboardVisible(false)
        if (isHistoryVisible) setIsHistoryVisible(false)

        // Send search request to backend
        fetch("https://api.mathmex.com/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                query: "", // Not used, only LaTeX is sent
                functionLatex: lastFunctionLatex, // Last inserted function/operator
                latex: currentLatex, // Full LaTeX string from the search bar
                isMathMode: isMathMode // Pass math mode boolean
            }),
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
    }, [latex, lastFunctionLatex, searchHistory, isKeyboardVisible, isHistoryVisible, isMathMode])

    // --- Handle key press from MathKeyboard (virtual keyboard) ---
    const handleKeyPress = (keyLatex: string) => {
        if (mathFieldRef.current) {
            mathFieldRef.current.write(keyLatex);
            mathFieldRef.current.focus();
            setLastFunctionLatex(keyLatex);
        }
    };

    // --- Fill input with example and trigger search ---
    const handleExampleClick = (formula: string) => {
        setLatex(formula)
        setTimeout(() => {
            performSearch()
        }, 0)
    }

    // --- Clear search history ---
    const clearHistory = () => {
        updateAndStoreHistory([])
    }

    // --- Handle click on a history item ---
    const handleHistoryItemClick = (itemLatex: string) => {
        setLatex(itemLatex)
        setIsHistoryVisible(false)
        setTimeout(() => {
            performSearch()
        }, 0)
    }

    // --- Render the search page ---
    return (
        <>
            <main className="container">
                <div className="scroll-decoration top"></div>
                <section className={styles.searchSection}>
                    <div className={styles.searchContainer}>
                        <div className={styles.searchInputContainer}>
                            {/* Single MathQuill input for both text and LaTeX */}
                            <EditableMathField
                                latex={latex}
                                onChange={(mathField) => {
                                    setLatex(mathField.latex());
                                }}
                                mathquillDidMount={(mathField) => {
                                    mathFieldRef.current = mathField;
                                }}
                                className={styles.textarea}
                                onKeyDown={(e: any) => {
                                    // Allow searching by pressing Enter
                                    if (e.key === "Enter") {
                                        e.preventDefault();
                                        performSearch();
                                    }
                                }}
                            />
                            <button className={styles.searchButton} onClick={performSearch} disabled={isLoading}>
                                <Search size={18} />
                                <span>{isLoading ? "Searching..." : "Search"}</span>
                            </button>
                        </div>
                        {/* Controls for history and keyboard, now with mode switch inline */}
                        <div className={styles.searchControls}>
                            <div className={styles.modeSwitchContainer} style={{ marginRight: 'auto' }}>
                                <div className={styles.modeSwitchGroup}>
                                    <span className={styles.modeSwitchLabel}>Search with...</span>
                                    <div className={styles.modeButtonRow}>
                                        <button
                                            className={`${styles.modeButton} ${isMathMode ? styles.active : ''}`}
                                            onClick={() => setIsMathMode(true)}
                                            aria-pressed={isMathMode}
                                            type="button"
                                        >
                                            Math
                                        </button>
                                        <button
                                            className={`${styles.modeButton} ${!isMathMode ? styles.active : ''}`}
                                            onClick={() => setIsMathMode(false)}
                                            aria-pressed={!isMathMode}
                                            type="button"
                                        >
                                            Text
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div className={styles.keyboardToggleContainer}>
                                <button
                                    className={`${styles.controlButton} ${isListening ? styles.listening : ""}`}
                                    aria-label={isListening ? "Stop voice input" : "Start voice input"}
                                    onClick={toggleSpeechRecognition}
                                >
                                    {isListening ? <Square size={20} strokeWidth={2.5} /> : <Mic size={20} />}
                                </button>
                                <button
                                    className={styles.controlButton}
                                    aria-label="Search history"
                                    onClick={() => {
                                        setIsHistoryVisible(!isHistoryVisible)
                                        if (!isHistoryVisible) setIsKeyboardVisible(false)
                                    }}
                                >
                                    <History size={20}/>
                                </button>
                                <button
                                    className={styles.controlButton}
                                    aria-label="Toggle keyboard"
                                    onClick={() => {
                                        setIsKeyboardVisible(!isKeyboardVisible)
                                        if (!isKeyboardVisible) setIsHistoryVisible(false)
                                    }}
                                >
                                    <Keyboard size={20}/>
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Show search history panel if visible */}
                    {isHistoryVisible && (
                        <HistoryPanel
                            history={searchHistory.slice().reverse()}
                            onClearHistory={clearHistory}
                            onHistoryItemClick={handleHistoryItemClick}
                            formatDate={formatDate}
                        />
                    )}

                    {/* Show math keyboard if visible */}
                    {isKeyboardVisible && <MathKeyboard layout={keyboardLayout} onKeyPress={handleKeyPress} />}
                </section>

                {/* Results panel */}
                <ResultsPanel results={searchResults} isLoading={isLoading} placeholderMessage={placeholderMessage} />

                <div className="scroll-decoration bottom"></div>
            </main>
        </>
    )
}


