import React, { useState, useEffect } from 'react';
import styles from './HelpModal.module.css';
import inputSwitchVideo from '../assets/input-mode-switch.mp4';
import functionInsertionVideo from '../assets/function-insertion.mp4';
import { Search, Keyboard, Goal } from "lucide-react";

/**
 * HelpModal.tsx
 *
 * Displays a multi-page modal tour/introduction for MathMex, including feature highlights and usage guides.
 * Used for onboarding new users and can be triggered from the Help button.
 */
/**
 * Props for the HelpModal component.
 * @typedef {Object} HelpModalProps
 * @property {boolean} open - Whether the modal is open.
 * @property {() => void} onClose - Function to close the modal.
 */
interface HelpModalProps {
  open: boolean;
  onClose: () => void;
}

/**
 * Pages for the onboarding tour, each with a title and content.
 */
const PAGES = [
  {
    title: 'Welcome to MathMex!',
    content: (
      <>
        <p className={styles.pageDescription}>
          MathMex is a search engine designed for conversational mathematics, allowing users to search for mathematical
          definitions and theorems.
        </p>

        <p className={styles.pageDescription}>
          We draw data from various sources across the internet, ensuring you get the theorems and definitions that are most relevant to your equation or problem.
        </p>
        <div className={styles.featureList}>
          <div className={styles.featureItem}>
            <span className={styles.featureIcon}><Search size={18}></Search></span>
            <span>Search theorems and formulas</span>
          </div>
          <div className={styles.featureItem}>
            <span className={styles.featureIcon}><Keyboard size={18}></Keyboard></span>
            <span>Search with plain English and written mathematics</span>
          </div>
          <div className={styles.featureItem}>
            <span className={styles.featureIcon}><Goal size={18}></Goal></span>
            <span>Get precise results</span>
          </div>
        </div>
      </>
    ),
  },
  {
    title: 'Hybrid Input Guide',
    content: (
      <>
        <p className={styles.pageDescription}>
          Use the on-screen switch to toggle between input modes.
        </p>
        <div className={styles.guideSteps}>
          <div className={styles.guideStep}>
            <div className={styles.stepNumber}>1</div>
            <div className={styles.stepContent}>
              <strong>Text Mode:</strong> Type normal text like "What is the quadratic formula?"
            </div>
          </div>
          <div className={styles.guideStep}>
            <div className={styles.stepNumber}>2</div>
            <div className={styles.stepContent}>
              <strong>Math Mode:</strong> Type rendered mathematics like, " a² + b² = c² "
            </div>
          </div>
        </div>
        <div className={styles.mediaContainer}>
          <video src={inputSwitchVideo} muted autoPlay loop playsInline className={styles.media} />
        </div>
      </>
    ),
  },
  {
    title: 'Insert Complex Functions',
    content: (
      <>
        <p className={styles.pageDescription}>
          Use the virtual keyboard and menu to insert complex mathematical functions.
        </p>
        <div className={styles.guideSteps}>
          <div className={styles.guideStep}>
            <div className={styles.stepNumber}>1</div>
            <div className={styles.stepContent}>
              <strong>Virtual Keyboard:</strong> Click the keyboard icon for common symbols
            </div>
          </div>
          <div className={styles.guideStep}>
            <div className={styles.stepNumber}>2</div>
            <div className={styles.stepContent}>
              <strong>Menu Access:</strong> Navigate to the " Insert ," tab, after clicking on the menu icon,
              for more advanced functions
            </div>
          </div>
        </div>
        <div className={styles.mediaContainer}>
          <video src={functionInsertionVideo} muted autoPlay loop playsInline className={styles.media} />
        </div>
      </>
    ),
  },
];

/**
 * Key for localStorage to track if the user has seen the intro.
 */
const LOCALSTORAGE_KEY = 'mathmex_seen_intro';

/**
 * HelpModal component for onboarding and feature tour.
 *
 * @param {HelpModalProps} props - The props for the component.
 * @returns {JSX.Element|null} The rendered modal, or null if not visible.
 */
const HelpModal: React.FC<HelpModalProps> = ({ open, onClose }) => {
  // Current page of the tour
  const [page, setPage] = useState(0);
  // Modal visibility state (syncs with open prop)
  const [visible, setVisible] = useState(open);

  useEffect(() => {
    setVisible(open);
  }, [open]);

  /**
   * Skip the tour, mark as seen in localStorage, and close the modal.
   */
  const handleSkip = () => {
    localStorage.setItem(LOCALSTORAGE_KEY, 'true');
    setVisible(false);
    onClose();
  };

  /**
   * Go to the next page, or finish the tour if on the last page.
   */
  const handleNext = () => {
    if (page < PAGES.length - 1) {
      setPage(page + 1);
    } else {
      handleSkip();
    }
  };

  /**
   * Go to the previous page.
   */
  const handleBack = () => {
    if (page > 0) setPage(page - 1);
  };

  if (!visible) return null;

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <h1 className={styles.modalTitle}>{PAGES[page].title}</h1>
        </div>
        
        <div className={styles.content}>
          {PAGES[page].content}
        </div>
        
        <div className={styles.footer}>
          {/* Skip button closes the tour and marks as seen */}
          <button className={styles.skipButton} onClick={handleSkip}>
            Skip Tour
          </button>
          
          {/* Page indicator dots */}
          <div className={styles.dotContainer}>
            {PAGES.map((_, i) => (
              <button
                key={i}
                className={`${styles.dot} ${i === page ? styles.active : ''}`}
                onClick={() => setPage(i)}
                aria-label={`Go to page ${i + 1}`}
              />
            ))}
          </div>
          
          {/* Navigation buttons */}
          <div className={styles.navButtons}>
            <button 
              onClick={handleBack} 
              disabled={page === 0} 
              className={`${styles.navButton} ${styles.backButton}`}
            >
              Back
            </button>
            <button 
              onClick={handleNext} 
              className={`${styles.navButton} ${styles.nextButton}`}
            >
              {page === PAGES.length - 1 ? 'Done' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Returns true if the user has not seen the intro tour (based on localStorage).
 * Used to determine if the HelpModal should be shown on first visit.
 *
 * @returns {boolean} Whether to show the first-time popup.
 */
export function shouldShowFirstTimePopup() {
  return !localStorage.getItem(LOCALSTORAGE_KEY);
}

export default HelpModal; 