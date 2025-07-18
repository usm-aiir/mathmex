import React, { useState } from "react";

const QUESTIONS = [
    // First 5 (product questions)
    "How easy was it to use MathMex?",
    "How helpful were the search results?",
    "How visually appealing is the interface?",
    "How likely are you to recommend MathMex?",
    "How satisfied are you overall?",
    // Next 10 (other questions)
    "How clear were the explanations?",
    "How fast was the website?",
    "How easy was it to find what you needed?",
    "How accurate were the results?",
    "How helpful was the math input?",
    "How helpful was the history feature?",
    "How helpful were the filters?",
    "How likely are you to use MathMex again?",
    "How likely are you to use MathMex for homework?",
    "How likely are you to use MathMex for research?"
];

export default function SurveyPage() {
    const [responses, setResponses] = useState<number[]>(Array(QUESTIONS.length).fill(0));
    const [submitted, setSubmitted] = useState(false);

    const handleChange = (idx: number, value: number) => {
        const updated = [...responses];
        updated[idx] = value;
        setResponses(updated);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitted(true);

        // Calculate product and sum
        const productScore = responses.slice(0, 5).reduce((a, b) => a + b, 0);
        const otherScore = responses.slice(5).reduce((a, b) => a + b, 0);

        // Send to backend
        fetch("/api/survey", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                productScore,
                otherScore
            })
        }).then(() => {
            // Optionally handle response
        });

        console.log("Submitted scores:", { productScore, otherScore });
    };

    return (
        <div style={{ maxWidth: 600, margin: "2rem auto", background: "#fffbe6", borderRadius: 8, boxShadow: "0 2px 8px #c19a49", padding: "2rem" }}>
            <h2>MathMex User Survey</h2>
            {!submitted ? (
                <form onSubmit={handleSubmit}>
                    {QUESTIONS.map((q, idx) => (
                        <div key={idx} style={{ marginBottom: "1.5rem" }}>
                            <label style={{ fontWeight: 600, marginBottom: 8, display: "block" }}>{q}</label>
                            <div style={{ display: "flex", gap: "1rem", marginTop: 8 }}>
                                {[1, 2, 3, 4, 5].map((num) => (
                                    <label key={num} style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                                        <input
                                            type="radio"
                                            name={`q${idx}`}
                                            value={num}
                                            checked={responses[idx] === num}
                                            onChange={() => handleChange(idx, num)}
                                            required
                                        />
                                        {num}
                                    </label>
                                ))}
                            </div>
                        </div>
                    ))}
                    <button
                        type="submit"
                        style={{
                            marginTop: "2rem",
                            background: "#c19a49",
                            color: "#fffbe6",
                            border: "none",
                            borderRadius: 8,
                            padding: "0.75rem 2rem",
                            fontSize: "1.1rem",
                            fontWeight: 600,
                            cursor: "pointer"
                        }}
                        disabled={submitted}
                    >
                        Submit
                    </button>
                </form>
            ) : (
                <div style={{ marginTop: "2rem", textAlign: "center", color: "#c19a49" }}>
                    <h3>Thank you for your feedback!</h3>
                </div>
            )}
        </div>
    );
}