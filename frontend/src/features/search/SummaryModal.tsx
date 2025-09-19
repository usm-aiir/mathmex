import styles from './SummaryModal.module.css';
import { X, Sparkles } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

/**
 * SummaryModal.tsx
 *
 * Modal dialog for displaying AI-generated answers and summaries with glassmorphism styling.
 * Shows loading state while generating and renders LaTeX content when complete.
 */

interface SummaryModalProps {
    isOpen: boolean;
    onClose: () => void;
    summary: string;
    isLoading: boolean;
    query: string;
}

/**
 * Modal dialog for displaying AI-generated summaries and answers.
 *
 * @param {SummaryModalProps} props - The props for the component.
 * @returns {JSX.Element|null} The rendered modal, or null if not open.
 */
export default function SummaryModal({ isOpen, onClose, summary, isLoading, query }: SummaryModalProps) {
    const [isGlass, setIsGlass] = useState(false);
    const modalBodyRef = useRef<HTMLDivElement>(null);
    const modalHeaderRef = useRef<HTMLDivElement>(null);

    // Handle glassmorphism effects based on scroll
    useEffect(() => {
        if (!isOpen) return;

        const handleScroll = () => {
            if (modalBodyRef.current) {
                const scrollTop = modalBodyRef.current.scrollTop;
                const headerIsGlass = scrollTop > 0;
                setIsGlass(headerIsGlass);
            }
        };

        setTimeout(() => {
            if (modalBodyRef.current) {
                modalBodyRef.current.addEventListener('scroll', handleScroll, { passive: true });
                handleScroll();
            }
        }, 100);

        return () => {
            if (modalBodyRef.current) {
                modalBodyRef.current.removeEventListener('scroll', handleScroll);
            }
        };
    }, [isOpen]);

    // Render LaTeX when content changes
    useEffect(() => {
        if (isOpen) {
            const timer = setTimeout(() => {
                import("mathlive").then(mathlive => {
                    mathlive.renderMathInDocument();
                });
            }, 150);
            
            return () => clearTimeout(timer);
        }
    }, [isOpen, summary, query, isLoading]);

    const handleClose = () => {
        onClose();
    };

    const handleOverlayClick = (e: React.MouseEvent) => {
        if (e.target === e.currentTarget) {
            handleClose();
        }
    };

    useEffect(() => {
        if (!isOpen) return;

        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                handleClose();
            }
        };

        document.addEventListener('keydown', handleEscape);
        return () => document.removeEventListener('keydown', handleEscape);
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className={styles.modalOverlay} onClick={handleOverlayClick}>
            <div className={styles.modalContent}>
                <div 
                    ref={modalHeaderRef}
                    className={`${styles.modalHeader} ${isGlass ? styles.glass : ''}`}
                >
                    <h2>
                        <Sparkles size={24} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />
                        AI Generated Answer
                    </h2>
                    <button 
                        className={styles.closeButton}
                        onClick={handleClose}
                        aria-label="Close AI Summary"
                    >
                        <X size={20} />
                    </button>
                </div>

                <div ref={modalBodyRef} className={styles.modalBody}>
                    <div className={styles.querySection}>
                        <h3>Your Query:</h3>
                        <math-field
                            read-only
                            virtual-keyboard-mode="off"
                            contenteditable="false"
                        >{query}</math-field>
                    </div>

                    <div className={styles.answerSection}>
                        <h3>Answer:</h3>
                        
                        {isLoading ? (
                            <div className={styles.loadingContainer}>
                                <div className={`${styles.loadingText} loading`}>
                                    <i>Thinking</i>
                                </div>
                            </div>
                        ) : (
                            <div className={styles.summaryContent}>
                                {summary ? (
                                    <div dangerouslySetInnerHTML={{ __html: summary }} />
                                ) : (
                                    <div className={styles.noSummary}>
                                        No answer was generated. Please try again.
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
} 