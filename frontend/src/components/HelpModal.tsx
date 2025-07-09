import React, { useState, useEffect } from 'react';
import styles from './HelpModal.module.css';
import inputSwitchVideo from '../assets/input-mode-switch.mp4';
import functionInsertionVideo from '../assets/function-insertion.mp4';

interface HelpModalProps {
  open: boolean;
  onClose: () => void;
}

const PAGES = [
  {
    title: 'Welcome to MathMex!',
    content: (
      <>
        <p className={styles.pageDescription}>
          Your intelligent tool for searching mathematical expressions with natural language or LaTeX.
        </p>
        <div className={styles.featureList}>
          <div className={styles.featureItem}>
            <span className={styles.featureIcon}>🔍</span>
            <span>Search theorems and formulas</span>
          </div>
          <div className={styles.featureItem}>
            <span className={styles.featureIcon}>⌨️</span>
            <span>Switch between text and math input</span>
          </div>
          <div className={styles.featureItem}>
            <span className={styles.featureIcon}>🎯</span>
            <span>Get precise mathematical results</span>
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

const LOCALSTORAGE_KEY = 'mathmex_seen_intro';

const HelpModal: React.FC<HelpModalProps> = ({ open, onClose }) => {
  const [page, setPage] = useState(0);
  const [visible, setVisible] = useState(open);

  useEffect(() => {
    setVisible(open);
  }, [open]);

  const handleSkip = () => {
    localStorage.setItem(LOCALSTORAGE_KEY, 'true');
    setVisible(false);
    onClose();
  };

  const handleNext = () => {
    if (page < PAGES.length - 1) {
      setPage(page + 1);
    } else {
      handleSkip();
    }
  };

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
          <button className={styles.skipButton} onClick={handleSkip}>
            Skip Tour
          </button>
          
          <div className={styles.dots}>
            {PAGES.map((_, i) => (
              <button
                key={i}
                className={`${styles.dot} ${i === page ? styles.activeDot : ''}`}
                onClick={() => setPage(i)}
                aria-label={`Go to page ${i + 1}`}
              />
            ))}
          </div>
          
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
              {page === PAGES.length - 1 ? 'Finish' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export function shouldShowFirstTimePopup() {
  return !localStorage.getItem(LOCALSTORAGE_KEY);
}

export default HelpModal; 