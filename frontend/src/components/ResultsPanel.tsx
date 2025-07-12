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

                            {result['media_type'] === "video" ? (
                                <div className={styles.resultDescription}>
                                    <iframe
                                        src={`https://www.youtube.com/embed/${extractYouTubeId(result.link)}`}
                                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                        allowFullScreen
                                        title={result.title}
                                    ></iframe>
                                </div>
                            ) : (
                                <p className={styles.resultDescription}>
                                    {result.body_text}
                                </p>
                            )}
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

/**
 * Extracts the YouTube video ID from a typical YouTube URL.
 * e.g. https://www.youtube.com/watch?v=abcd1234 -> abcd1234
 */
function extractYouTubeId(url: string): string {
    const regex = /(?:youtube\.com\/.*v=|youtu\.be\/)([^&\n?#]+)/;
    const match = url.match(regex);
    return match ? match[1] : "";
}
