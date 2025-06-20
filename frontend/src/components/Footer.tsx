// @ts-ignore
import styles from "./Footer.module.css"
import { Link } from "react-router-dom"

const Footer = () => {
    return (
        <footer>
            <div className={styles.footer}>
                <Link to="/" className={styles.link}>Home</Link>
                {" | "}
                <Link to="/about" className={styles.link}>About</Link>
                <p>
                    © {new Date().getFullYear()} MathMex ∙{" "}
                </p>
            </div>
        </footer>
    )
}

export default Footer