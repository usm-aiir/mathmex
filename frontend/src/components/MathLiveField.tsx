import { useEffect, useRef, forwardRef, useImperativeHandle } from "react"

interface MathLiveFieldProps {
    value: string
    onChange: (latex: string) => void
    placeholder: string
}

export interface MathLiveFieldHandle {
    insertAtCursor: (latex: string) => void
    fieldRef: React.RefObject<any>
}

const MathLiveField = forwardRef<MathLiveFieldHandle, MathLiveFieldProps>(
    ({ value, onChange, placeholder }, ref) => {
        const fieldRef = useRef<any>(null)

        useImperativeHandle(ref, () => ({
            insertAtCursor: (text: string) => {
                if (fieldRef.current) {
                    fieldRef.current.insert(text)
                    fieldRef.current.focus()
                    // If inserting "$ $", move cursor left to be between the $ $
                    if (text === "$ $" || text === "$~$") {
                        fieldRef.current.executeCommand &&
                            fieldRef.current.executeCommand("moveToPreviousChar")
                    }
                }
            },
            switchMode: (mode: "math" | "text") => {
                if (fieldRef.current && fieldRef.current.executeCommand) {
                    fieldRef.current.executeCommand("switchMode", mode)
                }
            },
            fieldRef
        }))

        useEffect(() => {
            if (!fieldRef.current) return
            fieldRef.current.value = value
            const handler = (e: any) => onChange(e.target.value)
            fieldRef.current.addEventListener("input", handler)
            return () => {
                fieldRef.current?.removeEventListener("input", handler)
            }
        }, [onChange, value])

        return (
            <math-field
                ref={fieldRef}
                virtualkeyboardmode="manual"
                textmode="true"
                placeholder={placeholder}
            ></math-field>
        )
    }
)

export default MathLiveField
export interface MathLiveFieldHandle {
    insertAtCursor: (text: string) => void
    switchMode: (mode: "math" | "text") => void
    fieldRef: React.RefObject<any>
}

declare global {
    namespace JSX {
        interface IntrinsicElements {
            'math-field': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
                ref?: React.Ref<any>
                virtualkeyboardmode?: string
                textmode?: string
                placeholder?: string
            }
        }
    }
}