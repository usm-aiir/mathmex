export const keyboardLayout = [
    {
        title: "Constants",
        keys: [
            { display: "α", latex: "\\alpha" },
            { display: "β", latex: "\\beta" },
            { display: "γ", latex: "\\gamma" },
            { display: "δ", latex: "\\delta" },
            { display: "ε", latex: "\\epsilon" },
            { display: "ζ", latex: "\\zeta" },
            { display: "η", latex: "\\eta" },
            { display: "θ", latex: "\\theta" },
            { display: "λ", latex: "\\lambda" },
            { display: "μ", latex: "\\mu" },
            { display: "π", latex: "\\pi" },
            { display: "σ", latex: "\\sigma" },
            { display: "φ", latex: "\\phi" },
            { display: "ω", latex: "\\omega" },
        ],
    },
    {
        title: "Operators",
        keys: [
            { display: "+", latex: "+" },
            { display: "−", latex: "-" },
            { display: "×", latex: "\\times" },
            { display: "÷", latex: "\\div" },
            { display: "＝", latex: "=" },
            { display: "≠", latex: "\\neq" },
            { display: "≈", latex: "\\approx" },
            { display: "<", latex: "<" },
            { display: ">", latex: ">" },
            { display: "≤", latex: "\\leq" },
            { display: "≥", latex: "\\geq" },
            { display: "±", latex: "\\pm" },
        ],
    },
    {
        title: "Symbols",
        keys: [
            { display: "∞", latex: "\\infty" },
            { display: "∂", latex: "\\partial" },
            { display: "∇", latex: "\\nabla" },
            { display: "∈", latex: "\\in" },
            { display: "∉", latex: "\\notin" },
            { display: "⊂", latex: "\\subset" },
            { display: "⊃", latex: "\\supset" },
            { display: "∪", latex: "\\cup" },
            { display: "∩", latex: "\\cap" },
            { display: "∀", latex: "\\forall" },
            { display: "∃", latex: "\\exists" },
            { display: "∄", latex: "\\nexists" },
        ],
    },
    {
        title: "Functions",
        keys: [
            { display: "√x", latex: "\\sqrt{}" },
            { display: "x²", latex: "^{2}" },
            { display: "xⁿ", latex: "^{}" },
            { display: "x/y", latex: "\\frac{}{}" },
            { display: "∑", latex: "\\sum_{}^{}" },
            { display: "∏", latex: "\\prod_{}^{}" },
            { display: "∫", latex: "\\int_{}^{}" },
            { display: "lim", latex: "\\lim_{ \\to }" },
        ],
    },
    {
        title: "Brackets",
        keys: [
            { display: "( )", latex: "()" },
            { display: "[ ]", latex: "[]" },
            { display: "{ }", latex: "\\{\\}" },
            { display: "⟨ ⟩", latex: "\\langle \\rangle" },
            { display: "|x|", latex: "\\left|  \\right|" },
            { display: "⌊x⌋", latex: "\\lfloor  \\rfloor" },
            { display: "⌈x⌉", latex: "\\lceil  \\rceil" },
        ],
    },
]

export interface SearchResult {
    title: string
    formula: string
    description: string
    tags: string[]
    year: string
}

export function mockSearch(query: string): SearchResult[] {
    let results: SearchResult[] = []
    const lowerQuery = query.toLowerCase()

    if (lowerQuery.includes("\\oint") || lowerQuery.includes("stokes")) {
        results.push({
            title: "Stokes' Theorem",
            formula: "\\oint_C \\vec{F} \\cdot d\\vec{r} = \\iint_S (\\nabla \\times \\vec{F}) \\cdot d\\vec{S}",
            description:
                "Stokes' theorem relates a surface integral of the curl of a vector field to a line integral of the vector field around the boundary of the surface.",
            tags: ["Vector Calculus", "Integration", "Differential Geometry"],
            year: "1850",
        })
    }
    if (lowerQuery.includes("e^{i") || lowerQuery.includes("euler")) {
        results.push({
            title: "Euler's Identity",
            formula: "e^{i\\pi} + 1 = 0",
            description:
                "Euler's identity is considered by many to be the most beautiful equation in mathematics, linking five fundamental mathematical constants.",
            tags: ["Complex Analysis", "Number Theory", "Fundamental Constants"],
            year: "1748",
        })
    }
    if (lowerQuery.includes("\\nabla") || lowerQuery.includes("divergence")) {
        results.push({
            title: "Divergence Theorem",
            formula: "\\iiint_V (\\nabla \\cdot \\vec{F}) dV = \\oiint_S \\vec{F} \\cdot \\hat{n} dS",
            description:
                "The divergence theorem relates the flux of a vector field through a closed surface to the divergence of the field within the volume enclosed.",
            tags: ["Vector Calculus", "Integration", "Fluid Dynamics"],
            year: "1762",
        })
    }
    if (lowerQuery.includes("\\sum") || lowerQuery.includes("series")) {
        results.push({
            title: "Geometric Series",
            formula: "\\sum_{n=0}^{\\infty} ar^n = \\frac{a}{1-r} \\quad \\text{for } |r| < 1",
            description: "The sum of an infinite geometric series with first term a and common ratio r (where |r| < 1).",
            tags: ["Series", "Calculus", "Convergence"],
            year: "Ancient",
        })
    }
    if (lowerQuery.includes("\\int") || lowerQuery.includes("fundamental")) {
        results.push({
            title: "Fundamental Theorem of Calculus",
            formula: "\\int_a^b f'(x) dx = f(b) - f(a)",
            description:
                "The fundamental theorem of calculus establishes the relationship between differentiation and integration.",
            tags: ["Calculus", "Integration", "Differentiation"],
            year: "1668",
        })
    }

    if (results.length === 0) {
        results = [
            {
                title: "Pythagorean Theorem",
                formula: "a^2 + b^2 = c^2",
                description:
                    "In a right triangle, the square of the length of the hypotenuse equals the sum of squares of the other two sides.",
                tags: ["Geometry", "Triangles", "Euclidean Geometry"],
                year: "~570 BCE",
            },
            {
                title: "Quadratic Formula",
                formula: "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
                description: "The solution to the quadratic equation ax² + bx + c = 0, where a ≠ 0.",
                tags: ["Algebra", "Equations", "Polynomials"],
                year: "~2000 BCE",
            },
        ]
    }

    return results
}
