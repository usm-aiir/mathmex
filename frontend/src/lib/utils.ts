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
        return "Just now"
    } else if (diffMinutes < 60) {
        return `${diffMinutes} min ago`
    }

    const diffHours = Math.floor(diffMinutes / 60)
    if (diffHours < 24) {
        return `${diffHours}h ago`
    }

    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays} day${diffDays !== 1 ? "s" : ""} ago`
}

