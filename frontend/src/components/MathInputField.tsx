"use client"
import { FC, MutableRefObject } from "react"
import { EditableMathField } from "react-mathquill"
import type { MathField } from "react-mathquill"

interface InputFieldProps {
    latex: string
    setLatex: (latex: string) => void
    mathFieldRef: MutableRefObject<MathField | null>
    onEnter?: () => void
}

const MathInputField: FC<InputFieldProps> = ({ latex, setLatex, mathFieldRef, onEnter }) => {
    const handleClick = () => {
        mathFieldRef.current?.focus()
    }

    return (
        <div className="math-field" role="textbox" aria-label="Math formula input" onClick={handleClick}>
            <EditableMathField
                latex={latex}
                onChange={(mathField) => {
                    if (mathField) {
                        setLatex(mathField.latex())
                    }
                }}
                mathquillDidMount={(mathField) => {
                    mathFieldRef.current = mathField
                }}
                config={{
                    spaceBehavesLikeTab: true,
                    handlers: {
                        enter: () => {
                            onEnter?.()
                            return false
                        },
                    },
                }}
            />
        </div>
    )
}

export default MathInputField
