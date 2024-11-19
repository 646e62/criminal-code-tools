"""
Utilities for handling statutory rule files and quantum calculations.

This module provides utility functions for parsing and converting quantum values
in the context of criminal code offences, as well as standardizing output formats.
"""

from typing import Dict, Union, List, Optional, TypedDict, Literal

# Type definitions
class QuantumDict(TypedDict):
    amount: Union[int, str, None]
    unit: str

class ParsedQuantum(TypedDict):
    fine: QuantumDict
    jail: QuantumDict

class StandardOutput(TypedDict):
    status: Dict[str, Union[bool, Optional[str]]]
    sections: List[str]
    notes: Optional[str]

# Constants
DAYS_PER_YEAR = 365
DAYS_PER_MONTH = 30
SUMMARY_CONVICTION_MAX_FINE = 5000
SUMMARY_CONVICTION_MAX_DAYS = 729

UNIT_MAPPINGS = {
    "y": "years",
    "m": "months",
    "d": "days",
    "$": "dollars"
}

DEFAULT_UNITS = {
    "fine": "dollars",
    "jail": "days"
}

def parse_quantum(quantum: str) -> ParsedQuantum:
    """
    Parse the quantum (amount and unit) of an offence.

    Args:
        quantum (str): The quantum string to parse. Can be:
            - Empty string: Returns default values
            - "sc": Returns summary conviction defaults
            - Format "amount[unit]": e.g., "5y" for 5 years
            - Format "fine&jail": e.g., "5000$&90d" for $5000 fine and 90 days

    Returns:
        ParsedQuantum: Dictionary containing parsed fine and jail amounts and units.
            Format:
            {
                "fine": {"amount": int|str, "unit": str},
                "jail": {"amount": int|str, "unit": str}
            }

    Examples:
        >>> parse_quantum("5y")
        {"fine": {"amount": 0, "unit": "dollars"}, "jail": {"amount": "5", "unit": "years"}}
        >>> parse_quantum("5000$&90d")
        {"fine": {"amount": "5000", "unit": "dollars"}, "jail": {"amount": "90", "unit": "days"}}
    """
    parsed_quantum: ParsedQuantum = {
        "fine": {"amount": 0, "unit": DEFAULT_UNITS["fine"]},
        "jail": {"amount": 0, "unit": DEFAULT_UNITS["jail"]}
    }

    if not quantum:
        return parsed_quantum

    # Handle summary conviction case
    if quantum.lower() == "sc":
        parsed_quantum["fine"]["amount"] = SUMMARY_CONVICTION_MAX_FINE
        parsed_quantum["jail"]["amount"] = SUMMARY_CONVICTION_MAX_DAYS
        return parsed_quantum

    # Handle combined fine and jail case
    if "&" in quantum:
        try:
            fine_part, jail_part = quantum.split("&")
            parsed_quantum["fine"]["amount"] = fine_part.rstrip("$")
            parsed_quantum["jail"]["amount"] = jail_part[:-1]
            parsed_quantum["jail"]["unit"] = UNIT_MAPPINGS.get(jail_part[-1], jail_part[-1])
            return parsed_quantum
        except ValueError:
            raise ValueError(f"Invalid combined quantum format: {quantum}. Expected format: 'fine&jail'")

    # Handle single quantum case
    try:
        unit = UNIT_MAPPINGS.get(quantum[-1], quantum[-1])
        value = quantum[:-1]

        if unit == "dollars":
            parsed_quantum["fine"]["amount"] = value
        else:
            parsed_quantum["jail"]["amount"] = value
            parsed_quantum["jail"]["unit"] = unit

        return parsed_quantum
    except IndexError:
        raise ValueError(f"Invalid quantum format: {quantum}")


def convert_quantum_to_days(quantum: ParsedQuantum) -> Optional[ParsedQuantum]:
    """
    Convert a time-based quantum to days.

    Args:
        quantum (ParsedQuantum): The quantum dictionary to convert, containing jail time information.

    Returns:
        Optional[ParsedQuantum]: The converted quantum with jail time in days, or None if conversion fails.

    Examples:
        >>> convert_quantum_to_days({"jail": {"amount": 1, "unit": "years"}, "fine": {"amount": 0, "unit": "dollars"}})
        {"jail": {"amount": 365, "unit": "days"}, "fine": {"amount": 0, "unit": "dollars"}}
    """
    try:
        amount = quantum["jail"]["amount"]
        amount_int = int(amount) if amount is not None else 0
        unit = quantum["jail"]["unit"]

        if unit == "years":
            quantum["jail"]["amount"] = amount_int * DAYS_PER_YEAR
            quantum["jail"]["unit"] = "days"
        elif unit == "months":
            quantum["jail"]["amount"] = amount_int * DAYS_PER_MONTH
            quantum["jail"]["unit"] = "days"
        elif unit != "days":
            return None

        return quantum
    except (ValueError, KeyError, TypeError) as e:
        raise ValueError(f"Error converting quantum to days: {str(e)}")


def standard_output(
    result: bool,
    result_notes: Optional[str],
    sections: List[str],
    explanation: Optional[str]
) -> StandardOutput:
    """
    Standardize the output format for check results.

    Args:
        result (bool): Whether the check was successful
        result_notes (Optional[str]): Additional notes about the result
        sections (List[str]): List of relevant sections
        explanation (Optional[str]): Detailed explanation of the result

    Returns:
        StandardOutput: Dictionary containing standardized output format
            Format:
            {
                "status": {"available": bool, "notes": str|None},
                "sections": List[str],
                "notes": str|None
            }
    """
    return {
        "status": {
            "available": result,
            "notes": result_notes,
        },
        "sections": sections,
        "notes": explanation
    }
