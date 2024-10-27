from constants import (
    PRIMARY_DESIGNATED_DNA_OFFENCES,
    SECONDARY_DESIGNATED_DNA_OFFENCES,
    EXCLUDED_CSO_OFFENCES,
    TERRORISM_OFFENCES,
    CRIMINAL_ORGANIZATION_OFFENCES,
    SECTION_469_OFFENCES,
)

# Basic metadata
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


def parse_quantum(quantum):
    """
    Parse the quantum of the offence.
    """
    parsed_quantum = {}

    if quantum == "":
        parsed_quantum["amount"] = None
        parsed_quantum["unit"] = None
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


# Procedure
def check_prelim_available(offence):
    """
    Check if the preliminary inquiry is available for a given offence.
    """

    if offence[3] == "14y" or offence[3] == "255y":
        return True
    else:
        return False


def reverse_onus():
    pass


def check_section_469_offence(section):
    """
    
    """

    if section in SECTION_469_OFFENCES:
        return True
    else:
        return False


# Sentencing options
def check_discharge_available(summary_minimum, indictable_minimum, indictable_maximum):
    """
    Discharges are available when the following conditions obtain:
    - The offence does not have a mandatory minimum of any kind
    - The offence is not punishable by 14y or greater
    """

    discharge_available = {}

    if summary_minimum["amount"] or indictable_minimum["amount"]:
        discharge_available["status"] = "unavailable"
        discharge_available["section"] = "cc730(1)"
        discharge_available["reason"] = "mandatory minimum sentence"

        return discharge_available

    elif indictable_maximum["amount"] >= 14:
        discharge_available["status"] = "unavailable"
        discharge_available["section"] = "cc730(1)"
        discharge_available["reason"] = "maximum term of 14y or greater"

        return discharge_available
    
    else:
        discharge_available["status"] = "available"
        discharge_available["section"] = "cc730(1)"
        discharge_available["reason"] = None

        return discharge_available


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

    # Convert None values to a comparable integer
    try:
        indictable_maximum["amount"] = int(indictable_maximum["amount"])
    except:
        indictable_maximum["amount"] = 0

    cso_available = {}

    if summary_minimum["amount"]:

        if summary_minimum["unit"] == "days" or summary_minimum["unit"] == "months" or summary_minimum["unit"] == "years":  
            cso_available["status"] = "unavailable"
            cso_available["section"] = "cc742.1(b)"
            cso_available["reason"] = "mandatory minimum term of imprisonment"

            return cso_available
        
        else:
            cso_available["status"] = "available"
            cso_available["section"] = "cc742.1"
            cso_available["reason"] = None

            return cso_available


    elif indictable_minimum["amount"]:

        if indictable_minimum["unit"] == "days" or indictable_minimum["unit"] == "months" or indictable_minimum["unit"] == "years":
            cso_available["status"] = "unavailable"
            cso_available["section"] = "cc742.1(b)"
            cso_available["reason"] = "mandatory minimum term of imprisonment"

            return cso_available
        
        else:
            cso_available["status"] = "available"
            cso_available["section"] = "cc742.1"
            cso_available["reason"] = None

    elif section in EXCLUDED_CSO_OFFENCES:
        cso_available["status"] = "unavailable"
        cso_available["section"] = "cc742.1(c)"
        cso_available["reason"] = "enumerated excluded offence"

        return cso_available

    elif (
        section in TERRORISM_OFFENCES
        and indictable_maximum >= 10
        and mode == "indictable"
    ):
        cso_available["status"] = "unavailable"
        cso_available["section"] = "cc742.1(d)"
        cso_available["reason"] = "serious indictable terrorism offence"

        return cso_available

    elif (
        section in TERRORISM_OFFENCES and indictable_maximum >= 10 and mode == "hybrid"
    ):
        cso_available["status"] = "available (summary conviction only)"
        cso_available["section"] = "cc742.1(d)"
        cso_available["reason"] = "serious indictable terrorism offence"

        return cso_available
    
    elif (
        section in CRIMINAL_ORGANIZATION_OFFENCES
        and indictable_maximum >= 10
        and mode == "indictable"
    ):
        cso_available["status"] = "unavailable"
        cso_available["section"] = "cc742.1(d)"
        cso_available["reason"] = "serious indictable criminal organization offence"

        return cso_available
    
    elif (
        section in CRIMINAL_ORGANIZATION_OFFENCES
        and indictable_maximum >= 10
        and mode == "hybrid"
    ):
        cso_available["status"] = "available (summary conviction only)"
        cso_available["section"] = "cc742.1(d)"
        cso_available["reason"] = "serious indictable criminal organization offence"

        return cso_available
    
    else:
        cso_available["status"] = "available"
        cso_available["section"] = "cc742.1"
        cso_available["reason"] = None

        return cso_available

# Intermittent sentences
def check_intermittent_available(summary_minimum, indictable_minimum):
    """
    Where facilities are available, the court may order that anyone sentenced
    to 90 days or less serve their sentence intermittently. The only excluded
    offences are those with a mandatory minimum term of imprisonment longer 
    than 90 days.
    """

    intermittent_available = {}

    if summary_minimum["amount"]:
        convert_quantum_to_days(summary_minimum)
        if int(summary_minimum["amount"]) > 90:
            intermittent_available["status"] = "unavailable"
            intermittent_available["section"] = "cc732(1)"
            intermittent_available["reason"] = "mandatory minimum term of imprisonment exceeds 90 days"

            return intermittent_available
        
        else:
            intermittent_available["status"] = "available"
            intermittent_available["section"] = "cc732(1)"
            intermittent_available["reason"] = None

            return intermittent_available
    
    elif indictable_minimum["amount"]:
        convert_quantum_to_days(indictable_minimum)
        if int(indictable_minimum["amount"]) > 90:
            intermittent_available["status"] = "unavailable"
            intermittent_available["section"] = "cc732(1)"
            intermittent_available["reason"] = "mandatory minimum term of imprisonment exceeds 90 days"

            return intermittent_available
        
        else:
            intermittent_available["status"] = "available"
            intermittent_available["section"] = "cc732(1)"
            intermittent_available["reason"] = None

            return intermittent_available


# Collateral consequences
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
        inadmissibilty_list.append(
            {
                "section": "irpa34(1)",
                "status": "permanent resident",
                "reason": "security",
            }
        )

    if section == "cc240.1":
        inadmissibilty_list.append(
            {
                "section": "irpa35(1)(c.1)",
                "status": "permanent resident",
                "reason": "human or international rights violations",
            }
        )
        inadmissibilty_list.append(
            {
                "section": "irpa35(1)(c.1)",
                "status": "foreign national",
                "reason": "human or international rights violations",
            }
        )

    if indictable_maximum >= 10:
        inadmissibilty_list.append(
            {
                "section": "irpa36(1)",
                "status": "permanent resident",
                "reason": "serious criminality",
            }
        )
        inadmissibilty_list.append(
            {
                "section": "irpa36(1)",
                "status": "foreign national",
                "reason": "serious criminality",
            }
        )

    if mode == "hybrid" or mode == "indictable":
        inadmissibilty_list.append(
            {
                "section": "irpa36(2)",
                "status": "foreign national",
                "reason": "criminality",
            }
        )

    return inadmissibilty_list


# Ancillary orders
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
    

def check_section_515_mandatory_weapons_prohibition(section):
    pass

