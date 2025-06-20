// @ts-ignore
import styles from "./Header.module.css";
import { FC } from "react"
import { Link } from "react-router-dom"

const Header: FC = () => {
    return (
        <header className={styles.header}>
            <div className="container">
                <Link to="/" className={styles.headerLink} style={{ textDecoration: "none", color: "inherit" }}>
                    <div className={styles.headerContent}>
                        <div className={`${styles.ornament} ${styles.left}`}></div>
                        <div className={styles.titleContainer}>
                            <h1>
                                Math<span className={styles.highlight}>Mex</span>
                            </h1>
                            <p className={styles.tagline}>Mathematical Theorem Search Engine</p>
                        </div>
                        <div className={`${styles.ornament} ${styles.right}`}></div>
                    </div>
                </Link>
            </div>
        </header>
    )
}

export default Header
