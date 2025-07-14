/**
 * utils.ts
 *
 * Utility functions for the MathMex frontend.
 */
export function formatDate(date: Date): string {
    const now = new Date()
    const diffMilliseconds = now.getTime() - date.getTime()
    const diffMinutes = Math.floor(diffMilliseconds / (1000 * 60))

    if (diffMinutes < 1) {
        // Less than 1 minute ago
        return "Just now"
    } else if (diffMinutes < 60) {
        // Less than 1 hour ago
        return `${diffMinutes} min ago`
    } else {
        const diffHours = Math.floor(diffMinutes / 60)
        if (diffHours < 24) {
            // Less than 24 hours ago
            return `${diffHours}h ago`
        } else {
            // More than 24 hours ago, show time in HH:mm
            return `${date.getHours().toString().padStart(2, "0")}:${date.getMinutes().toString().padStart(2, "0")}`
        }
    }
}
