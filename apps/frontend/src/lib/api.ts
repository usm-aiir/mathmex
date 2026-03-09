/**
 * API base URL. Set VITE_API_BASE in project root .env for local dev (e.g. http://localhost:5001).
 */
export const API_BASE =
  import.meta.env.VITE_API_BASE || "https://api.mathmex.com";
