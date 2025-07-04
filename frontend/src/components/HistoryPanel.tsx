"use client"

// @ts-ignore
import styles from "./HistoryPanel.module.css"
import { FC } from "react"
import { MathJax } from "better-react-mathjax"
import type { SearchHistoryItem } from "../types/search"

interface SearchHistoryDisplayProps {
    history: SearchHistoryItem[]
    onClearHistory: () => void
    onHistoryItemClick: (latex: string) => void
    formatDate: (date: Date) => string
}

const HistoryPanel: FC<SearchHistoryDisplayProps> = ({
                                                                       history,
                                                                       onClearHistory,
                                                                       onHistoryItemClick,
                                                                       formatDate,
                                                                   }) => {
    return (
        <div className={styles.searchHistory}>
            <div className={styles.historyHeader}>
                <h4>Search History</h4>
                <button className={styles.clearHistoryBtn} onClick={onClearHistory}>
                    Clear
                </button>
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
                                <MathJax inline dynamic>{`\$$${item.latex}\$$`}</MathJax>
                            </div>
                            <div className="history-time">{formatDate(new Date(item.timestamp))}</div>
                        </div>
                    ))
                )}
            </div>
        </div>
    )
}

export default HistoryPanel
