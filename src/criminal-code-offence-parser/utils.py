"""
Utilities file for handling statutory rule files.
"""


# Move these to a utils
def parse_quantum(quantum):
    """
    Parse the quantum of the offence.
    """
    parsed_quantum = {}

    if quantum == "":
        parsed_quantum["amount"] = 0
        parsed_quantum["unit"] = "days"
        return parsed_quantum

    #
    # Update to reflect the maximum fine amount
    if quantum == "sc":
        quantum = "729d"

    unit_mappings = {"y": "years", "m": "months", "d": "days", "$": "dollars"}
    unit = unit_mappings.get(quantum[-1], quantum[-1])

    # Assign all but the last character of the quantum string to the value variable
    value = quantum[:-1]
    parsed_quantum["amount"] = value
    parsed_quantum["unit"] = unit

    return parsed_quantum


def convert_quantum_to_days(quantum):
    """
    Convert the quantum of the offence to days.
    """
    try:
        quantum_int = int(quantum["amount"])
    except:
        quantum_int = 0

    if quantum["unit"] == "years":
        quantum["amount"] = quantum_int * 365
        quantum["unit"] = "days"
        return quantum

    elif quantum["unit"] == "months":
        quantum["amount"] = quantum_int * 30
        quantum["unit"] = "days"
        return quantum
    elif quantum["unit"] == "days":
        return quantum
    else:
        return None

def standard_output(result, result_notes, sections, explanation):
    """
    Function to standardize the output for the check results.
    """
    output_dictionary = {
        "status": {
            "available": result,
            "notes": result_notes,
        },
        "sections": sections,
        "notes": explanation
    }

    return output_dictionary
