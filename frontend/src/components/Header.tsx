// @ts-ignore
import styles from "./Header.module.css";
import { FC, useEffect, useState } from "react";
import { Link } from "react-router-dom";

const Header: FC = () => {
    const [dark, setDark] = useState(false);

    useEffect(() => {
        document.documentElement.setAttribute("data-theme", dark ? "dark" : "light");
    }, [dark]);

    return (
        <header className={styles.header}>
            <div className={`${styles.headerRow} container`}>
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
                <button
                    onClick={() => setDark((d) => !d)}
                    className={styles.themeToggle}
                    aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
                >
                    <span className={dark ? styles.icon : styles.iconActive}>
                        {/* Sun SVG */}
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="12" cy="12" r="5"/>
                            <g strokeLinecap="round">
                                <line x1="12" y1="1" x2="12" y2="3"/>
                                <line x1="12" y1="21" x2="12" y2="23"/>
                                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                                <line x1="1" y1="12" x2="3" y2="12"/>
                                <line x1="21" y1="12" x2="23" y2="12"/>
                                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                            </g>
                        </svg>
                    </span>
                    <span className={styles.switchTrack}>
                        <span className={dark ? styles.switchThumbDark : styles.switchThumbLight}></span>
                    </span>
                    <span className={dark ? styles.iconActive : styles.icon}>
                        {/* Moon SVG */}
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z"/>
                        </svg>
                    </span>
                </button>
            </div>
        </header>
    );
};

export default Header;
