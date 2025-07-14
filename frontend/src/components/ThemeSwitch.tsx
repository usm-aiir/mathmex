import styles from "./ThemeSwitch.module.css"
import { Moon, Sun } from "lucide-react"
import { useDarkMode } from "../hooks/darkMode"

/**
 * ThemeSwitch.tsx
 *
 * Theme toggle button for switching between dark and light mode in the MathMex app.
 * Uses a custom hook to manage dark mode state.
 */
/**
 * ThemeSwitch component for toggling dark/light mode.
 *
 * @returns {JSX.Element} The rendered theme switch button.
 */
const ThemeSwitch = () => {
    // Get dark mode state and toggle function from custom hook
    const { isDarkMode, toggleDarkMode } = useDarkMode()

    return (
        <button
            className={styles.darkModeToggle}
            onClick={toggleDarkMode}
            aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
            title={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
        >
            <div className={`${styles.iconContainer} ${isDarkMode ? styles.light : styles.dark}`}>
                {/* Sun and Moon icons visually indicate the theme */}
                <Sun className={`${styles.icon} ${styles.sunIcon}`} size={20} />
                <Moon className={`${styles.icon} ${styles.moonIcon}`} size={20} />
            </div>
        </button>
    )
}

export default ThemeSwitch
