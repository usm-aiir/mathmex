export interface SearchHistoryItem {
    latex: string
    timestamp: number
}

export interface SearchResult {
    title: string
    formula: string
    description: string
    tags: string[]
    year: string
}