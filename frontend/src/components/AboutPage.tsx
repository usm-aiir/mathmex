/**
 * AboutPage.tsx
 *
 * Displays information about the MathMex project, its mission, features, and links to the research group and GitHub repository.
 * This is a static informational page.
 */
import styles from "./AboutPage.module.css";

const AboutPage = () => (
    <div className="container">
        <div className={styles.aboutPage}>
            <h1>About MathMex</h1>
            <p>
                <strong>MathMex</strong> is an innovative platform designed to make mathematical knowledge more accessible than ever before.<br /><br />
                Whether you’re a student, educator, or researcher, MathMex empowers you to search for mathematical theorems, formulas, and concepts using natural language.<br /><br />
                Our mission is to break down barriers to mathematical discovery by combining the power of artificial intelligence and advanced information retrieval techniques. With MathMex, you can quickly find precise mathematical results, explore related concepts, and deepen your understanding of mathematics—all in one place.<br /><br />
                <strong>Key Features:</strong><br />
                • Search for theorems and formulas using plain English or LaTeX<br />
                • Instantly access a curated database of mathematical knowledge<br />
                • User-friendly interface designed for all levels of expertise<br />
                • Powered by cutting-edge AI and information retrieval research<br /><br />
                MathMex is brought to you by the dedicated team at the Artificial Intelligence and Information Retrieval Lab (AIIR) at the University of Southern Maine. Our goal is to support learners and professionals worldwide in their mathematical journeys.
            </p>
            <p>
                Learn more about our research group:&nbsp;
                <a
                    href="https://cs.usm.maine.edu/~behrooz.mansouri/AIIRLab/index.html"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    AIIR Lab at USM
                </a>
            </p>
            <p>
                View the project on GitHub:&nbsp;
                <a
                    href="https://github.com/AIIRLab-USM/MathMex"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    github.com/AIIRLab-USM/MathMex
                </a>
            </p>
        </div>
    </div>
);

export default AboutPage;