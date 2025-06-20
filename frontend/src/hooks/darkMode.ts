"use client"

import { useState, useEffect } from "react"

export function useDarkMode() {
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

        // Store preference
        localStorage.setItem("darkMode", JSON.stringify(isDarkMode))
    }, [isDarkMode])

    const toggleDarkMode = () => {
        setIsDarkMode(!isDarkMode)
    }

    return { isDarkMode, toggleDarkMode }
}
