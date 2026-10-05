from Automation_Analyst.errror_patterns import ERROR_PATTERNS


def analyze_error(error_message):
    error_message = error_message.lower()

    for pattern in ERROR_PATTERNS:
        for keyword in pattern["keywords"]:
            if keyword in error_message:
                return {
                    "type": pattern["name"],
                    "root_cause": pattern["root_cause"],
                    "category": pattern["category"],
                    "severity": pattern["severity"],
                    "solution": pattern["solution"]
                }

    return {
        "type": "Unknown Error",
        "root_cause": "Belum teridentifikasi",
        "category": "Unknown",
        "severity": "Low",
        "solution": "Periksa log manual"
    }
