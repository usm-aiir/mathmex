import styles from "./Header.module.css"
import type { FC } from "react"
import { Sun, Moon } from "lucide-react"
import { useDarkMode } from "../hooks/darkMode"

/**
 * Header.tsx
 *
 * Application header component. Displays the app title, tagline, and theme (dark/light) toggle buttons.
 */
/**
 * Header component for the MathMex app.
 *
 * Displays the app title, tagline, and theme toggle buttons for dark/light mode.
 *
 * @returns {JSX.Element} The rendered header.
 */
const Header: FC = () => {
    // Get dark mode state and toggle function from custom hook
    const { isDarkMode, toggleDarkMode } = useDarkMode()

    // Switch to light mode if currently in dark mode
    const switchToLightMode = () => {
        if (isDarkMode) {
            toggleDarkMode()
        }
    }

    // Switch to dark mode if currently in light mode
    const switchToDarkMode = () => {
        if (!isDarkMode) {
            toggleDarkMode()
        }
    }

    return (
        <header className={styles.header}>
            <div className="container">
                <div className={styles.headerContent}>
                    {/* Left ornament and light mode toggle */}
                    <div className={styles.ornamentContainer}>
                        <div className={`${styles.ornament} ${styles.left}`}></div>
                        <div className={styles.toggleOverlay}>
                            <button
                                className={`${styles.themeButton} ${styles.lightModeButton} ${!isDarkMode ? styles.active : ""}`}
                                onClick={switchToLightMode}
                                aria-label="Switch to light mode"
                                title="Light Mode"
                            >
                                <Sun className={styles.themeIcon} />
                            </button>
                        </div>
                    </div>
                    {/* App title and tagline */}
                    <div className={styles.titleContainer}>
                        <h1>
                            Math<span className={styles.highlight}>Mex</span>
                        </h1>
                        <p className={styles.tagline}>Mathematical Theorem Search Engine</p>
                    </div>
                    {/* Right ornament and dark mode toggle */}
                    <div className={styles.ornamentContainer}>
                        <div className={`${styles.ornament} ${styles.right}`}></div>
                        <div className={styles.toggleOverlay}>
                            <button
                                className={`${styles.themeButton} ${styles.darkModeButton} ${isDarkMode ? styles.active : ""}`}
                                onClick={switchToDarkMode}
                                aria-label="Switch to dark mode"
                                title="Dark Mode"
                            >
                                <Moon className={styles.themeIcon} />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    )
}

export default Header
