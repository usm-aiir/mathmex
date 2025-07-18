import styles from "./Footer.module.css"
import { Link } from "react-router-dom"
import { FC } from "react"

/**
 * Footer.tsx
 *
 * Application footer component. Displays navigation links and a Help button, and shows copyright.
 */
/**
 * Props for the Footer component.
 * @typedef {Object} FooterProps
 * @property {() => void=} onHelpClick - Optional callback for when the Help button is clicked.
 */
interface FooterProps {
    onHelpClick?: () => void;
}

/**
 * Footer component for the MathMex app.
 *
 * @param {FooterProps} props - The props for the component.
 * @returns {JSX.Element} The rendered footer.
 */
const Footer: FC<FooterProps> = ({ onHelpClick }) => {
    return (
        <footer>
            <div className={styles.footer}>
                {/* Navigation links */}
                <Link to="/" className={styles.link}>Home</Link>
                {" | "}
                <Link to="/about" className={styles.link}>About</Link>
                {" | "}
                <Link to="/survey" className={styles.link}>Survey</Link>
                {" | "}
                {/* Help button triggers the Help modal */}
                <button
                    aria-label="Show help / introduction"
                    onClick={onHelpClick}
                    className={styles.link}
                    style={{
                        background: "none",
                        border: "none",
                        padding: 0,
                        font: "inherit",
                        color: "inherit",
                        cursor: "pointer",
                        textDecoration: "none",
                        textUnderlineOffset: "2px"
                    }}
                >
                    Help
                </button>
                <p>
                    © {new Date().getFullYear()} MathMex ∙{" "}
                </p>
            </div>
        </footer>
    )
}

export default Footer