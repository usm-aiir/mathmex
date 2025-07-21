import React from "react"
import styles from "./SettingsSidebar.module.css"
import ThemeSwitch from "./ThemeSwitch"
import { X } from "lucide-react"

interface SettingsSidebarProps {
    open: boolean
    onClose: () => void
}

const SettingsSidebar: React.FC<SettingsSidebarProps> = ({ open, onClose }) => {
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
                <ThemeSwitch />
            </div>
        </div>
    )
}

export default SettingsSidebar 