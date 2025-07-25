import styles from "./Header.module.css"
import type { FC } from "react"
import { useState } from "react"
import { Settings, History } from "lucide-react"
import SettingsSidebar from "./SettingsSidebar"

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
const Header: FC<{ onOpenHistorySidebar?: () => void }> = ({ onOpenHistorySidebar }) => {
    const [sidebarOpen, setSidebarOpen] = useState(false)

    return (
        <header className={styles.header}>
            {/* Search history button on the left */}
            <div className={`${styles.buttonContainer} ${styles.left}`}>
                <button
                    id={styles.historyButton}
                    className={styles.headerButton}
                    onClick={onOpenHistorySidebar}
                    aria-label="Open search history"
                    title="Search History"
                >
                    <History size={28} />
                </button>
            </div>
            <div className="container">
                <div className={styles.headerContent}>
                    <div className={styles.titleContainer}>
                        <h1>
                            Math<span className={styles.highlight}>Mex</span>
                        </h1>
                        <p className={styles.tagline}>Mathematical Theorem Search Engine</p>
                    </div>
                </div>
            </div>
            {/* Settings button on the right */}
            <div className={`${styles.buttonContainer} ${styles.right}`}>
                <button
                    className={styles.headerButton}
                    onClick={() => setSidebarOpen(true)}
                    aria-label="Open settings"
                    title="Settings"
                >
                    <Settings size={26} />
                </button>
            </div>
            <SettingsSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        </header>
    )
}

export default Header
