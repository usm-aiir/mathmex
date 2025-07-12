import styles from './FilterModal.module.css';
import { X, Check } from 'lucide-react';
import type { SearchFilters } from '../types/search';

interface FilterModalProps {
    isOpen: boolean;
    onClose: () => void;
    filters: SearchFilters;
    onFiltersChange: (filters: SearchFilters) => void;
}

const AVAILABLE_SOURCES = [
    { id: 'arxiv', name: 'arXiv', description: 'Research papers and preprints' },
    { id: 'math-overflow', name: 'Math Overflow', description: 'Research-level mathematics' },
    { id: 'math-stack-exchange', name: 'Math Stack Exchange', description: 'Mathematics Q&A' },
    { id: 'mathematica', name: 'Mathematica', description: 'Wolfram documentation' },
    { id: 'wikipedia', name: 'Wikipedia', description: 'Mathematical articles' },
    { id: 'youtube', name: 'YouTube', description: 'Educational videos' }
];

const AVAILABLE_MEDIA_TYPES = [
    { id: 'article', name: 'Articles', description: 'Text-based content' },
    { id: 'pdf', name: 'PDFs', description: 'Research papers and documents' },
    { id: 'video', name: 'Videos', description: 'Educational videos and lectures' }
];

export default function FilterModal({ isOpen, onClose, filters, onFiltersChange }: FilterModalProps) {
    if (!isOpen) return null;

    const toggleSource = (sourceId: string) => {
        const newSources = filters.sources.includes(sourceId)
            ? filters.sources.filter(id => id !== sourceId)
            : [...filters.sources, sourceId];
        onFiltersChange({ ...filters, sources: newSources });
    };

    const toggleMediaType = (mediaTypeId: string) => {
        const newMediaTypes = filters.mediaTypes.includes(mediaTypeId)
            ? filters.mediaTypes.filter(id => id !== mediaTypeId)
            : [...filters.mediaTypes, mediaTypeId];
        onFiltersChange({ ...filters, mediaTypes: newMediaTypes });
    };

    const selectAllSources = () => {
        onFiltersChange({ ...filters, sources: AVAILABLE_SOURCES.map(s => s.id) });
    };

    const clearAllSources = () => {
        onFiltersChange({ ...filters, sources: [] });
    };

    const selectAllMediaTypes = () => {
        onFiltersChange({ ...filters, mediaTypes: AVAILABLE_MEDIA_TYPES.map(m => m.id) });
    };

    const clearAllMediaTypes = () => {
        onFiltersChange({ ...filters, mediaTypes: [] });
    };

    return (
        <div className={styles.modalOverlay} onClick={onClose}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                <div className={styles.modalHeader}>
                    <h2>Search Filters</h2>
                    <button className={styles.closeButton} onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>

                <div className={styles.modalBody}>
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

                <div className={styles.modalFooter}>
                    <button className={styles.applyButton} onClick={onClose}>
                        Apply Filters
                    </button>
                </div>
            </div>
        </div>
    );
} 