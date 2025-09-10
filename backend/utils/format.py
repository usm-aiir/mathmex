import re

def format_for_mathmex(latex):
    """
    Converts LaTeX like '\\text{abc} x^2 \\text{def} y' to
    'abc $x^2$ def $y$'.

    Args:
        latex (str): The LaTeX string to convert.
    Returns:
        str: The formatted string for storage.
    """
    # Pattern: \text{...}
    text_pattern = re.compile(r'\\text\{([^}]*)\}')
    parts = []
    last_end = 0

    # Find all \text{...} and split
    for m in text_pattern.finditer(latex):
        # Add math before this text, if any
        if m.start() > last_end:
            math_part = latex[last_end:m.start()].strip()
            if math_part:
                parts.append(f"$${math_part}$$")
        # Add the plain text
        parts.append(m.group(1))
        last_end = m.end()
    # Add any trailing math
    if last_end < len(latex):
        math_part = latex[last_end:].strip()
        if math_part:
            parts.append(f"${math_part}$")
    # Join with spaces, remove empty $...$
    return " ".join([p for p in parts if p and p != "$$"])

def format_for_mathlive(text: str) -> str:
    """
    Replaces single $...$ wrappers with $$...$$ for MathLive consistency,
    while leaving existing $$...$$ untouched.

    Args:
        text (str): The input string containing LaTeX math.
    Returns:
        str: The string with single $...$ replaced by $$...$$
    """
    # Use a regex to find single $...$ not already part of $$...$$
    # Matches a single $...$ with no extra $ next to it
    pattern = re.compile(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)')

    return pattern.sub(r'$\1$', text)
