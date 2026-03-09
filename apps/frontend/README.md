# MathMex Frontend

React application for the MathMex search UI. See the [main README](../../README.md) for full project setup.

## Run (dev)

From project root:

```sh
cd apps/frontend && npm run dev
```

Or from this directory: `npm run dev`

## Configuration

The frontend loads `.env` from the project root (see `vite.config.ts` envDir). For local dev, add to `.env`:

```
VITE_API_BASE=http://localhost:5001
```

This points the frontend at the backend API. Omit for production builds that use the default API URL.

## Structure

- `src/` — React components, pages, styles
- `index.html` — Entry HTML
- `vite.config.ts` — Vite config

## Build

```sh
npm run build
```

Output goes to `dist/`.
