// @ts-ignore
import styles from "./Footer.module.css"
import { FC } from "react"

const Footer: FC = () => {
    return (
        <footer>
            <div className={styles.footer}>
                <p>© {new Date().getFullYear()} MathMex ∙ About </p>
            </div>
        </footer>
    )
}

export default Footer
