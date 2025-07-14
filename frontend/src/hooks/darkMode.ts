/**
 * darkMode.ts
 *
 * Custom React hook for managing dark/light theme state in the MathMex app.
 * Persists user preference in localStorage and syncs with system preference.
 */
"use client"

import { useState, useEffect } from "react"

/**
 * useDarkMode hook for toggling and persisting dark mode.
 *
 * @returns {{ isDarkMode: boolean, toggleDarkMode: () => void }} State and toggle function for dark mode.
 */
export function useDarkMode() {
    // Initialize dark mode state from localStorage or system preference
    const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
        // Check localStorage first
        const stored = localStorage.getItem("darkMode")
        if (stored !== null) {
            return JSON.parse(stored)
        }
        // Fall back to system preference
        return window.matchMedia("(prefers-color-scheme: dark)").matches
    })

    useEffect(() => {
        // Apply data-theme attribute to document root
        if (isDarkMode) {
            document.documentElement.setAttribute("data-theme", "dark")
        } else {
            document.documentElement.setAttribute("data-theme", "light")
        }

        // Store preference in localStorage
        localStorage.setItem("darkMode", JSON.stringify(isDarkMode))
    }, [isDarkMode])

    /**
     * Toggle between dark and light mode.
     */
    const toggleDarkMode = () => {
        setIsDarkMode(!isDarkMode)
    }

    return { isDarkMode, toggleDarkMode }
}
