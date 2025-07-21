import React from "react"
import styles from "./SettingsSidebar.module.css"
import { useDarkMode } from "../hooks/darkMode"
import { X } from "lucide-react"

interface SettingsSidebarProps {
    open: boolean
    onClose: () => void
}

const SettingsSidebar: React.FC<SettingsSidebarProps> = ({ open, onClose }) => {
    const { isDarkMode, toggleDarkMode } = useDarkMode()
    return (
        <div className={`${styles.sidebar} ${open ? styles.open : ""}`}
            aria-hidden={!open}
        >
            <button className={styles.closeButton} onClick={onClose} aria-label="Close settings">
                <X size={24} />
            </button>
            <h2 className={styles.title}>Settings</h2>
            <div className={styles.section}>
                <span className={styles.label}>Dark Mode</span>
                <button
                    className={styles.pillSwitch}
                    onClick={toggleDarkMode}
                    aria-label={isDarkMode ? "Disable dark mode" : "Enable dark mode"}
                    title={isDarkMode ? "Disable dark mode" : "Enable dark mode"}
                    type="button"
                >
                    <span className={styles.track + (isDarkMode ? ' ' + styles.on : '')}>
                        <span className={styles.thumb + (isDarkMode ? ' ' + styles.thumbOn : '')} />
                    </span>
                </button>
            </div>
        </div>
    )
}

export default SettingsSidebar 