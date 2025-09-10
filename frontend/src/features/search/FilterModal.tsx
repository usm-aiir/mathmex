import styles from './FilterModal.module.css';
import { X, Check } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import type { SearchFilters } from '../../types/search.ts';

/**
 * FilterModal.tsx
 *
 * Modal dialog for selecting search filters (sources and media types) in the MathMex app.
 * Allows users to filter search results by source and media type.
 */
/**
 * Props for the FilterModal component.
 * @typedef {Object} FilterModalProps
 * @property {boolean} isOpen - Whether the modal is open.
 * @property {() => void} onClose - Function to close the modal.
 * @property {SearchFilters} filters - Current filter state.
 * @property {(filters: SearchFilters) => void} onFiltersChange - Callback to update filters.
 */
interface FilterModalProps {
    isOpen: boolean;
    onClose: () => void;
    filters: SearchFilters;
    onFiltersChange: (filters: SearchFilters) => void;
}

/**
 * List of available sources for filtering.
 */
const AVAILABLE_SOURCES = [
    { id: 'arxiv', name: 'arXiv', description: 'Research papers and preprints' },
    { id: 'math-overflow', name: 'Math Overflow', description: 'Research-level mathematics' },
    { id: 'math-stack-exchange', name: 'Math Stack Exchange', description: 'Mathematics Q&A' },
    { id: 'mathematica', name: 'Mathematica', description: 'Wolfram documentation' },
    { id: 'wikipedia', name: 'Wikipedia', description: 'Mathematical articles' },
    { id: 'youtube', name: 'YouTube', description: 'Educational videos' },
    { id: 'proof-wiki', name: 'ProofWiki', description: 'Formal Proofs'}
];

/**
 * List of available media types for filtering.
 */
const AVAILABLE_MEDIA_TYPES = [
    { id: 'article', name: 'Articles', description: 'Text-based content' },
    { id: 'pdf', name: 'PDFs', description: 'Research papers and documents' },
    { id: 'video', name: 'Videos', description: 'Educational videos and lectures' }
];

/**
 * Modal dialog for selecting search filters (sources and media types).
 *
 * @param {FilterModalProps} props - The props for the component.
 * @returns {JSX.Element|null} The rendered modal, or null if not open.
 */
export default function FilterModal({ isOpen, onClose, filters, onFiltersChange }: FilterModalProps) {
    const [isGlass, setIsGlass] = useState(false);
    const [isFooterGlass, setIsFooterGlass] = useState(true);
    const modalBodyRef = useRef<HTMLDivElement>(null);
    const modalHeaderRef = useRef<HTMLDivElement>(null);
    const modalFooterRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Only set up scroll detection when modal is open
        if (!isOpen) return;

        const handleScroll = () => {
            console.log('Scroll event fired!');
            
            if (modalBodyRef.current) {
                const scrollTop = modalBodyRef.current.scrollTop;
                console.log('Current scrollTop:', scrollTop);
                
                // Simple condition: if scrolled at all, apply glass effect
                const headerIsGlass = scrollTop > 0;
                console.log('Setting header glass to:', headerIsGlass);
                
                setIsGlass(headerIsGlass);
                
                // Footer logic
                if (modalFooterRef.current) {
                    const scrollHeight = modalBodyRef.current.scrollHeight;
                    const clientHeight = modalBodyRef.current.clientHeight;
                    const maxScrollTop = scrollHeight - clientHeight;
                    const footerIsGlass = scrollTop < maxScrollTop;
                    console.log('Setting footer glass to:', footerIsGlass);
                    setIsFooterGlass(footerIsGlass);
                }
            }
        };

        // Wait a bit for the modal to render, then set up scroll listener
        const timer = setTimeout(() => {
            const modalBody = modalBodyRef.current;
            if (modalBody) {
                console.log('Setting up scroll listener on modal body');
                modalBody.addEventListener('scroll', handleScroll);
                
                // Initial check
                console.log('Running initial scroll check');
                handleScroll();
                
                return () => {
                    console.log('Removing scroll listener');
                    modalBody.removeEventListener('scroll', handleScroll);
                };
            } else {
                console.log('Modal body ref is still null after timeout');
            }
        }, 100);

        return () => clearTimeout(timer);
    }, [isOpen]); // Add isOpen as dependency

    if (!isOpen) return null;

    // Toggle a source in the filter list
    const toggleSource = (sourceId: string) => {
        const newSources = filters.sources.includes(sourceId)
            ? filters.sources.filter(id => id !== sourceId)
            : [...filters.sources, sourceId];
        onFiltersChange({ ...filters, sources: newSources });
    };

    // Toggle a media type in the filter list
    const toggleMediaType = (mediaTypeId: string) => {
        const newMediaTypes = filters.mediaTypes.includes(mediaTypeId)
            ? filters.mediaTypes.filter(id => id !== mediaTypeId)
            : [...filters.mediaTypes, mediaTypeId];
        onFiltersChange({ ...filters, mediaTypes: newMediaTypes });
    };

    // Select all sources
    const selectAllSources = () => {
        onFiltersChange({ ...filters, sources: AVAILABLE_SOURCES.map(s => s.id) });
    };

    // Clear all sources
    const clearAllSources = () => {
        onFiltersChange({ ...filters, sources: [] });
    };

    // Select all media types
    const selectAllMediaTypes = () => {
        onFiltersChange({ ...filters, mediaTypes: AVAILABLE_MEDIA_TYPES.map(m => m.id) });
    };

    // Clear all media types
    const clearAllMediaTypes = () => {
        onFiltersChange({ ...filters, mediaTypes: [] });
    };

    return (
        <div className={styles.modalOverlay} onClick={onClose}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                <div ref={modalHeaderRef} className={`${styles.modalHeader} ${isGlass ? styles.glass : ''}`}>
                    <h2>Search Filters</h2>
                    <button className={styles.closeButton} onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>

                <div ref={modalBodyRef} className={styles.modalBody}>
                    {/* Sources Section */}
                    <div className={styles.filterSection}>
                        <div className={styles.sectionHeader}>
                            <h3>Sources</h3>
                            <div className={styles.sectionActions}>
                                <button 
                                    className={styles.actionButton}
                                    onClick={selectAllSources}
                                >
                                    Select All
                                </button>
                                <button 
                                    className={styles.actionButton}
                                    onClick={clearAllSources}
                                >
                                    Clear All
                                </button>
                            </div>
                        </div>
                        <div className={styles.filterGrid}>
                            {AVAILABLE_SOURCES.map(source => (
                                <label key={source.id} className={styles.filterItem}>
                                    <input
                                        type="checkbox"
                                        checked={filters.sources.includes(source.id)}
                                        onChange={() => toggleSource(source.id)}
                                        className={styles.checkbox}
                                    />
                                    <div className={styles.filterItemContent}>
                                        <span className={styles.filterItemName}>{source.name}</span>
                                        <span className={styles.filterItemDescription}>{source.description}</span>
                                    </div>
                                    {filters.sources.includes(source.id) && (
                                        <Check size={16} className={styles.checkIcon} />
                                    )}
                                </label>
                            ))}
                        </div>
                    </div>

                    {/* Media Types Section */}
                    <div className={styles.filterSection}>
                        <div className={styles.sectionHeader}>
                            <h3>Media Types</h3>
                            <div className={styles.sectionActions}>
                                <button 
                                    className={styles.actionButton}
                                    onClick={selectAllMediaTypes}
                                >
                                    Select All
                                </button>
                                <button 
                                    className={styles.actionButton}
                                    onClick={clearAllMediaTypes}
                                >
                                    Clear All
                                </button>
                            </div>
                        </div>
                        <div className={styles.filterGrid}>
                            {AVAILABLE_MEDIA_TYPES.map(mediaType => (
                                <label key={mediaType.id} className={styles.filterItem}>
                                    <input
                                        type="checkbox"
                                        checked={filters.mediaTypes.includes(mediaType.id)}
                                        onChange={() => toggleMediaType(mediaType.id)}
                                        className={styles.checkbox}
                                    />
                                    <div className={styles.filterItemContent}>
                                        <span className={styles.filterItemName}>{mediaType.name}</span>
                                        <span className={styles.filterItemDescription}>{mediaType.description}</span>
                                    </div>
                                    {filters.mediaTypes.includes(mediaType.id) && (
                                        <Check size={16} className={styles.checkIcon} />
                                    )}
                                </label>
                            ))}
                        </div>
                    </div>
                </div>

                <div ref={modalFooterRef} className={`${styles.modalFooter} ${isFooterGlass ? styles.glass : ''}`}>
                    <button className={styles.applyButton} onClick={onClose}>
                        Apply Filters
                    </button>
                </div>
            </div>
        </div>
    );
} 