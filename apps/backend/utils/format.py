import re
from latex2mathml.converter import convert as latex2mathml
import xml.etree.ElementTree as ET

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

def format_for_tangent_cft_search(latex_str: str) -> str:
    """
    Converts a LaTeX string to TangentCFT-compatible MathML format.

    Example output for "a^2+b^2=c^2":
    "<math xmlns=\"http://www.w3.org/1998/Math/MathML\" alttext=\"a^2+b^2=c^2\" 
      class=\"ltx_Math\" display=\"block\"><semantics>...</semantics></math>"
    """
    # Convert LaTeX to Presentation MathML
    pmml_full = latex2mathml(latex_str)

    # Parse the PMML string and extract the correct structure
    try:
        root = ET.fromstring(pmml_full)  # Parse the MathML string
        semantics = root.find(".//{http://www.w3.org/1998/Math/MathML}semantics")  # Find the <semantics> tag
        if semantics is not None:
            # Extract the <mrow> content inside <semantics>
            mrow = semantics.find("{http://www.w3.org/1998/Math/MathML}mrow")
            if mrow is not None:
                pmml_body = ET.tostring(mrow, encoding="unicode")  # Convert <mrow> to string
            else:
                pmml_body = ET.tostring(semantics, encoding="unicode")  # Fallback to <semantics> content
        else:
            pmml_body = pmml_full  # Fallback to the full PMML if <semantics> is missing
    except ET.ParseError as e:
        print(f"Error parsing PMML: {e}")
        pmml_body = pmml_full  # Fallback to the full PMML if parsing fails

    # Wrap it in the TangentCFT <math> format
    tangentcft_mathml = (
        f'<math xmlns="http://www.w3.org/1998/Math/MathML" '
        f'alttext="{latex_str}" class="ltx_Math" display="block">'
        f'<semantics>{pmml_body}</semantics></math>'
    )

    return tangentcft_mathml

