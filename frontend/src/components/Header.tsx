// @ts-ignore
import styles from "./Header.module.css";
import { FC } from "react"

const Header: FC = () => {
    return (
        <header className={styles.header}>
            <div className="container">
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
            </div>
        </header>
    )
}

export default Header
