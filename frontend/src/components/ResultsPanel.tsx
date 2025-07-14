import styles from "./ResultsPanel.module.css"
import { FC, ReactNode, useEffect } from "react"
import { Download, ArrowLeft, ArrowRight } from "lucide-react"
import type { SearchResult } from "../types/search"

interface ResultsPanelProps {
    results: SearchResult[]
    isLoading: boolean
    placeholderMessage: ReactNode
    currentPage: number
    totalResults: number
    pageSize: number
    onNextPage: () => void
    onPrevPage: () => void
}

const ResultsPanel: FC<ResultsPanelProps> = ({ results, isLoading, placeholderMessage, currentPage, totalResults, pageSize, onNextPage, onPrevPage }) => {
    useEffect(() => {
        if (results.length > 0) {
            import("mathlive").then(mathlive => {
                mathlive.renderMathInDocument();
            });
        }
    }, [results]);

    const totalPages = Math.max(1, Math.ceil(totalResults / pageSize));

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
                            {result.media_type === "video" ? (
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
                            {result.media_type === "pdf" && (
                                <a
                                    className={styles.downloadButton}
                                    href={result.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    download
                                >
                                    <Download size={16} />
                                    <span>Download PDF</span>
                                </a>
                            )}
                        </div>
                    ))
                ) : (
                    placeholderMessage
                )}
            </div>
            {/* Pagination Controls */}
            {totalResults > pageSize && (
                <div className={styles.pagination}>
                    <button
                        className={styles.pageArrow}
                        onClick={onPrevPage}
                        disabled={currentPage === 1}
                        aria-label="Previous page"
                    >
                        <ArrowLeft size={20} />
                    </button>
                    <div className={styles.resultsRangeInfo}>
                        {(() => {
                            const start = (currentPage - 1) * pageSize + 1;
                            const end = Math.min(currentPage * pageSize, totalResults);
                            return `Showing results ${start}-${end}`;
                        })()}
                    </div>
                    <button
                        className={styles.pageArrow}
                        onClick={onNextPage}
                        disabled={currentPage === totalPages}
                        aria-label="Next page"
                    >
                        <ArrowRight size={20} />
                    </button>
                </div>
            )}
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
