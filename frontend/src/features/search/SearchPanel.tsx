import { useRef, useEffect, useState } from "react"
import { Mic, Send, Square, Filter, Type, FunctionSquare } from "lucide-react"
import styles from "./SearchPanel.module.css"

interface Props {
    // filters
    filtersActive: boolean
    activeFiltersCount: number
    onToggleFilter: () => void

    // math-field
    onSearch: () => void
    mathFieldRef: React.RefObject<any>
    initialLatex?: string
}

export default function SearchPanel({
    // filters
    filtersActive,
    activeFiltersCount,
    onToggleFilter,

    // math-field
    mathFieldRef,
    onSearch,
    initialLatex
}: Props) {
    const recognitionRef = useRef<SpeechRecognition | null>(null);

    // input mode hook
    const [mode, setMode] = useState<"math" | "text">("text")

    // speech-to-latex hooks
    const [isListening, setIsListening] = useState(false)
    const [transcript, setTranscript] = useState<string>("");

    // Make sure UI mode is sync'd with current math-field mode
    useEffect(() => {
        const el = mathFieldRef.current;
        if (!el) return;
        // Handler for mode-change event
        const modeChangeHandler = (evt: any) => setMode(evt.detail.mode);
        // Handler for input event (check mode on every input)
        const inputHandler = () => {
            if (el.mode && el.mode !== mode) {
                setMode(el.mode);
            }
        };
        el.addEventListener("mode-change", modeChangeHandler);
        el.addEventListener("input", inputHandler);
        // Set initial mode
        setMode(el.mode || "text");
        return () => {
            el.removeEventListener("mode-change", modeChangeHandler);
            el.removeEventListener("input", inputHandler);
        };
    }, [mathFieldRef, mode]);

    /* Speech recognition */
    const toggleSpeechRecognition = () => {
        if (isListening) {
            recognitionRef.current?.stop();
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.error("Speech recognition not supported in this browser.");
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = "en-US";
        recognitionRef.current = recognition;

        recognition.onresult = (event: SpeechRecognitionEvent) => {
            let interimTranscript = "";
            let finalTranscript = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcriptPart = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcriptPart;
                } else {
                    interimTranscript += transcriptPart;
                }
            }

            setTranscript(finalTranscript);
        };

        recognition.onend = () => {
            setIsListening(false);
            recognitionRef.current = null;
        };

        recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
            console.error("Speech recognition error:", event.error);
            setIsListening(false);
        };

        recognition.start();
        setIsListening(true);
    };

    /* Speech-to-LaTeX backend connection */
    const speechToLatex = (text: string) => {
        fetch(`/api/speech-to-latex`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.latex && mathFieldRef.current) {
                    mathFieldRef.current.insert(data.latex)
                }
            })
            .catch((err) => {
                console.error("Error converting speech to LaTeX", err);
            });
    };

    /* Constant effect */
    useEffect(() => {
        /* If there is a transcript present, translate it on backend */
        if (!isListening && transcript) {
            speechToLatex(transcript)
            /* Empty transcript */
            setTranscript("")
        }
    }, [isListening])

    return (
        <div className={styles.searchContainer}>
            {/* Remove mobile history sidebar button from here */}
            <div className={styles.inputContainer}>
                <math-field
                    ref={mathFieldRef}
                    placeholder="\mathrm{Search\ mathematics...}"
                    onKeyDown={(e: any) => {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            onSearch();
                        }
                    }}
                >{initialLatex}</math-field>
                <button
                    className={styles.searchButton}
                    onClick={onSearch}
                >
                    <Send size={22} />
                </button>
            </div>

            <div className={styles.searchControls}>
                <div className={styles.controlsRow}>

                    <div className={styles.modeSwitchGroup}>
                        <div className={styles.modeSliderRow}>
                            <span className={`${styles.modeSliderIcon} ${styles.text}`}> <Type size={16} /> </span>
                            <span className={`${styles.modeSliderIcon} ${styles.math}`}> <FunctionSquare size={22} /> </span>
                            <div className={styles.modeSliderTrack}></div>
                            <div
                                className={styles.modeSliderThumb}
                                style={{ left: mode === "math" ? "36px" : "0" }}
                            />
                            <button
                                type="button"
                                className={`${styles.modeSliderButton} ${styles.text}`}
                                onClick={() => {
                                    const el = mathFieldRef.current;
                                    if (el && el.executeCommand) {
                                        el.executeCommand("switchMode", "text");
                                        el.focus();
                                        setMode("text");
                                    }
                                }}
                                aria-pressed={mode === "text"}
                                aria-label="Text input mode"
                                tabIndex={0}
                            />
                            <button
                                type="button"
                                className={`${styles.modeSliderButton} ${styles.math}`}
                                onClick={() => {
                                    const el = mathFieldRef.current;
                                    if (el && el.executeCommand) {
                                        el.executeCommand("switchMode", "math");
                                        el.focus();
                                        setMode("math");
                                    }
                                }}
                                aria-pressed={mode === "math"}
                                aria-label="Math input mode"
                                tabIndex={0}
                            />
                        </div>
                    </div>

                    <div className={styles.actionButtons}>
                        <button
                            className={`${styles.controlButton} ${isListening ? styles.listening : ""}`}
                            aria-label={isListening ? "Stop voice input" : "Start voice input"}
                            onClick={toggleSpeechRecognition}
                        >
                            {isListening ? <Square size={18} strokeWidth={2.5} /> : <Mic size={20} />}
                        </button>
                        <button
                            className={`${styles.controlButton} ${filtersActive ? styles.active : ""}`}
                            aria-label="Search filters"
                            onClick={onToggleFilter}
                        >
                            <Filter size={20} />
                            {filtersActive && (
                                <span className={styles.filterBadge}>{activeFiltersCount}</span>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
