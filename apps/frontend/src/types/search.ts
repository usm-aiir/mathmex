export interface SearchHistoryItem {
    latex: string
    timestamp: number
}

export interface SearchResult {
    title: string
    body_text: string
    link: string
    score: string
    media_type: string
}

export interface SearchFilters {
    sources: string[]
    mediaTypes: string[]
}