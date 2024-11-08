"""
Utilities file for handling statutory rule files.
"""


# Move these to a utils
def parse_quantum(quantum):
    """
    Parse the quantum of the offence.
    """
    parsed_quantum = {
        "fine": {
            "amount": 0,
            "unit": "dollars"
        },
        "jail": {
            "amount": 0,
            "unit": "days"
        }
    }

    if quantum == "":
        return parsed_quantum

    #
    # Update to reflect the maximum fine amount
    if quantum == "sc":
        parsed_quantum["fine"]["amount"] = 5000
        parsed_quantum["fine"]["unit"] = "dollars"
        parsed_quantum["jail"]["amount"] = 729
        parsed_quantum["jail"]["unit"] = "days"
        return parsed_quantum

    # Assign all but the last character of the quantum string to the value variable
    unit_mappings = {"y": "years", "m": "months", "d": "days", "$": "dollars"}
    unit = unit_mappings.get(quantum[-1], quantum[-1])

    if "&" in quantum:
        quantums = quantum.split("&")
        parsed_quantum["fine"]["amount"] = quantums[0]
        parsed_quantum["fine"]["unit"] = "dollars"
        parsed_quantum["jail"]["amount"] = quantums[1]
        parsed_quantum["jail"]["unit"] = "days"
        return parsed_quantum
    
    if unit == "dollars":
        value = quantum[:-1]
        parsed_quantum["fine"]["amount"] = value
        parsed_quantum["fine"]["unit"] = unit
        parsed_quantum["jail"]["amount"] = 0
        parsed_quantum["jail"]["unit"] = "days"
    else:
        value = quantum[:-1]
        parsed_quantum["jail"]["amount"] = value
        parsed_quantum["jail"]["unit"] = unit
        parsed_quantum["fine"]["amount"] = 0
        parsed_quantum["fine"]["unit"] = "dollars"

    return parsed_quantum


def convert_quantum_to_days(quantum):
    """
    Convert the quantum of the offence to days.
    """
    try:
        quantum_int = int(quantum["amount"])
    except:
        quantum_int = 0

    if quantum["jail"]["unit"] == "years":
        quantum["jail"]["amount"] = quantum_int * 365
        quantum["jail"]["unit"] = "days"
        return quantum

    elif quantum["jail"]["unit"] == "months":
        quantum["jail"]["amount"] = quantum_int * 30
        quantum["jail"]["unit"] = "days"
        return quantum
    elif quantum["jail"]["unit"] == "days":
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
