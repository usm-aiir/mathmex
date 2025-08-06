import styles from "./HistorySidebar.module.css"
import {FC, useEffect, useRef, useState} from "react"
import type { SearchHistoryItem } from "../../types/search.ts"

/**
 * HistorySidebar.tsx
 *
 * Displays the user's search history for the current session, allowing re-search and clearing history.
 * Renders a list of previous queries and integrates with MathLive for math rendering.
 */
/**
 * Props for the HistorySidebar component.
 * @typedef {Object} SearchHistoryDisplayProps
 * @property {SearchHistoryItem[]} history - List of search history items.
 * @property {() => void} onClearHistory - Callback to clear the history.
 * @property {(latex: string) => void} onHistoryItemClick - Callback for clicking a history item.
 * @property {(date: Date) => string} formatDate - Function to format timestamps.
 */
interface SearchHistoryDisplayProps {
    history: SearchHistoryItem[]
    onClearHistory: () => void
    onHistoryItemClick: (latex: string) => void
    formatDate: (date: Date) => string
    isSidebarOpen?: boolean
}

/**
 * HistorySidebar component for displaying and interacting with search history.
 *
 * @param {SearchHistoryDisplayProps} props - The props for the component.
 * @returns {JSX.Element} The rendered history panel.
 */
const HistorySidebar: FC<SearchHistoryDisplayProps> = ({
    history,
    onClearHistory,
    onHistoryItemClick,
    formatDate,
    isSidebarOpen = false,
}) => {
    const [isGlass, setIsGlass] = useState(false)
    const historyListRef = useRef<HTMLDivElement>(null)
    const historyHeaderRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        // Re-render math expressions in history when history changes
        if (history.length > 0) {
            import("mathlive").then(mathlive => {
                mathlive.renderMathInDocument();
            });
        }
    }, [history]);

    useEffect(() => {
        const handleScroll = () => {
            if (historyListRef.current && historyHeaderRef.current) {
                const scrollTop = historyListRef.current.scrollTop
                setIsGlass(scrollTop > 0)
            }
        }

        const historyList = historyListRef.current
        if (historyList) {
            historyList.addEventListener('scroll', handleScroll)
            return () => historyList.removeEventListener('scroll', handleScroll)
        }
    }, [])

    // Always use sidebar functionality (not just mobile)
    return (
        <div
            className={`${styles.historySidebar} ${isSidebarOpen ? styles.open : ''}`}
        >
            <div ref={historyHeaderRef} className={`${styles.historyHeader} ${isGlass ? styles.glass : ''}`}>
                <h4 className={styles.historyTitle}>Search History</h4>
                {/* Button to clear history */}
                <button className={styles.clearHistoryBtn} onClick={onClearHistory}>
                    Clear
                </button>
            </div>
            <div ref={historyListRef} className={styles.historyList}>
                {history.length === 0 ? (
                    <p className={styles.emptyHistory}>No searches in this session</p>
                ) : (
                    history.map((item, index) => (
                        <div
                            key={`${item.timestamp}-${index}`}
                            className={styles.historyItem}
                            onClick={() => onHistoryItemClick(item.latex)}
                            title={`Search for: ${item.latex}\nSearched: ${formatDate(new Date(item.timestamp))}`}
                        >
                            <div className={styles.historyFormula}>
                                {/* Render math expression as LaTeX */}
                                <p>{`\$$${item.latex}\$$`}</p>
                            </div>
                            <div className={styles.historyTime}>{formatDate(new Date(item.timestamp))}</div>
                        </div>
                    ))
                )}
            </div>
        </div>
    )
}

export default HistorySidebar
