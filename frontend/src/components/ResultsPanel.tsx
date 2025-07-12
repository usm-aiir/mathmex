import styles from "./ResultsPanel.module.css"
import { FC, ReactNode, useEffect } from "react"
import type { SearchResult } from "../types/search"

interface ResultsPanelProps {
    results: SearchResult[]
    isLoading: boolean
    placeholderMessage: ReactNode
}

const ResultsPanel: FC<ResultsPanelProps> = ({ results, isLoading, placeholderMessage }) => {
    useEffect(() => {
        if (results.length > 0) {
            import("mathlive").then(mathlive => {
                mathlive.renderMathInDocument();
            });
        }
    }, [results]);

    return (
        <section className={styles.resultsSection}>
            <h2 className={styles.resultsSectionTitle}>Results</h2>
            <div className={styles.resultsContainer}>
                {isLoading ? (
                    <div className="loading">Searching...</div>
                ) : results.length > 0 ? (
                    results.map((result, index) => (
                        <div key={index} className={styles.resultItem}>
                            <h3 className={styles.resultTitle}>{result.title}</h3>
                            <a className={styles.source} href={result.link} target="_blank" rel="noopener noreferrer">
                                {result.link}
                            </a>
                            <p>
                                {result.body_text}
                            </p>
                        </div>
                    ))
                ) : (
                    placeholderMessage
                )}
            </div>
        </section>
    )
}

export default ResultsPanel
