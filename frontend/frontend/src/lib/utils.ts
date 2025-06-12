export function formatDate(date: Date): string {
    const now = new Date()
    const diffMilliseconds = now.getTime() - date.getTime()
    const diffMinutes = Math.floor(diffMilliseconds / (1000 * 60))

    if (diffMinutes < 1) {
        return "Just now"
    } else if (diffMinutes < 60) {
        return `${diffMinutes} min ago`
    } else {
        const diffHours = Math.floor(diffMinutes / 60)
        if (diffHours < 24) {
            return `${diffHours}h ago`
        } else {
            return `${date.getHours().toString().padStart(2, "0")}:${date.getMinutes().toString().padStart(2, "0")}`
        }
    }
}
