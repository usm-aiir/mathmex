import styles from "./Header.module.css"
import type { FC } from "react"
import { Sun, Moon } from "lucide-react"
import { useDarkMode } from "../hooks/darkMode"

const Header: FC = () => {
    const { isDarkMode, toggleDarkMode } = useDarkMode()

    const switchToLightMode = () => {
        if (isDarkMode) {
            toggleDarkMode()
        }
    }

    const switchToDarkMode = () => {
        if (!isDarkMode) {
            toggleDarkMode()
        }
    }

    return (
        <header className={styles.header}>
            <div className="container">
                <div className={styles.headerContent}>
                    <div className={styles.ornamentContainer}>
                        <div className={`${styles.ornament} ${styles.left}`}></div>
                        <div className={styles.toggleOverlay}>
                            <button
                                className={`${styles.themeButton} ${styles.lightModeButton} ${!isDarkMode ? styles.active : ""}`}
                                onClick={switchToLightMode}
                                aria-label="Switch to light mode"
                                title="Light Mode"
                            >
                                <Sun size={20} />
                            </button>
                        </div>
                    </div>
                    <div className={styles.titleContainer}>
                        <h1>
                            Math<span className={styles.highlight}>Mex</span>
                        </h1>
                        <p className={styles.tagline}>Mathematical Theorem Search Engine</p>
                    </div>
                    <div className={styles.ornamentContainer}>
                        <div className={`${styles.ornament} ${styles.right}`}></div>
                        <div className={styles.toggleOverlay}>
                            <button
                                className={`${styles.themeButton} ${styles.darkModeButton} ${isDarkMode ? styles.active : ""}`}
                                onClick={switchToDarkMode}
                                aria-label="Switch to dark mode"
                                title="Dark Mode"
                            >
                                <Moon size={20} />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    )
}

export default Header
