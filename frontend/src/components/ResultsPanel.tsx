import styles from "./ResultsPanel.module.css"
import { FC, ReactNode } from "react"
import { MathJax } from "better-react-mathjax"
import type { SearchResult } from "../types/search"

interface ResultsPanelProps {
    results: SearchResult[]
    isLoading: boolean
    placeholderMessage: ReactNode
}

const ResultsPanel: FC<ResultsPanelProps> = ({ results, isLoading, placeholderMessage }) => {
    return (
        <section className={styles.resultsSection}>
            <h2 className={styles.resultsSectionTitle}>Results</h2>
            <div className={styles.resultsContainer}>
                {isLoading ? (
                    <div className="loading">Searching</div>
                ) : results.length > 0 ? (
                    results.map((result, index) => (
                        <div key={index} className={styles.resultItem}>
                            <h3 className={styles.resultTitle}>{result.title}</h3>
                            <div className={styles.resultFormula}>
                                <MathJax dynamic>{`$$${result.body_text}$$`}</MathJax>
                            </div>
                            <p className={styles.resultDescription}>{result.link}</p>
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
