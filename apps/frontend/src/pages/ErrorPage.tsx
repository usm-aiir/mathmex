/**
 * ErrorPage.tsx
 *
 * Displayed when MathMex is temporarily unavailable (e.g. lab server resources
 * allocated to other projects). Shown on app load when backend is down, or on 5xx errors.
 */
import styles from "./ErrorPage.module.css"

const ErrorPage = () => {
    const code = typeof window !== "undefined"
        ? (new URLSearchParams(window.location.search).get("code") || "503")
        : "503"

    return (
        <main className={styles.main}>
            <div className={styles.card}>
                <div className={styles.statusCode}>{code}</div>
                <h1 className={styles.title}>MathMex is temporarily unavailable</h1>
                <div className={styles.dividerMid} />
                <p className={styles.message}>
                    Our servers are being used for other projects right now.
                </p>
                <p className={styles.submessage}>
                    Please check back later — we appreciate your patience!
                </p>
            </div>
        </main>
    )
}

export default ErrorPage
