import { ReactNode, useState, useRef, useEffect } from "react"
import styles from "./SearchPage.module.css"
import SearchPanel from "../features/search/SearchPanel"
import HistorySidebar from "../features/search/HistorySidebar.tsx"
import ResultsPanel from "../features/search/ResultsPanel"
import FilterModal from "../features/search/FilterModal.tsx"
import SummaryModal from "../features/search/SummaryModal"
import type { SearchFilters, SearchResult, SearchHistoryItem } from "../types/search"
import { formatDate } from "../lib/utils"

const API_BASE = process.env.NODE_ENV === "development" ? "http://localhost:440/api" : "/api"

// Settings management functions
const getSettingFromStorage = (key: string, defaultValue: boolean): boolean => {
    if (typeof window === 'undefined') return defaultValue
    const stored = localStorage.getItem(key)
    return stored !== null ? JSON.parse(stored) : defaultValue
}

const saveSettingToStorage = (key: string, value: boolean): void => {
    if (typeof window !== 'undefined') {
        localStorage.setItem(key, JSON.stringify(value))
    }
}

// Get current settings values (called before every search)
export const getCurrentSearchSettings = () => ({
    enhancedSearch: getSettingFromStorage('enhancedSearch', false),
    diversifyResults: getSettingFromStorage('diversifyResults', false)
})

// Settings hooks for UI components
export const useEnhancedSearch = () => {
    const [isEnabled, setIsEnabled] = useState(() => getSettingFromStorage('enhancedSearch', false))
    
    const toggle = () => {
        const newValue = !isEnabled
        setIsEnabled(newValue)
        saveSettingToStorage('enhancedSearch', newValue)
    }
    
    return { isEnhancedSearchEnabled: isEnabled, toggleEnhancedSearch: toggle }
}

export const useDiversifyResults = () => {
    const [isEnabled, setIsEnabled] = useState(() => getSettingFromStorage('diversifyResults', false))
    
    const toggle = () => {
        const newValue = !isEnabled
        setIsEnabled(newValue)
        saveSettingToStorage('diversifyResults', newValue)
    }
    
    return { isDiversifyResultsEnabled: isEnabled, toggleDiversifyResults: toggle }
}

export const useDarkMode = () => {
    const [isDarkMode, setIsDarkMode] = useState(() => {
        const stored = getSettingFromStorage('darkMode', false)
        const systemPreference = typeof window !== 'undefined' ? 
            window.matchMedia("(prefers-color-scheme: dark)").matches : false
        return stored !== null ? stored : systemPreference
    })

    useEffect(() => {
        if (typeof window !== 'undefined') {
            document.documentElement.setAttribute("data-theme", isDarkMode ? "dark" : "light")
        }
    }, [isDarkMode])

    const toggle = () => {
        const newValue = !isDarkMode
        setIsDarkMode(newValue)
        saveSettingToStorage('darkMode', newValue)
    }

    return { isDarkMode, toggleDarkMode: toggle }
}

interface SearchPageProps {
    isHistoryOpen?: boolean
    setIsHistoryOpen?: (open: boolean) => void
}

export default function SearchPage({ isHistoryOpen: externalHistoryOpen, setIsHistoryOpen: setExternalHistoryOpen }: SearchPageProps) {
    const mathFieldRef = useRef<any>(null)
    const searchParam = new URLSearchParams(window.location.search).get("q") || "";
    const initialLatex = searchParam ? decodeURIComponent(searchParam) : "";

    // Search filter modal
    const [isFilterVisible, setIsFilterVisible] = useState(false)
    const [filters, setFilters] = useState<SearchFilters>({ sources: [], mediaTypes: [] })

    // Search results
    const [searchResults, setSearchResults] = useState<SearchResult[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [selectedResults, setSelectedResults] = useState<number[]>([])

    // Clear selection when new search is performed
    useEffect(() => {
        setSelectedResults([])
    }, [searchResults])

    // AI Summary Modal state
    const [summary, setSummary] = useState<string>("");
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [currentQuery, setCurrentQuery] = useState<string>("");

    const closeSummaryModal = () => {
        setIsModalOpen(false);
        setSummary("");
        setCurrentQuery("");
    };

    // Handler for LLM answer generation
    const handleSummarization = async () => {
        const query = mathFieldRef.current?.value || "";

        if (!query) {
            alert("Please enter a query first.");
            return;
        }

        if (!searchResults || searchResults.length === 0) {
            alert("Please perform a search first to get results for summarization.");
            return;
        }

        // Use selected results if any are selected, otherwise use top 10 results
        let contextResults = selectedResults.length > 0
            ? selectedResults.map(i => searchResults[i])
            : searchResults.slice(0, 10);

         // Open modal and start loading
        setCurrentQuery(query);
        setIsModalOpen(true);
        setIsGenerating(true);
        setSummary("");

        try {
            const res = await fetch("/api/summarize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query,
                    results: contextResults
                }),
            });
            const data = await res.json();
            setSummary(data.summary || "No answer generated.");
        } catch (err) {
            setSummary("Backend not reachable! Please try again later.");
        } finally {
            setIsGenerating(false);
        }
    };

    // History
    const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([])
    const [isHistoryOpenInternal, setIsHistoryOpenInternal] = useState(false)
    const isHistoryOpen = externalHistoryOpen !== undefined ? externalHistoryOpen : isHistoryOpenInternal
    const setIsHistoryOpen = setExternalHistoryOpen || setIsHistoryOpenInternal

    // Load search history from localStorage on mount
    useEffect(() => {
        const stored = localStorage.getItem("mathMexSearchHistory")
        if (stored) {
            try {
                setSearchHistory(JSON.parse(stored))
            } catch (e) {
                setSearchHistory([])
            }
        }
    }, [])

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
    }, [])

    const performSearch = () => {
        const currentLatex = mathFieldRef.current?.value?.trim() ?? ""
        if (!currentLatex) return

        setIsLoading(true)
        setSearchResults([])

        const newItem: SearchHistoryItem = { latex: currentLatex, timestamp: Date.now() }
        let updatedHistory = searchHistory.filter(item => item.latex !== currentLatex)
        updatedHistory.push(newItem)
        setSearchHistory(updatedHistory)
        localStorage.setItem("mathMexSearchHistory", JSON.stringify(updatedHistory))

        // Get fresh settings for each search
        const searchSettings = getCurrentSearchSettings()
        
        fetch(`${API_BASE}/search`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: currentLatex,
                sources: filters.sources,
                mediaTypes: filters.mediaTypes,
                do_enhance: searchSettings.enhancedSearch,
                diversify: searchSettings.diversifyResults
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
                        filtersActive={filters.sources.length > 0 || filters.mediaTypes.length > 0}
                        activeFiltersCount={filters.sources.length + filters.mediaTypes.length}
                        mathFieldRef={mathFieldRef}
                        onSearch={() => performSearch()}
                        onToggleFilter={() => setIsFilterVisible(!isFilterVisible)}
                        initialLatex={initialLatex}
                        searchResults={searchResults}
                        selectedResults={selectedResults}
                        onSummarize={handleSummarization}
                    />
                </div>
                <div className={styles.bottomSection}>
                    <ResultsPanel
                        results={searchResults}
                        isLoading={isLoading}
                        placeholderMessage={placeholderMessage}
                        selectedResults={selectedResults}
                        onSelectionChange={setSelectedResults}
                    />
                </div>
            </div>
            <HistorySidebar
                history={searchHistory.slice().reverse()}
                onClearHistory={() => {
                    setSearchHistory([])
                    localStorage.removeItem("mathMexSearchHistory")
                }}
                onHistoryItemClick={(latex) => {
                    if (mathFieldRef.current) {
                        mathFieldRef.current.value = latex
                    }
                    setTimeout(() => performSearch(), 0)
                }}
                formatDate={formatDate}
                isSidebarOpen={isHistoryOpen}
            />
            <FilterModal
                isOpen={isFilterVisible}
                onClose={() => setIsFilterVisible(false)}
                filters={filters}
                onFiltersChange={setFilters}
            />
            {/* AI Summary Modal */}
            <SummaryModal
                isOpen={isModalOpen}
                onClose={closeSummaryModal}
                summary={summary}
                isLoading={isGenerating}
                query={currentQuery}
            />
            {/* Overlay for sidebar */}
            {isHistoryOpen && (
                <div className={styles.overlay} onClick={() => setIsHistoryOpen(false)}></div>
            )}
        </main>
    )
}
