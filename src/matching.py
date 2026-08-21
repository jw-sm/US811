import re
from typing import Optional

from normalize import normalize

_DIRECTION_MAP = {"E": "EAST", "W": "WEST", "N": "NORTH", "S": "SOUTH"}
_REF_CODE_RE = re.compile(r"([NSEW])(\d+)")


def _is_ref_code_match(dig_name: str, normalized_step_identifier: str) -> bool:
    """Handles ref-style street codes like 'E0960' matching '960 EAST'."""
    match = _REF_CODE_RE.match(dig_name)
    if not match:
        return False

    dig_dir, dig_num = match.groups()
    number_matches = (
        dig_num.lstrip("0") in normalized_step_identifier
        or dig_num in normalized_step_identifier
    )
    if not number_matches:
        return False

    full_direction = _DIRECTION_MAP.get(dig_dir, dig_dir)
    return (
        full_direction in normalized_step_identifier
        or dig_dir in normalized_step_identifier
    )


def street_names_match(dig_name: str, step_identifier: str) -> bool:
    """
    True if a Directions-API step identifier refers to the same street as
    dig_name, using several fallback heuristics (exact / substring / ref-code).
    """
    normalized_step_identifier = normalize(step_identifier)

    return (
        normalized_step_identifier == dig_name
        or dig_name in normalized_step_identifier
        or normalized_step_identifier in dig_name
        or _is_ref_code_match(dig_name, normalized_step_identifier)
    )


def find_matching_step(steps: list[dict], dig_name: str) -> Optional[tuple[int, dict]]:
    """
    Scan a Directions-API leg's steps for the one matching dig_name.
    Returns (index, step) or None if no step matches.
    """
    for i, step in enumerate(steps):
        step_identifier = step.get("name", "") or step.get("ref", "")
        if street_names_match(dig_name, step_identifier):
            return i, step
    return None