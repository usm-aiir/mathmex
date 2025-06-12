"use client"

// @ts-ignore
import styles from "./MathKeyboard.module.css"

interface KeyConfig {
    display: string
    latex: string
}

interface KeyboardSectionConfig {
    title: string
    keys: KeyConfig[]
}

interface MathKeyboardProps {
    layout: KeyboardSectionConfig[]
    onKeyPress: (latex: string) => void
}

const MathKeyboard: React.FC<MathKeyboardProps> = ({ layout, onKeyPress }) => {
    return (
        <div className={styles.mathKeyboard}>
            {layout.map((section) => (
                <div key={section.title} className={styles.keyboardSection}>
                    <h4>{section.title}</h4>
                    <div className={styles.keyRow}>
                        {section.keys.map((key) => (
                            <button
                                key={key.latex}
                                className={styles.key}
                                data-latex={key.latex}
                                onClick={() => onKeyPress(key.latex)}
                                title={`Insert ${key.latex}`}
                            >
                                {key.display}
                            </button>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    )
}

export default MathKeyboard
