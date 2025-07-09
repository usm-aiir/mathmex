import styles from "./Footer.module.css"
import { Link } from "react-router-dom"
import { FC } from "react"

interface FooterProps {
    onHelpClick?: () => void;
}

const Footer: FC<FooterProps> = ({ onHelpClick }) => {
    return (
        <footer>
            <div className={styles.footer}>
                <Link to="/" className={styles.link}>Home</Link>
                {" | "}
                <Link to="/about" className={styles.link}>About</Link>
                {" | "}
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