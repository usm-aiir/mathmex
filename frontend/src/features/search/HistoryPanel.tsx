import styles from "./HistoryPanel.module.css"
import {FC, useEffect} from "react"
import type { SearchHistoryItem } from "../../types/search.ts"
import { X } from "lucide-react"

/**
 * HistoryPanel.tsx
 *
 * Displays the user's search history for the current session, allowing re-search and clearing history.
 * Renders a list of previous queries and integrates with MathLive for math rendering.
 */
/**
 * Props for the HistoryPanel component.
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
    onCloseSidebar?: () => void
}

/**
 * HistoryPanel component for displaying and interacting with search history.
 *
 * @param {SearchHistoryDisplayProps} props - The props for the component.
 * @returns {JSX.Element} The rendered history panel.
 */
const HistoryPanel: FC<SearchHistoryDisplayProps> = ({
    history,
    onClearHistory,
    onHistoryItemClick,
    formatDate,
    isSidebarOpen = false,
    onCloseSidebar,
}) => {
    useEffect(() => {
        // Re-render math expressions in history when history changes
        if (history.length > 0) {
            import("mathlive").then(mathlive => {
                mathlive.renderMathInDocument();
            });
        }
    }, [history]);

    // Determine if mobile (window width <= 480px)
    const isMobile = typeof window !== 'undefined' && window.innerWidth <= 480;

    return (
        <div
            className={
                isMobile
                    ? `${styles.historySidebar} ${isSidebarOpen ? styles.open : ''}`
                    : styles.historyContainer
            }
        >
            <div className={styles.historyHeader}>
                <h4>Search History</h4>
                {/* Button to clear history */}
                <button className={styles.clearHistoryBtn} onClick={onClearHistory}>
                    Clear
                </button>
                {/* Close button for mobile sidebar */}
                {isMobile && onCloseSidebar && (
                    <button className={styles.closeButton} onClick={onCloseSidebar} aria-label="Close history sidebar">
                        <X size={24} />
                    </button>
                )}
            </div>
            <div className={styles.historyList}>
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

export default HistoryPanel
