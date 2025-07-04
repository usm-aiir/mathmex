import styles from "./ThemeSwitch.module.css"
import { Moon, Sun } from "lucide-react"
import { useDarkMode } from "../hooks/darkMode"

const ThemeSwitch = () => {
    const { isDarkMode, toggleDarkMode } = useDarkMode()

    return (
        <button
            className={styles.darkModeToggle}
            onClick={toggleDarkMode}
            aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
            title={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
        >
            <div className={`${styles.iconContainer} ${isDarkMode ? styles.light : styles.dark}`}>
                <Sun className={`${styles.icon} ${styles.sunIcon}`} size={20} />
                <Moon className={`${styles.icon} ${styles.moonIcon}`} size={20} />
            </div>
        </button>
    )
}

export default ThemeSwitch
