import styles from "./ResultsPanel.module.css"
import { FC, ReactNode, useEffect, useRef, useState } from "react"
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
    selectedResults: number[]
    onSelectionChange: (selectedResults: number[]) => void
}

const IS_DEV = process.env.NODE_ENV === "development";

/**
 * ResultsPanel component for displaying search results and pagination.
 *
 * @param {ResultsPanelProps} props - The props for the component.
 * @returns {JSX.Element} The rendered results panel.
 */
const ResultsPanel: FC<ResultsPanelProps> = ({ results, isLoading, placeholderMessage, selectedResults, onSelectionChange }) => {
    const [currentPage, setCurrentPage] = useState(1)
    const resultsDisplayRef = useRef<HTMLDivElement>(null)
    const resultsTitleRef = useRef<HTMLHeadingElement>(null)
    
    const RESULTS_PER_PAGE = 7
    const totalPages = Math.ceil(results.length / RESULTS_PER_PAGE)
    const startIndex = (currentPage - 1) * RESULTS_PER_PAGE
    const endIndex = startIndex + RESULTS_PER_PAGE
    const currentResults = results.slice(startIndex, endIndex)

    useEffect(() => {
        // Re-render math expressions in results when results change
        if (currentResults) {
            import("mathlive").then(mathlive => {
                mathlive.renderMathInDocument({
			TeX: {
				delimiters: {
					display: [['$$', '$$']],
					inline: [['$','$']]
				}
			}
		});
            });
        }
    }, [currentResults]);

    useEffect(() => {
        // Reset to first page when results change
        setCurrentPage(1);
    }, [results]);

    useEffect(() => {
        // Scroll to results section when page changes (except initial load)
        if (currentPage > 1 && resultsTitleRef.current) {
            // Calculate offset to account for sticky header
            // Find the sticky header element and get its actual height
            const stickyHeader = document.querySelector('[class*="topSection"]') as HTMLElement;
            const stickyHeaderHeight = stickyHeader ? stickyHeader.offsetHeight + 20 : 180; // 20px buffer
            
            const elementTop = resultsTitleRef.current.getBoundingClientRect().top + window.scrollY;
            const offsetTop = elementTop - stickyHeaderHeight;
            
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    }, [currentPage]);

    return (
                        <section className={styles.resultsContainer}>
            <h2 ref={resultsTitleRef} className={styles.resultsTitle}>Results</h2>
            <div ref={resultsDisplayRef} className={styles.resultsDisplay}>
                {isLoading ? (
                    <div className="loading">Searching</div>
                ) : results.length > 0 ? (
                    <>
                        {currentResults.map((result, displayIndex) => {
                            const actualIndex = startIndex + displayIndex;
                            return (
                                <div key={actualIndex} className={`${styles.resultItem} ${selectedResults.includes(actualIndex) ? styles.selected : ''}`}>
                                    <div className={styles.selectionControl}>
                                        <input
                                            type="checkbox"
                                            className={styles.resultCheckbox}
                                            checked={selectedResults.includes(actualIndex)}
                                            onChange={() => {
                                                onSelectionChange(selectedResults.includes(actualIndex)
                                                    ? selectedResults.filter(i => i !== actualIndex)
                                                    : [...selectedResults, actualIndex]);
                                            }}
                                            title="Include in AI summary"
                                        />
                                    </div>
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
                            ) : result.media_type === "image" ? (
                                <img src={result.link} alt={result.body_text}/>
                            ) : (
                                <p className={styles.resultDescription}>
                                    {result.body_text}
                                </p>
                            )}
                        </div>
                            );
                        })}
                    </>
                ) : (
                    placeholderMessage
                )}
            </div>
            {/* Pagination outside of results display */}
            {results.length > 0 && totalPages > 1 && (
                <div className={styles.pagination}>
                    <button 
                        onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                        disabled={currentPage === 1}
                        className={styles.paginationButton}
                    >
                        Previous
                    </button>
                    <span className={styles.pageInfo}>
                        Page {currentPage} of {totalPages}
                    </span>
                    <button 
                        onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                        disabled={currentPage === totalPages}
                        className={styles.paginationButton}
                    >
                        Next
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
 *
 * @param {string} url - The YouTube URL.
 * @returns {string} The extracted video ID, or an empty string if not found.
 */
function extractYouTubeId(url: string): string {
    const regex = /(?:youtube\.com\/.*v=|youtu\.be\/)([^&\n?#]+)/;
    const match = url.match(regex);
    return match ? match[1] : "";
}
