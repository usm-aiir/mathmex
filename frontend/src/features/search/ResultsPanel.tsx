import styles from "./ResultsPanel.module.css"
import { FC, ReactNode, useEffect } from "react"
import type { SearchResult } from "../../types/search.ts"

/**
 * ResultsPanel.tsx
 *
 * Displays search results, including pagination and support for video and text results.
 * Handles rendering of result items and pagination controls.
 */
/**
 * Props for the ResultsPanel component.
 * @typedef {Object} ResultsPanelProps
 * @property {SearchResult[]} results - Array of search results to display.
 * @property {boolean} isLoading - Whether results are loading.
 * @property {ReactNode} placeholderMessage - Message to show when no results.
 * @property {number} currentPage - Current page number.
 * @property {number} totalResults - Total number of results.
 * @property {number} pageSize - Number of results per page.
 * @property {() => void} onNextPage - Callback for next page.
 * @property {() => void} onPrevPage - Callback for previous page.
 */
interface ResultsPanelProps {
    results: SearchResult[]
    isLoading: boolean
    placeholderMessage: ReactNode
}

const IS_DEV = process.env.NODE_ENV === "development";

/**
 * ResultsPanel component for displaying search results and pagination.
 *
 * @param {ResultsPanelProps} props - The props for the component.
 * @returns {JSX.Element} The rendered results panel.
 */
const ResultsPanel: FC<ResultsPanelProps> = ({ results, isLoading, placeholderMessage }) => {
    useEffect(() => {
        // Re-render math expressions in results when results change
        if (results.length > 0) {
            import("mathlive").then(mathlive => {
                mathlive.renderMathInDocument();
            });
        }
    }, [results]);

    return (
        <section className={styles.resultsContainer}>
            <h2 className={styles.resultsTitle}>Results</h2>
            <div className={styles.resultsDisplay}>
                {isLoading ? (
                    <div className="loading">Searching...</div>
                ) : results.length > 0 ? (
                    results.map((result, index) => (
                        <div key={index} className={styles.resultItem}>
                            <div className={styles.resultHeader}>
                                <h3 className={styles.resultTitle}>{result.title}</h3>
                                {/* Add visual relevance scores if in dev */}
                                {IS_DEV && (
                                    <span className={styles.resultScore} title="Relevance score">
                                        {parseFloat(result.score).toFixed(2)}
                                    </span>
                                )}
                            </div>
                            <a className={styles.source} href={result.link} target="_blank" rel="noopener noreferrer">
                                {result.link}
                            </a>
                            {result.media_type === "video" ? (
                                <div className={styles.resultDescription}>
                                    {/* Embed YouTube video if media_type is video */}
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
 *
 * @param {string} url - The YouTube URL.
 * @returns {string} The extracted video ID, or an empty string if not found.
 */
function extractYouTubeId(url: string): string {
    const regex = /(?:youtube\.com\/.*v=|youtu\.be\/)([^&\n?#]+)/;
    const match = url.match(regex);
    return match ? match[1] : "";
}
