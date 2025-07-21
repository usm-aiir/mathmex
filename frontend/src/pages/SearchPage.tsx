import { ReactNode, useState, useRef, useEffect } from "react"
import styles from "./SearchPage.module.css"
import SearchPanel from "../features/search/SearchPanel"
import HistoryPanel from "../features/search/HistoryPanel"
import ResultsPanel from "../features/search/ResultsPanel"
import FilterModal from "../features/search/FilterModal.tsx"
import type { SearchFilters, SearchResult, SearchHistoryItem } from "../types/search"
import { formatDate } from "../lib/utils"

const API_BASE = process.env.NODE_ENV === "development" ? "http://localhost:440/api" : "/api"

interface SearchPageProps {
    isHistoryOpen?: boolean
    setIsHistoryOpen?: (open: boolean) => void
}

export default function SearchPage({ isHistoryOpen: externalHistoryOpen, setIsHistoryOpen: setExternalHistoryOpen }: SearchPageProps) {
    const mathFieldRef = useRef<any>(null)
    // const searchParam = new URLSearchParams(window.location.search).get("q") || "";
    // mathFieldRef.current.value = searchParam ? decodeURIComponent(searchParam) : "";

    // Microphone status, Speech-to-LaTeX
    const [isListening, setIsListening] = useState(false)

    // Text/math mode
    const [mode, setMode] = useState<"math" | "text">("text")

    // Search filter modal
    const [isFilterVisible, setIsFilterVisible] = useState(false)
    const [filters, setFilters] = useState<SearchFilters>({ sources: [], mediaTypes: [] })

    // Search results
    const [searchResults, setSearchResults] = useState<SearchResult[]>([])
    const [isLoading, setIsLoading] = useState(false)

    // History
    const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([])
    const [isHistoryOpenInternal, setIsHistoryOpenInternal] = useState(false)
    const isHistoryOpen = externalHistoryOpen !== undefined ? externalHistoryOpen : isHistoryOpenInternal
    const setIsHistoryOpen = setExternalHistoryOpen || setIsHistoryOpenInternal

    // Results placeholder, set on mount
    const [placeholderMessage, setPlaceholderMessage] = useState<ReactNode>(null)
    useEffect(() => {
        setPlaceholderMessage(
            <div className={styles.resultsPlaceholderMessage}>
                <p>
                    Search for any mathematical topic, e.g. "Pythagorean Theorem," or a² + b² = c²
                </p>
            </div>
        )
    })

    const performSearch = () => {
        const currentLatex = mathFieldRef.current?.value?.trim() ?? ""
        if (!currentLatex) return

        setIsLoading(true)
        setSearchResults([])

        const newItem: SearchHistoryItem = { latex: currentLatex, timestamp: Date.now() }
        let updatedHistory = searchHistory.filter(item => item.latex !== currentLatex)
        updatedHistory.push(newItem)
        setSearchHistory(updatedHistory)
        sessionStorage.setItem("mathMexSearchHistory", JSON.stringify(updatedHistory))

        fetch(`${API_BASE}/search`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: currentLatex,
                sources: filters.sources,
                mediaTypes: filters.mediaTypes
            }),
        })
            .then(res => res.json())
            .then(data => {
                setSearchResults(data.results || [])
                setIsLoading(false)
            })
            .catch(() => {
                setSearchResults([])
                setIsLoading(false)
            })
    }

    return (
        <main className={styles.parentContainer}>
            <div className={styles.contentWrapper}>
                <div className={styles.topSection}>
                    <SearchPanel
                        isListening={isListening}
                        setIsListening={setIsListening}
                        mode={mode}
                        setMode={setMode}
                        filtersActive={filters.sources.length > 0 || filters.mediaTypes.length > 0}
                        activeFiltersCount={filters.sources.length + filters.mediaTypes.length}
                        mathFieldRef={mathFieldRef}
                        onSearch={() => performSearch()}
                        onToggleFilter={() => setIsFilterVisible(!isFilterVisible)}
                        onOpenHistorySidebar={() => setIsHistoryOpen(true)}
                    />
                </div>
                <div className={styles.bottomSection}>
                    <HistoryPanel
                        history={searchHistory.slice().reverse()}
                        onClearHistory={() => {
                            setSearchHistory([])
                            sessionStorage.removeItem("mathMexSearchHistory")
                        }}
                        onHistoryItemClick={(latex) => {
                            if (mathFieldRef.current) {
                                mathFieldRef.current.value = latex
                            }
                            setTimeout(() => performSearch(), 0)
                        }}
                        formatDate={formatDate}
                        isSidebarOpen={isHistoryOpen}
                        onCloseSidebar={() => setIsHistoryOpen(false)}
                    />
                    <ResultsPanel
                        results={searchResults}
                        isLoading={isLoading}
                        placeholderMessage={placeholderMessage}
                    />
                </div>
            </div>
            <FilterModal
                isOpen={isFilterVisible}
                onClose={() => setIsFilterVisible(false)}
                filters={filters}
                onFiltersChange={setFilters}
            />
            {/* Overlay for mobile sidebar */}
            {isHistoryOpen && (
                <div className={styles.overlay} onClick={() => setIsHistoryOpen(false)}></div>
            )}
        </main>
    )
}
