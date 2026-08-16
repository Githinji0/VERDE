from typing import Any, Dict, List, Tuple
from backend.app.brain.payloads import VALID_UNIVERSES, VALID_REGIONS, VALID_NEUTRALIZATIONS


def validate_brain_configuration(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates a simulation configuration dictionary against allowed BRAIN parameters.
    Returns (is_valid, list_of_issues).
    """
    issues = []
    if "universe" in config and config["universe"].upper() not in VALID_UNIVERSES:
        issues.append(f"Universe '{config['universe']}' is not recognized.")
    if "region" in config and config["region"].upper() not in VALID_REGIONS:
        issues.append(f"Region '{config['region']}' is not recognized.")
    if "neutralization" in config and config["neutralization"].upper() not in VALID_NEUTRALIZATIONS:
        issues.append(f"Neutralization '{config['neutralization']}' is not recognized.")
    if "decay" in config and not (0 <= int(config["decay"]) <= 100):
        issues.append("Decay must be an integer between 0 and 100.")
    if "truncation" in config and not (0.01 <= float(config["truncation"]) <= 1.0):
        issues.append("Truncation must be a float between 0.01 and 1.0.")

    return len(issues) == 0, issues
