def evaluate_alert(data: dict):
    
    risk_score = data.get("risk_score", 0)

    if risk_score >= 80:
        return {
            "severity": "critical",
            "message": "Infrastructure at critical risk level"
        }

    if risk_score >= 60:
        return {
            "severity": "warning",
            "message": "Infrastructure risk increasing"
        }

    return None