import csv
from constants import (
    PRIMARY_DESIGNATED_DNA_OFFENCES,
    SECONDARY_DESIGNATED_DNA_OFFENCES,
    EXCLUDED_CSO_OFFENCES,
    TERRORISM_OFFENCES,
    CRIMINAL_ORGANIZATION_OFFENCES,
)

# Open the CSV file
with open("data/cc-offences-2024-09-16.csv") as csvfile:
    csvreader = csv.reader(csvfile)
    data = list(csvreader)


def check_offence_type(offence):
    """
    Check the type of offence for a given offence.
    """

    if offence[3] == "":
        return "summary"
    elif offence[5] == "":
        return "indictable"
    else:
        return "hybrid"


def check_prelim_available(offence):
    """
    Check if the preliminary inquiry is available for a given offence.
    """

    if offence[3] == "14y" or offence[3] == "999y":
        return True
    else:
        return False


def check_dna_designation(offence, mode, quantum):
    """
    Check if the offence is a designated DNA offence.
    """

    try:
        quantum_int = int(quantum["amount"])
    except:
        quantum_int = 0

    if offence[0] in PRIMARY_DESIGNATED_DNA_OFFENCES:
        return "primary"
    elif offence[0] in SECONDARY_DESIGNATED_DNA_OFFENCES:
        return "secondary"
    elif (
        (mode == "indictable" or mode == "hybrid")
        and quantum["unit"] == "years"
        and quantum_int >= 5
    ):
        return "secondary"
    else:
        return None


def parse_quantum(quantum):
    """
    Parse the quantum of the offence.
    """
    parsed_quantum = {}

    if quantum == "":
        parsed_quantum["amount"] = None
        parsed_quantum["unit"] = None
        return parsed_quantum

    if quantum == "sc":
        quantum = "729d"

    unit_mappings = {"y": "years", "m": "months", "d": "days", "$": "dollars"}
    unit = unit_mappings.get(quantum[-1], quantum[-1])

    # Assign all but the last character of the quantum string to the value variable
    value = quantum[:-1]
    parsed_quantum["amount"] = value
    parsed_quantum["unit"] = unit

    return parsed_quantum


def check_cso_availablity(
    section, summary_minimum, indictable_minimum, indictable_maximum, mode
):
    """
    Check if the charge screening officer is available for a given offence. An offence
    qualifies for a CSO if the following conditions obtain:

    - The offence does not have a mandatory minimum term of imprisonment
    - The offence is not an enumerated offence
    - The offence is not:
      - A terrorism or criminal organization offence; AND
      - Punishable by 10y or more term of imprisonment; AND
      - Prosecuted by indictment
    """

    try:
        indictable_maximum = int(indictable_maximum["amount"])
    except:
        indictable_maximum = 0
    cso_available = {
    }

    if summary_minimum["amount"] or indictable_minimum["amount"]:
        cso_available["section"] = "cc742.1(b)"
        cso_available["status"] = "unavailable"
        cso_available["reason"] = "mandatory minimum term of imprisonment"
        
        return cso_available

    elif section in EXCLUDED_CSO_OFFENCES:
        cso_available["section"] = "cc742.1(c)"
        cso_available["status"] = "unavailable"
        cso_available["reason"] = "enumerated excluded offence"
        
        return cso_available
    
    elif (
        section in TERRORISM_OFFENCES
        and indictable_maximum >= 10
        and mode == "indictable"
    ):
        cso_available["section"] = "cc742.1(d)"
        cso_available["status"] = "unavailable"
        cso_available["reason"] = "serious indictable terrorism offence"

        return cso_available
    
    elif (
        section in TERRORISM_OFFENCES and indictable_maximum >= 10 and mode == "hybrid"
    ):
        cso_available["section"] = "cc742.1(d)"
        cso_available["status"] = "available (summary conviction only)"
        cso_available["reason"] = "serious indictable terrorism offence"

        return cso_available
    elif (
        section in CRIMINAL_ORGANIZATION_OFFENCES
        and indictable_maximum >= 10
        and mode == "indictable"
    ):
        cso_available["section"] = "cc742.1(d)"
        cso_available["status"] = "unavailable"
        cso_available["reason"] = "serious indictable criminal organization offence"

        return cso_available
    elif (
        section in CRIMINAL_ORGANIZATION_OFFENCES
        and indictable_maximum >= 10
        and mode == "hybrid"
    ):
        cso_available["section"] = "cc742.1(d)"
        cso_available["status"] = "available (summary conviction only)"
        cso_available["reason"] = "serious indictable criminal organization offence"

        return cso_available
    else:
        cso_available["section"] = "cc742.1"
        cso_available["status"] = "available"
        cso_available["reason"] = None

        return cso_available


def check_inadmissibility(section, mode, indictable_maximum):
    """
    Checks to see whether the offence renders the defendant liable for IRPA
    consequences.
    """
    inadmissibilty_list = []

    try:
        indictable_maximum = int(indictable_maximum)
    except:
        indictable_maximum = 0

    if section in TERRORISM_OFFENCES:
        inadmissibilty_list.append({"section": "irpa34(1)", "status": "permanent resident", "reason": "security"})
    
    if section == "cc240.1":
        inadmissibilty_list.append({"section": "irpa35(1)(c.1)", "status": "permanent resident", "reason": "human or international rights violations"})
        inadmissibilty_list.append({"section": "irpa35(1)(c.1)", "status": "foreign national", "reason": "human or international rights violations"})

    if indictable_maximum >= 10:
        inadmissibilty_list.append({"section": "irpa36(1)", "status": "permanent resident", "reason": "serious criminality"})
        inadmissibilty_list.append({"section": "irpa36(1)", "status": "foreign national", "reason": "serious criminality"})

    if mode == "hybrid" or mode == "indictable":
        inadmissibilty_list.append({"section": "irpa36(2)", "status": "foreign national", "reason": "criminality"})

    return inadmissibilty_list

def check_mandatory_weapons_prohibition_recognizance(section):
    pass

def reverse_onus():
    pass

def parse_offence(offence, mode="summary"):
    """
    Parse the offence data for a given offence.
    """

    # Remove any whitespace from the offence input and convert to lowercase
    offence = offence.strip().lower()
    parsed_offence = {}

    # Find the offence in the data
    for row in data:
        if row[0] == offence:

            mode = check_offence_type(row)
            prelim_available = check_prelim_available(row)
            indictable_minimum_quantum = parse_quantum(row[2])
            indictable_maximum_quantum = parse_quantum(row[3])
            summary_minimum_quantum = parse_quantum(row[4])
            summary_maximum_quantum = parse_quantum(row[5])

            parsed_offence["section"] = row[0]
            parsed_offence["description"] = row[1]
            parsed_offence["mode"] = mode
            parsed_offence["summary_minimum"] = summary_minimum_quantum
            parsed_offence["summary_maximum"] = summary_maximum_quantum
            parsed_offence["indictable_minimum"] = indictable_minimum_quantum
            parsed_offence["indictable_maximum"] = indictable_maximum_quantum
            parsed_offence["prelim_available"] = prelim_available
            parsed_offence["cso_available"] = check_cso_availablity(
                row[0],
                summary_minimum_quantum,
                indictable_minimum_quantum,
                indictable_maximum_quantum,
                mode,
            )
            parsed_offence["dna_designation"] = check_dna_designation(
                row, mode, indictable_maximum_quantum
            )
            parsed_offence["inadmissibility"] = check_inadmissibility(
                row[0], mode, indictable_maximum_quantum["amount"]
            )

            return parsed_offence

    # Return None if the offence is not found
    return None
