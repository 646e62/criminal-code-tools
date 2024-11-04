from constants import (
    PRIMARY_DESIGNATED_DNA_OFFENCES,
    SECONDARY_DESIGNATED_DNA_OFFENCES,
    EXCLUDED_CSO_OFFENCES,
    TERRORISM_OFFENCES,
    CRIMINAL_ORGANIZATION_OFFENCES,
    SECTION_469_OFFENCES,
    PRIMARY_SOIRA_OFFENCES_CURRENT,
    SECONDARY_SOIRA_OFFENCES,
    SOIRA_OFFENCES_ATTEMPTS,
    SOIRA_OFFENCES_CONSPIRACY,
    PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_CRIMINAL_ORGANIZATION,
    PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_CDSA,
    PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_CANNABIS,
    PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_HUMAN_TRAFFICKING,
    ABSOLUTE_JURISDICITON_OFFENCES_FRAUD,
    ABSOLUTE_JURISDICITON_OFFENCES_ATTEMPTS_CONSPIRACIES,
    ABSOLUTE_JURISDICITON_OFFENCES_DESIGNATED_OFFENCES,
    ABSOLUTE_JURISDICITON_OFFENCES_FALSE_PRETENCES,
    ABSOLUTE_JURISDICITON_OFFENCES_PPOBC,
    ABSOLUTE_JURISDICITON_OFFENCES_THEFT,
    ABSOLUTE_JURISDICTION_OFFENCES_MISCHIEF,
    SECTION_161_FORFEITURE_ORDER_OFFENCES,
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
def check_prelim_available(indictable_maximum):
    """
    Check if the preliminary inquiry is available for a given offence.
    """

    prelim_available = {}

    if indictable_maximum == "14y" or offence == "255y":
        prelim_available["status"] = {
            "available": True,
            "notes": "",
            },
        prelim_available["section"] = "cc535"
        prelim_available["reason"] = "maximum prison term of 14y or greater"
        
        return prelim_available
    else:
        prelim_available["status"] = {
            "available": False,
            "notes": "",
            },
        prelim_available["section"] = "cc535"
        prelim_available["reason"] = "maximum term of less than 14y"
        
        return prelim_available


def reverse_onus():
    pass


def check_section_469_offence(section):
    """
    Quick check to determine whether an offence exists in the 469 list. Has 
    implication on which court can adjudicate a show-cause hearing.
    """

    if section in SECTION_469_OFFENCES:
        return True
    else:
        return False


def check_absolute_jurisdiction_offence(section):
    
    absolute_jurisdiction_list = []

    if section in ABSOLUTE_JURISDICITON_OFFENCES_THEFT:
        absolute_jurisdiction_list.append(
            {
                "status": {
                    "available": True,
                    "notes": "",
            },
                "section": "cc553(a)(i)",
                "reason": "theft (other than cattle theft)",
            }
        )

    if section in ABSOLUTE_JURISDICITON_OFFENCES_FALSE_PRETENCES:
        absolute_jurisdiction_list.append(
            {
                "status": {
                    "available": True,
                    "notes": "",
            },
                "section": "cc553(a)(ii)",
                "reason": "false pretences",
            }
        )

    if section in ABSOLUTE_JURISDICITON_OFFENCES_PPOBC:
        absolute_jurisdiction_list.append(
            {
                "status": {
                    "available": True,
                    "notes": "",
            },
                "section": "cc553(a)(iii)",
                "reason": "possession of property obtained by crime",
            }
        )

    if section in ABSOLUTE_JURISDICITON_OFFENCES_FRAUD:
        absolute_jurisdiction_list.append(
            {
                "status": {
                    "available": True,
                    "notes": "",
            },
                "section": "cc553(a)(iv)",
                "reason": "fraud",
            }
        )

    if section in ABSOLUTE_JURISDICTION_OFFENCES_MISCHIEF:
        absolute_jurisdiction_list.append(
            {
                "status": {
                    "available": True,
                    "notes": "",
            },
                "section": "cc553(a)(v)",
                "reason": "mischief",
            }
        )

    if section in ABSOLUTE_JURISDICITON_OFFENCES_ATTEMPTS_CONSPIRACIES:
        absolute_jurisdiction_list.append(
            {
                "status": {
                    "available": True,
                    "notes": "",
            },
                "section": "cc553(b)",
                "reason": "attempt or conspiracies in relation to cc554(a) or (c)",
            }
        )

    if section in ABSOLUTE_JURISDICITON_OFFENCES_DESIGNATED_OFFENCES:
        absolute_jurisdiction_list.append(
            {
                "status": {
                    "available": True,
                    "notes": "",
            },
                "section": "cc553(c)",
                "reason": "designated offences",
            }
        )

    if absolute_jurisdiction_list == []:
        absolute_jurisdiction_list.append(
            {
                "status": {
                    "available": False,
                    "notes": "",
            },
                "section": "cc553",
                "reason": "",
            }
        )

    return absolute_jurisdiction_list

########################
##                    ##
## Sentencing options ##
##                    ##
########################

def check_discharge_available(summary_minimum, indictable_minimum, indictable_maximum):
    """
    Discharges are available when the following conditions obtain:
    - The offence does not have a mandatory minimum of any kind
    - The offence is not punishable by 14y or greater
    """

    discharge_available = {}

    if summary_minimum["amount"] or indictable_minimum["amount"]:
        discharge_available["status"] = {
            "available": False,
            "notes": "",
        },
        discharge_available["section"] = "cc730(1)"
        discharge_available["reason"] = "mandatory minimum sentence"

        return discharge_available

    elif indictable_maximum["amount"] >= 14:
        discharge_available["status"] = {
            "available": False,
            "notes": "",
        },
        discharge_available["section"] = "cc730(1)"
        discharge_available["reason"] = "maximum term of 14y or greater"

        return discharge_available
    
    else:
        discharge_available["status"] = {
            "available": True,
            "notes": "",
        },
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
            cso_available["status"] = {
                "available": False,
                "notes": "",
            },
            cso_available["section"] = "cc742.1(b)"
            cso_available["reason"] = "mandatory minimum term of imprisonment"

            return cso_available
        
        else:
            cso_available["status"] = {
                "available": True,
                "notes": "",
            },
            cso_available["section"] = "cc742.1"
            cso_available["reason"] = None

            return cso_available


    elif indictable_minimum["amount"]:

        if indictable_minimum["unit"] == "days" or indictable_minimum["unit"] == "months" or indictable_minimum["unit"] == "years":
            cso_available["status"] = {
                "available": False,
                "notes": "",
            },
            cso_available["section"] = "cc742.1(b)"
            cso_available["reason"] = "mandatory minimum term of imprisonment"

            return cso_available
        
        else:
            cso_available["status"] = {
                "available": True,
                "notes": "",
            },
            cso_available["section"] = "cc742.1"
            cso_available["reason"] = None

    elif section in EXCLUDED_CSO_OFFENCES:
        cso_available["status"] = {
            "available": False,
            "notes": "",
        },
        cso_available["section"] = "cc742.1(c)"
        cso_available["reason"] = "enumerated excluded offence"

        return cso_available

    elif (
        section in TERRORISM_OFFENCES
        and indictable_maximum["amount"] >= 10
        and mode == "indictable"
    ):
        cso_available["status"] = {
            "available": False,
            "notes": "",
        },
        cso_available["section"] = "cc742.1(d)"
        cso_available["reason"] = "serious indictable terrorism offence"

        return cso_available

    elif (
        section in TERRORISM_OFFENCES and indictable_maximum >= 10 and mode == "hybrid"
    ):
        cso_available["status"] = {
                "available": True,
                "notes": "summary conviction only",
        },
        cso_available["section"] = "cc742.1(d)"
        cso_available["reason"] = "serious indictable terrorism offence"

        return cso_available
    
    elif (
        section in CRIMINAL_ORGANIZATION_OFFENCES
        and indictable_maximum["amount"] >= 10
        and mode == "indictable"
    ):
        cso_available["status"] = {
            "available": False,
            "notes": "",
        },
        cso_available["section"] = "cc742.1(d)"
        cso_available["reason"] = "serious indictable criminal organization offence"

        return cso_available
    
    elif (
        section in CRIMINAL_ORGANIZATION_OFFENCES
        and indictable_maximum["amount"] >= 10
        and mode == "hybrid"
    ):
        cso_available["status"] = {
            "available": True,
            "notes": "summary conviction only",
        },
        cso_available["section"] = "cc742.1(d)"
        cso_available["reason"] = "serious indictable criminal organization offence"

        return cso_available
    
    else:
        cso_available["status"] = {
            "available": True,
            "notes": "",
        },
        cso_available["section"] = "cc742.1"
        cso_available["reason"] = None

        return cso_available


def check_intermittent_available(summary_minimum, indictable_minimum):
    """
    Where facilities are available, the court may order that anyone sentenced
    to 90 days or less serve their sentence intermittently. The only excluded
    offences are those with a mandatory minimum term of imprisonment longer 
    than 90 days.
    """

    intermittent_available = {}
    summary_minimum = convert_quantum_to_days(summary_minimum)
    indictable_minimum = convert_quantum_to_days(indictable_minimum)

    print(summary_minimum, indictable_minimum)

    if summary_minimum == None and indictable_minimum == None:
        intermittent_available["status"] = {
            "available": True,
            "notes": "",
        },
        intermittent_available["section"] = "cc732(1)"
        intermittent_available["reason"] = "no minimum term of imprisonment"

        return intermittent_available

    elif summary_minimum["amount"] and int(summary_minimum["amount"]) <= 90:
        intermittent_available["status"] = {
            "available": True,
            "notes": "",
        },
        intermittent_available["section"] = "cc732(1)"
        intermittent_available["reason"] = "minimum does not exceed 90 days"

        return intermittent_available
    
    elif indictable_minimum["amount"] and int(indictable_minimum["amount"]) <= 90:
        intermittent_available["status"] = {
            "available": True,
            "notes": "",
        },
        intermittent_available["section"] = "cc732(1)"
        intermittent_available["reason"] = "minimum does not exceed 90 days"

        return intermittent_available
    
    else:
        intermittent_available["status"] = {
            "available": False,
            "notes": "",
        },
        intermittent_available["section"] = "cc732(1)"
        intermittent_available["reason"] = "mandatory minimum term of imprisonment exceeds 90 days"

        return intermittent_available


def check_suspended_sentence_available(summary_minimum, indictable_minimum):
    """
    A suspended sentence is available for any offence without a mandatory 
    minimum and where the offender is sentenced to two years or less. The 
    latter can be mapped out in a later version of the program, when we start
    to parse imposed sentences, rather than simply creating an offence grid.
    """

    suspended_sentence_available = {}

    if summary_minimum["amount"]:
        suspended_sentence_available["status"] = {
            "available": False,
            "notes": "",
        },
        suspended_sentence_available["section"] = "cc731(1)"
        suspended_sentence_available["reason"] = "mandatory minimum sentence"

        return suspended_sentence_available
    
    elif indictable_minimum["amount"]:
        suspended_sentence_available["status"] = {
            "available": False,
            "notes": "",
        },
        suspended_sentence_available["section"] = "cc731(1)"
        suspended_sentence_available["reason"] = "mandatory minimum sentence"

        return suspended_sentence_available
        
    else:
        suspended_sentence_available["status"] = {
            "available": True,
            "notes": "",
        },
        suspended_sentence_available["section"] = "cc731(1)"
        suspended_sentence_available["reason"] = None

        return suspended_sentence_available
    

def check_prison_and_probation(mode, indictable_minimum):
    """
    A suspended sentence is available for any offence that doesn't have a 
    mandatory minimum exceeding two years. If the offence is hybrid, 
    probation is available on summary conviction proceedings. If the offence
    is straight indictable, probation is available where the minimum term of
    imprisonment is less than two years.
    """

    prison_and_probation_available = {}

    # Convert the quantum of the offence to days if it is not already in that
    # format
    
    if indictable_minimum["amount"] == None:
        prison_and_probation_available["status"] = {
            "available": True,
            "notes": "",
        },
        prison_and_probation_available["section"] = "cc732(1)"
        prison_and_probation_available["reason"] = "no minimum term of imprisonment"

        return prison_and_probation_available
    else:
        indictable_minimum = convert_quantum_to_days(indictable_minimum)

    if mode == "summary":
        prison_and_probation_available["status"] = {
            "available": True,
            "notes": "",
        },
        prison_and_probation_available["section"] = "cc732(1)(b)"
        prison_and_probation_available["reason"] = None

        return prison_and_probation_available

    elif mode == "hybrid":
        if indictable_minimum["amount"] < 730:
            prison_and_probation_available["status"] = {
                "available": True,
                "notes": "",
            },
            prison_and_probation_available["section"] = "cc732(1)"
            prison_and_probation_available["reason"] = None

            return prison_and_probation_available
        else:
            prison_and_probation_available["status"] = {
                "available": False,
                "notes": "",
            },
            prison_and_probation_available["section"] = "cc732(1)"
            prison_and_probation_available["reason"] = "mandatory minimum term of imprisonment exceeds two years"

            return prison_and_probation_available

    elif mode == "indictable":
        if indictable_minimum["amount"] < 730:
            prison_and_probation_available["status"] = {
                "available": True,
                "notes": "",
            },
            prison_and_probation_available["section"] = "cc732(1)"
            prison_and_probation_available["reason"] = None

            return prison_and_probation_available
        else:
            prison_and_probation_available["status"] = {
                "available": False,
                "notes": "",
            },
            prison_and_probation_available["section"] = "cc732(1)"
            prison_and_probation_available["reason"] = "mandatory minimum term of imprisonment exceeds two years"

            return prison_and_probation_available


def check_fine_alone(summary_minimum, indictable_minimum):
    """
    Checks to see whether the offence has a mandatory minimum prison term. If
    so, a fine alone is not available. Otherwise, it is.
    """

    fine_alone_available = {}

    print(indictable_minimum)

    if summary_minimum["amount"] == None or indictable_minimum["amount"] == None:
        fine_alone_available["status"] = {
            "available": True,
            "notes": "",
        },
        fine_alone_available["section"] = "cc734(1)"
        fine_alone_available["reason"] = "no mandatory minimum term of imprisonment"

        return fine_alone_available

    if summary_minimum["amount"]:
        fine_alone_available["status"] = {
            "available": False,
            "notes": "",
        },
        fine_alone_available["section"] = "cc734(1)"
        fine_alone_available["reason"] = "mandatory minimum term of imprisonment"

        return fine_alone_available
    
    elif indictable_minimum["amount"]:
        fine_alone_available["status"] = {
            "available": False,
            "notes": "",
        },
        fine_alone_available["section"] = "cc734(1)"
        fine_alone_available["reason"] = "mandatory minimum term of imprisonment"

        return fine_alone_available


def check_fine_and_probation(indictable_minimum):
    """
    The same rules apply to this check as to the check for prison and 
    probation. If the offence has a mandatory minimum term of imprisonment that
    exceeds two years, probation is not available. Otherwise, it is.

    The function only checks for indictable offences, as summary maximums are
    all below two years.
    """

    fine_and_probation_available = {}
    print(indictable_minimum)

    if indictable_minimum["amount"] == None:
        fine_and_probation_available["status"] = {
            "available": True,
            "notes": "",
        },
        fine_and_probation_available["section"] = "cc732(1)"
        fine_and_probation_available["reason"] = "no minimum term of imprisonment"

        return fine_and_probation_available
    
    else:
        indictable_minimum = convert_quantum_to_days(indictable_minimum)

    if indictable_minimum["amount"] < 730:
        fine_and_probation_available["status"] = {
            "available": True,
            "notes": "",
        },
        fine_and_probation_available["section"] = "cc732(1)"
        fine_and_probation_available["reason"] = None

        return fine_and_probation_available
    else:
        fine_and_probation_available["status"] = {
            "available": False,
            "notes": "",
        },
        fine_and_probation_available["section"] = "cc732(1)"
        fine_and_probation_available["reason"] = "mandatory minimum term of imprisonment exceeds two years"

        return fine_and_probation_available


def check_fine_probation_intermittent(summary_minimum, indictable_minimum):
    """
    Check to see if an intermittent sentence is available. If it is, the court
    can also impose the fine and probation order. The only offences excluded
    from this are those with a mandatory minimum term of imprisonment exceeding
    90 days.

    Keep this code as a separate function. Although it just duplicates the
    check_intermittent_available function, the two checks should be kept apart
    in case the logic for either changes in the future.
    """

    fine_probation_intermittent_available = check_intermittent_available(
        summary_minimum, indictable_minimum
    )

    return fine_probation_intermittent_available


#############################
##                         ##
## Collateral consequences ##
##                         ##
#############################

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
    

def check_soira(section, mode, indictable_maximum):
    """
    SOIRA orders are available when an offender is convicted of one or more of 
    the designated offences. The duration of the order depends on several 
    factors, including:
    - The mode the offence was prosecuted in;
    - The maximum term of imprisonment;
    - Whether the offender was convicted of multiple designated offences in the
    same proceeding; and
    - The offender's prior criminal record.

    
    """

    soira_list = []
    
    # Check to see whether the offence is a designated SOIRA offence
    if section in PRIMARY_SOIRA_OFFENCES_CURRENT:
        soira_list.append(
            {
                "section": [
                    "cc490.011[primary offence](a)",
                    ],
                "status": "primary",
                "reason": "primary designated offence",
            }
        )

    elif section in SECONDARY_SOIRA_OFFENCES:
        soira_list.append(
            {
                "section": [
                    "cc490.011[secondary offence](a)",
                    ],
                "status": "secondary",
                "reason": "secondary designated offence",
            }
        )
    elif section in SOIRA_OFFENCES_ATTEMPTS:
        soira_list.append(
            {
                "section": [
                    "cc490.011[primary offence](f)", 
                    "cc490.011[secondary offence](b)",
                    ],
                "status": "secondary",
                "reason": "attempted designated offence",
            }
        )
    elif section in SOIRA_OFFENCES_CONSPIRACY:
        soira_list.append(
            {
                "section": [
                    "cc490.011[primary offence](f)", 
                    "cc490.011[secondary offence](b)",
                    ],
                "status": "secondary",
                "reason": "conspiracy to commit designated offence",
            }
        )
    else:
        return None
    
    # Determine the duration of the SOIRA order
    # cc490.011(2)
    if mode == "summary":
        soira_list[0]["section"].append("cc490.011(2)(a)")
        soira_list[0]["duration"] = {
            "amount": 10,
            "unit": "years",
        }

    elif int(indictable_maximum["amount"] == 2 or int(indictable_maximum["amount"]) == 5):
        soira_list[0]["section"].append("cc490.011(2)(a)")
        soira_list[0]["duration"] = {
            "amount": 10,
            "unit": "years",
        }

    elif int(indictable_maximum["amount"]) == 10 or int(indictable_maximum["amount"]) == 14:
        soira_list[0]["section"].append("cc490.011(2)(b)")
        soira_list[0]["duration"] = {
            "amount": 20,
            "unit": "years",
        }

    elif int(indictable_maximum["amount"]) == 255:
        soira_list[0]["section"].append("cc490.011(2)(c)")
        soira_list[0]["duration"] = {
            "amount": 255,
            "unit": "years",
        }
    
    # cc490.13(3) & (5) are implementable once we have data for an offender's
    # criminal record

    return soira_list


def check_proceeds_of_crime_forfeiture(section, mode):

    proceeds_list = []

    if mode == "summary":
        proceeds_list.append(
            {
                "section": [
                    "cc462.3[designated offence]",
                    "cc462.37(1)",
                    ],
                "status": "unavailable",
                "reason": "strictly summary conviction offence",
            }
        )

        return proceeds_list
    
    elif section in PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_CRIMINAL_ORGANIZATION:
        proceeds_list.append(
            {
                "section": [
                    "cc462.37(2.02)(a)"
                    ],
                "status": "available",
                "reason": "particular circumstances — criminal organization offence",
            }
        )

    elif section in PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_CDSA:
        proceeds_list.append(
            {
                "section": [
                    "cc462.37(2.02)(b)"
                    ],
                "status": "available",
                "reason": "particular circumstances — CDSA offence",
            }
        )

    elif section in PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_CANNABIS:
        proceeds_list.append(
            {
                "section": [
                    "cc462.37(2.02)(c)"
                    ],
                "status": "available",
                "reason": "particular circumstances — cannabis offence",
            }
        )

    elif section in PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_HUMAN_TRAFFICKING:
        proceeds_list.append(
            {
                "section": [
                    "cc462.37(2.02)(d)"
                    ],
                "status": "available",
                "reason": "particular circumstances — human trafficking offence",
            }
        )

    else:
        proceeds_list.append(
            {
                "section": [
                    "cc462.3[designated offence]",
                    "cc462.37(1)",],
                "status": "available",
                "reason": "offence prosecutable by indictment",
            }   
        )

    return proceeds_list


def check_section_164_forfeiture_order(section):
    """
    Checks whether the offence is one of the enumerated offences for which a
    cc164.2 forfeiture order is required.
    """

    section_164_forfeiture_list = []

    if section in SECTION_161_FORFEITURE_ORDER_OFFENCES:
        section_164_forfeiture_list.append(
            {
                "section": "cc164.2",
                "reason": "enumerated offence",
            }
        )
    
    return section_164_forfeiture_list


def check_section_515_mandatory_weapons_prohibition(section):
    pass
