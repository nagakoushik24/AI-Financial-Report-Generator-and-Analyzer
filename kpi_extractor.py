import re

def extract_kpis(text):
    kpis = {}
    patterns = {
        "Revenue": r"Revenue(?:\s*\(.*?\))?\s*[:\-]?\s*\$?([\d,]+\.?\d*)",
        "Net Income": r"Net Income\s*[:\-]?\s*\$?([\d,]+\.?\d*)",
        "Total Assets": r"Total Assets\s*[:\-]?\s*\$?([\d,]+\.?\d*)",
        "Total Liabilities": r"Total Liabilities\s*[:\-]?\s*\$?([\d,]+\.?\d*)"
    }
    for kpi, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            kpis[kpi] = match.group(1)
    return kpis
