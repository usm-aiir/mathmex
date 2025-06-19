"use client"
// @ts-ignore
import styles from "./InputField.module.css"
import { FC, MutableRefObject, useEffect, useRef, KeyboardEvent, useState } from "react"
import { EditableMathField } from "react-mathquill"
import type { MathField } from "react-mathquill"
import ReactDOM from "react-dom/client"

interface InputFieldProps {
    latex: string
    setLatex: (latex: string) => void
    mathFieldRef: MutableRefObject<MathField | null>
    onEnter?: () => void
}

interface MathFieldData {
    id: string
    latex: string
    element: HTMLSpanElement
}

// Extend HTMLSpanElement to include the mathField property
declare global {
    interface HTMLSpanElement {
        __mathField?: MathField
    }
}

const InputField: FC<InputFieldProps> = ({ setLatex, mathFieldRef, onEnter }) => {
    const contentRef = useRef<HTMLDivElement>(null)
    const [mathFields, setMathFields] = useState<MathFieldData[]>([])
    const [activeMathFieldId, setActiveMathFieldId] = useState<string | null>(null)

    const computeLatexFromDOM = () => {
        if (!contentRef.current) return ""
        
        let latex = ""
        const walker = document.createTreeWalker(
            contentRef.current,
            NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
            null
        )

        let node: Node | null = walker.nextNode()
        while (node) {
            if (node.nodeType === Node.TEXT_NODE) {
                latex += node.textContent
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                const element = node as HTMLElement
                if (element.hasAttribute('data-math-field-id')) {
                    const mathField = mathFields.find((f: MathFieldData) => f.id === element.getAttribute('data-math-field-id'))
                    if (mathField) {
                        latex += mathField.latex
                    }
                }
            }
            node = walker.nextNode()
        }

        return latex
    }

    const insertMathField = () => {
        const selection = window.getSelection()
        if (!selection || !contentRef.current) return

        // Ensure selection is inside the contenteditable search bar
        let node: Node | null = selection.anchorNode
        let isInside = false
        while (node) {
            if (node === contentRef.current) {
                isInside = true
                break
            }
            node = node.parentNode
        }
        if (!isInside) return

        const range = selection.getRangeAt(0)
        const newId = `math-${Date.now()}`
        
        // Create container for math field
        const mathContainer = document.createElement('span')
        mathContainer.setAttribute('data-math-field-id', newId)
        mathContainer.className = styles.mathFieldWrapper
        
        // Insert the container at cursor position
        range.insertNode(mathContainer)
        range.selectNodeContents(mathContainer)
        selection.removeAllRanges()
        selection.addRange(range)

        // Add to math fields state
        const newMathField: MathFieldData = {
            id: newId,
            latex: "",
            element: mathContainer
        }
        
        setMathFields((prev: MathFieldData[]) => [...prev, newMathField])
        setActiveMathFieldId(newId)

        // Render MathQuill field
        const mathFieldElement = document.createElement('div')
        mathContainer.appendChild(mathFieldElement)
        
        // Use ReactDOM.render to render the MathQuill field
        const mathField = (
            <EditableMathField
                latex=""
                onChange={(mathField) => {
                    if (mathField) {
                        handleMathFieldChange(newId, mathField.latex())
                    }
                }}
                mathquillDidMount={(mathField) => {
                    // Store mathField reference on the DOM element
                    mathContainer.__mathField = mathField
                    // Do NOT focus the math field here
                    // Immediately blur the math field after mount
                    setTimeout(() => {
                        if (mathField && typeof mathField.blur === 'function') {
                            mathField.blur()
                        }
                        // Insert a zero-width space after the math field
                        const zwsp = document.createTextNode('\u200b')
                        if (mathContainer.parentNode) {
                            mathContainer.parentNode.insertBefore(zwsp, mathContainer.nextSibling)
                        }
                        // Move caret to the start of the zwsp node
                        const range = document.createRange()
                        range.setStart(zwsp, 0)
                        range.setEnd(zwsp, 0)
                        const sel = window.getSelection()
                        if (sel) {
                            sel.removeAllRanges()
                            sel.addRange(range)
                        }
                        // Optionally, focus the contenteditable container
                        contentRef.current?.focus()
                    }, 0)
                    // Update the mathFieldRef
                    mathFieldRef.current = mathField
                }}
                config={{
                    spaceBehavesLikeTab: true,
                    handlers: {
                        enter: () => {
                            handleMathFieldExit(newId)
                            return false
                        },
                        deleteOutOf: (direction) => {
                            if (direction === -1) { // Backspace
                                handleMathFieldExit(newId)
                            } else if (direction === 1) { // Delete
                                mathContainer.remove()
                                setMathFields((prev: MathFieldData[]) => prev.filter((f: MathFieldData) => f.id !== newId))
                            }
                            return false
                        }
                    }
                }}
            />
        )
        
        // Use ReactDOM.render to render the MathQuill field
        const root = ReactDOM.createRoot(mathFieldElement)
        root.render(mathField)
    }

    const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
        // If we're in a math field, let it handle its own keyboard events
        if (activeMathFieldId) {
            return
        }

        // Enter: submit query (onEnter) only if not Ctrl/Cmd
        if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey && !e.metaKey) {
            e.preventDefault()
            onEnter?.()
        }
        // Cmd/Ctrl+Enter: insert a new paragraph/line break
        else if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
            e.preventDefault()
            // Insert a new paragraph at the caret position
            document.execCommand('insertParagraph')
        }

        // Handle Ctrl/Cmd + M for inserting math field
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'm') {
            e.preventDefault()
            insertMathField()
        }

        // Handle backspace and delete for math fields
        if ((e.key === "Backspace" || e.key === "Delete") && contentRef.current) {
            const selection = window.getSelection()
            if (!selection) return

            const range = selection.getRangeAt(0)
            const node = range.startContainer

            // Find if we're at a math field boundary
            const mathField = mathFields.find((field: MathFieldData) => {
                const element = field.element
                return (
                    (e.key === "Backspace" && node === element.previousSibling) ||
                    (e.key === "Delete" && node === element.nextSibling)
                )
            })

            if (mathField) {
                e.preventDefault()
                mathField.element.remove()
                setMathFields((prev: MathFieldData[]) => prev.filter((f: MathFieldData) => f.id !== mathField.id))
            }
        }
    }

    const handleMathFieldChange = (id: string, newLatex: string) => {
        setMathFields((fields: MathFieldData[]) => 
            fields.map((field: MathFieldData) => 
                field.id === id ? { ...field, latex: newLatex } : field
            )
        )
    }

    const handleMathFieldExit = (id: string) => {
        setActiveMathFieldId(null)
        mathFieldRef.current = null
        const mathField = mathFields.find((field: MathFieldData) => field.id === id)
        if (mathField && contentRef.current) {
            // Move cursor after the math field
            const range = document.createRange()
            range.setStartAfter(mathField.element)
            range.collapse(true)
            
            const selection = window.getSelection()
            if (selection) {
                selection.removeAllRanges()
                selection.addRange(range)
            }
        }
    }

    // Handle clicks on math fields
    useEffect(() => {
        const handleClick = (e: MouseEvent) => {
            const target = e.target as HTMLElement
            const mathFieldElement = target.closest('[data-math-field-id]')
            if (mathFieldElement) {
                const id = mathFieldElement.getAttribute('data-math-field-id')
                if (id) {
                    setActiveMathFieldId(id)
                    const mathField = (mathFieldElement as HTMLSpanElement).__mathField
                    if (mathField) {
                        mathField.focus()
                        mathFieldRef.current = mathField
                    }
                }
            }
        }

        contentRef.current?.addEventListener('click', handleClick)
        return () => {
            contentRef.current?.removeEventListener('click', handleClick)
        }
    }, [])

    // Update latex whenever content changes
    useEffect(() => {
        const latex = computeLatexFromDOM()
        setLatex(latex)
    }, [mathFields, contentRef.current?.innerHTML])

    return (
        <div className={styles.inputContainer}>
            <div className={styles.inputWrapper}>
                <div 
                    ref={contentRef}
                    contentEditable={true}
                    onKeyDown={handleKeyDown}
                    className={styles.contentEditable}
                    data-placeholder="Type your query here..."
                />
                <button 
                    className={styles.mathButton}
                    onClick={insertMathField}
                    title="Insert Equation (CTRL+M)"
                >
                    ∑
                </button>
            </div>
        </div>
    )
}

export default InputField 