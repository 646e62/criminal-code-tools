"""
Criminal Code of Canada rules for creating a sentencing grid. The rules are 
current to October 2, 2024.
"""

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
    VIOLENCE_USED_THREATENED_ATTEMPTED_OFFENCES,
)

from utils import (
    convert_quantum_to_days,
    standard_output,
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

# Procedure
def check_prelim_available(indictable_maximum):
    """
    Check if the preliminary inquiry is available for a given offence.
    """

    if indictable_maximum == "14y" or indictable_maximum == "255y":
        prelim_available = standard_output(
            True, 
            None,
            ["cc535"], 
            "maximum term of 14y or greater"
        )
        return prelim_available
    
    else:
        prelim_available = standard_output(
            False, 
            None, 
            ["cc535"], 
            "maximum of less than 14y"
        )
        return prelim_available


def reverse_onus():
    pass


def check_section_469_offence(section):
    """
    Quick check to determine whether an offence exists in the 469 list. Has
    implication on which court can adjudicate a show-cause hearing.
    """

    if section in SECTION_469_OFFENCES:
        return standard_output(
            True, 
            None, 
            ["cc469"], 
            "listed offence"
        )
    
    else:
        return standard_output(
            False, 
            None, 
            ["cc469"], 
            "not a listed offence"
        )


def check_absolute_jurisdiction_offence(section):

    absolute_jurisdiction_list = []

    if section in ABSOLUTE_JURISDICITON_OFFENCES_THEFT:
        absolute_jurisdiction_list.append(
            standard_output(
                True,
                None,
                ["cc553(a)(i)"],
                "theft (other than cattle theft)",
            )
        )

    if section in ABSOLUTE_JURISDICITON_OFFENCES_FALSE_PRETENCES:
        absolute_jurisdiction_list.append(
            standard_output(
                True,
                None,
                ["cc553(a)(ii)"],
                "false pretences"
            )
        )

    if section in ABSOLUTE_JURISDICITON_OFFENCES_PPOBC:
        absolute_jurisdiction_list.append(
            standard_output(
                True,
                None,
                ["cc553(a)(iii)"],
                "possession of property obtained by crime"
            )
        )

    if section in ABSOLUTE_JURISDICITON_OFFENCES_FRAUD:
        absolute_jurisdiction_list.append(
            standard_output(
                True,
                None,
                ["cc553(a)(iv)"],
                "fraud"
            )
        )

    if section in ABSOLUTE_JURISDICTION_OFFENCES_MISCHIEF:
        absolute_jurisdiction_list.append(
            standard_output(
                True,
                None,
                ["cc553(a)(v)"],
                "mischief"
            )
        )

    if section in ABSOLUTE_JURISDICITON_OFFENCES_ATTEMPTS_CONSPIRACIES:
        absolute_jurisdiction_list.append(
            standard_output(
                True,
                None,
                "cc553(b)",
                "attempt or conspiracies in relation to cc554(a) or (c)"
            )
        )

    if section in ABSOLUTE_JURISDICITON_OFFENCES_DESIGNATED_OFFENCES:
        absolute_jurisdiction_list.append(
            standard_output(
                True,
                None,
                "cc553(c)",
                "designated offences",
            )
        )

    if absolute_jurisdiction_list == []:
        absolute_jurisdiction_list.append(
            standard_output(
                False,
                None,
                ["cc553"],
                "not an absolute jurisdiction offence"
            )
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

    if summary_minimum["jail"]["amount"] or indictable_minimum["jail"]["amount"]:
        return standard_output(
            False,
            None,
            ["cc730(1)"],
            "mandatory minimum sentence"
        )

    elif indictable_maximum["jail"]["amount"] >= 14:
        return standard_output(
            False,
            None,
            ["cc730(1)"],
            "maximum term of 14y or greater"
        )

    else:
        return standard_output(
            True,
            None,
            ["cc730(1)"],
            "no mandatory minimum, punishable by less than 14y"
        )
    

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
    # Confirm whether this is necessary since the v0.0.5 updates to the program
    try:
        indictable_maximum["jail"]["amount"] = int(indictable_maximum["amount"])
    except:
        indictable_maximum["jail"]["amount"] = 0

    cso_available = {}

    if summary_minimum["jail"]["amount"]:

        if (
            summary_minimum["jail"]["unit"] == "days"
            or summary_minimum["jail"]["unit"] == "months"
            or summary_minimum["jail"]["unit"] == "years"
        ):
            return standard_output(
                False,
                None,
                ["cc742.1(b)"],
                "mandatory minimum term of imprisonment"
            )

        else:
            return standard_output(
                True,
                None,
                ["cc742.1"],
                "no mandatory minimum"
            )

    elif indictable_minimum["jail"]["amount"]:

        if (
            indictable_minimum["jail"]["unit"] == "days"
            or indictable_minimum["jail"]["unit"] == "months"
            or indictable_minimum["jail"]["unit"] == "years"
        ):
            return standard_output(
                False,
                None,
                ["cc742.1(b)"],
                "mandatory minimum term of imprisonment"
            )

        else:
            return standard_output(
                True,
                None,
                ["cc742.1"],
                None
            )

    elif section in EXCLUDED_CSO_OFFENCES:
        return standard_output(
            False,
            None,
            ["cc742.1(c)"],
            "enumerated excluded offence"
        )

    elif (
        section in TERRORISM_OFFENCES
        and int(indictable_maximum["jail"]["amount"]) >= 10
        and mode == "indictable"
    ):
        return standard_output(
            False,
            None,
            ["cc742.1(d)"],
            "serious indictable terrorism offence"
        )

    elif (
        section in TERRORISM_OFFENCES and int(indictable_maximum["jail"]["amount"]) >= 10 and mode == "hybrid"
    ):
        return standard_output(
            True,
            "summary conviction only",
            ["cc742.1(d)"],
            "serious indictable terrorism offence"
        )

    elif (
        section in CRIMINAL_ORGANIZATION_OFFENCES
        and int(indictable_maximum["jail"]["amount"]) >= 10
        and mode == "indictable"
    ):
        return standard_output(
            False,
            "summary conviction only",
            ["cc742.1(d)"],
            "serious indictable criminal organization offence"
        )

    elif (
        section in CRIMINAL_ORGANIZATION_OFFENCES
        and int(indictable_maximum["jail"]["amount"]) >= 10
        and mode == "hybrid"
    ):
        return standard_output(
            True,
            "summary conviction only",
            ["cc742.1(d)"],
            "serious indictable criminal organization offence"
        )

    else:
        return standard_output(
            True,
            None,
            ["cc742.1"],
            None
        )


def check_intermittent_available(summary_minimum, indictable_minimum):
    """
    Where facilities are available, the court may order that anyone sentenced
    to 90 days or less serve their sentence intermittently. The only excluded
    offences are those with a mandatory minimum term of imprisonment longer
    than 90 days.
    """

    if summary_minimum["jail"]["amount"] == 0 and indictable_minimum["jail"]["amount"] == 0:
        return standard_output(
            True,
            None,
            ["cc732(1)"],
            "no minimum term of imprisonment"
        )

    elif summary_minimum["jail"]["amount"] and int(summary_minimum["jail"]["amount"]) <= 90:
        return standard_output(
            True,
            None,
            ["cc732(1)"],
            "minimum does not exceed 90 days"
        )

    elif indictable_minimum["jail"]["amount"] and int(indictable_minimum["jail"]["amount"]) <= 90:
        return standard_output(
            True,
            None,
            ["cc732(1)"],
            "minimum does not exceed 90 days"
        )

    else:
        return standard_output(
            False,
            None,
            ["cc732"],
            "mandatory minimum term of imprisonment exceeds 90 days"
        )


def check_suspended_sentence_available(summary_minimum, indictable_minimum):
    """
    A suspended sentence is available for any offence without a mandatory
    minimum and where the offender is sentenced to two years or less. The
    latter can be mapped out in a later version of the program, when we start
    to parse imposed sentences, rather than simply creating an offence grid.
    """

    if summary_minimum["jail"]["amount"] or summary_minimum["fine"]["amount"]:
        return standard_output(
            False,
            None,
            ["cc731(1)"],
            "mandatory minimum sentence"
        )

    elif indictable_minimum["jail"]["amount"] or indictable_minimum["fine"]["amount"]:
        return standard_output(
            False,
            None,
            ["cc731(1)"],
            "mandatory minimum sentence"
        )

    else:
        return standard_output(
            True,
            None,
            ["cc731(1)"],
            "no mandatory minimum sentence"
        )


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

    if indictable_minimum["jail"]["amount"] == None:
        prison_and_probation_available["status"] = (
            {
                "available": True,
                "notes": None,
            },
        )
        prison_and_probation_available["section"] = "cc732(1)"
        prison_and_probation_available["notes"] = "no minimum term of imprisonment"

        return prison_and_probation_available

    if mode == "summary":
        prison_and_probation_available["status"] = (
            {
                "available": True,
                "notes": None,
            },
        )
        prison_and_probation_available["section"] = "cc732(1)(b)"
        prison_and_probation_available["notes"] = None

        return prison_and_probation_available

    elif mode == "hybrid":
        if int(indictable_minimum["jail"]["amount"]) < 730:
            prison_and_probation_available["status"] = (
                {
                    "available": True,
                    "notes": None,
                },
            )
            prison_and_probation_available["section"] = "cc732(1)"
            prison_and_probation_available["notes"] = None

            return prison_and_probation_available
        else:
            prison_and_probation_available["status"] = (
                {
                    "available": False,
                    "notes": None,
                },
            )
            prison_and_probation_available["section"] = "cc732(1)"
            prison_and_probation_available["notes"] = (
                "mandatory minimum term of imprisonment exceeds two years"
            )

            return prison_and_probation_available

    elif mode == "indictable":
        if int(indictable_minimum["jail"]["amount"]) < 730:
            prison_and_probation_available["status"] = (
                {
                    "available": True,
                    "notes": None,
                },
            )
            prison_and_probation_available["section"] = "cc732(1)"
            prison_and_probation_available["notes"] = None

            return prison_and_probation_available
        else:
            prison_and_probation_available["status"] = (
                {
                    "available": False,
                    "notes": None,
                },
            )
            prison_and_probation_available["section"] = "cc732(1)"
            prison_and_probation_available["notes"] = (
                "mandatory minimum term of imprisonment exceeds two years"
            )

            return prison_and_probation_available


def check_fine_alone(summary_minimum, indictable_minimum):
    """
    Checks to see whether the offence has a mandatory minimum prison term. If
    so, a fine alone is not available. Otherwise, it is.
    """

    fine_alone_available = {}

    if summary_minimum["jail"]["amount"] == None or indictable_minimum["jail"]["amount"] == None:
        fine_alone_available["status"] = (
            {
                "available": True,
                "notes": None,
            },
        )
        fine_alone_available["section"] = "cc734(1)"
        fine_alone_available["notes"] = "no mandatory minimum term of imprisonment"

        return fine_alone_available

    if summary_minimum["jail"]["amount"]:
        fine_alone_available["status"] = (
            {
                "available": False,
                "notes": None,
            },
        )
        fine_alone_available["section"] = "cc734(1)"
        fine_alone_available["notes"] = "mandatory minimum term of imprisonment"

        return fine_alone_available

    elif indictable_minimum["jail"]["amount"]:
        fine_alone_available["status"] = (
            {
                "available": False,
                "notes": None,
            },
        )
        fine_alone_available["section"] = "cc734(1)"
        fine_alone_available["notes"] = "mandatory minimum term of imprisonment"

        return fine_alone_available


def check_fine_and_probation(indictable_minimum):
    """
    The same rules apply to this check as to the check for prison and
    probation. If the offence has a mandatory minimum term of imprisonment that
    exceeds two years, probation is not available. Otherwise, it is.

    The function only checks for indictable offences, as summary maximums are
    all below two years.
    """

    if int(indictable_minimum["jail"]["amount"]) == 0:
        return standard_output(
            True,
            None,
            ["cc732(1)"],
            "no minimum term of imprionment"
        )

    if int(indictable_minimum["jail"]["amount"]) < 730:
        return standard_output(
            True,
            None,
            ["cc732(1)"],
            None
        )
    
    else:
        return standard_output(
            False,
            None,
            ["cc732(1)"],
            "mandatory minimum term of imprisonment exceeds two years"
        )


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


# Ancillary orders
def check_dna_designation(offence, mode, quantum):
    """
    Check if the offence is a designated DNA offence.
    """

    if offence[0] in PRIMARY_DESIGNATED_DNA_OFFENCES:
        return standard_output(
            True,
            None,
            ["cc487.04"],
            "primary designated offence"
        )

    elif offence[0] in SECONDARY_DESIGNATED_DNA_OFFENCES:
        return standard_output(
            True,
            None,
            ["cc487.04"],
            "secondary designated offence"
        )
    
    elif (
        (mode == "indictable" or mode == "hybrid")
        and quantum["jail"]["unit"] == "years"
        and int(quantum["jail"]["amount"]) >= 5
    ):
        return standard_output(
            True,
            None,
            ["cc487.04"],
            "secondary designated offence"
        )
    
    else:
        return standard_output(
            False,
            None,
            ["cc487.04"],
            "not a designated offence"
        )


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
            standard_output(
                True,
                "primary",
                ["cc490.011[primary offence](a)"],
                "primary designated offence"
            )
        )

    elif section in SECONDARY_SOIRA_OFFENCES:
        soira_list.append(
            standard_output(
                True,
                "secondary",
                ["cc490.011[secondary offence](a)"],
                "secondary designated offence"
            )
        )
    elif section in SOIRA_OFFENCES_ATTEMPTS:
        soira_list.append(
            standard_output(
                True,
                "secondary",
                [
                    "cc490.011[primary offence](f)",
                    "cc490.011[secondary offence](b)",
                ],
                "attempted designated offence"
            )
        )
    elif section in SOIRA_OFFENCES_CONSPIRACY:
        soira_list.append(
            standard_output(
                True,
                "secondary",
                [
                    "cc490.011[primary offence](f)",
                    "cc490.011[secondary offence](b)",
                ],
                "conspiracy to commit designated offence"
            )
        )
    else:
        return standard_output(
            False,
            None,
            [
                "cc490.011[primary offence](f)",
                "cc490.011[secondary offence](b)",
            ],
            "not a designated offence"
        )

    # Determine the duration of the SOIRA order
    # Rework this code after recent re-writes, and adapt to use the standard
    # output function
    # cc490.011(2)
    if mode == "summary":
        soira_list[0]["section"].append("cc490.011(2)(a)")
        soira_list[0]["duration"] = {
            "amount": 10,
            "unit": "years",
        }

    elif int(
        indictable_maximum["amount"] == 2 or int(indictable_maximum["amount"]) == 5
    ):
        soira_list[0]["section"].append("cc490.011(2)(a)")
        soira_list[0]["duration"] = {
            "amount": 10,
            "unit": "years",
        }

    elif (
        int(indictable_maximum["amount"]) == 10
        or int(indictable_maximum["amount"]) == 14
    ):
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
            standard_output(
                False,
                None,
                [
                    "cc462.3[designated offence]",
                    "cc462.37(1)",
                ],
                "strictly summary conviction offence"
            )
        )

        return proceeds_list

    elif section in PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_CRIMINAL_ORGANIZATION:
        proceeds_list.append(
            standard_output(
                True,
                None,
                ["cc462.37(2.02)(a)"],
                "particular circumstances — criminal organization offence"
            )
        )

    elif section in PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_CDSA:
        proceeds_list.append(
            standard_output(
                True,
                None,
                ["cc462.37(2.02)(b)"],
                "particular circumstances — CDSA offence"
            )
        )

    elif section in PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_CANNABIS:
        proceeds_list.append(
            standard_output(
                True,
                None,
                ["cc462.37(2.02)(c)"],
                "particular circumstances — cannabis offence"
            )
        )

    elif section in PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_HUMAN_TRAFFICKING:
        proceeds_list.append(
            standard_output(
                True,
                None,
                ["cc462.37(2.02)(d)"],
                "particular circumstances — human trafficking offence"
            )
        )

    else:
        proceeds_list.append(
            standard_output(
                False,
                None,
                [
                    "cc462.3[designated offence]",
                    "cc462.37(1)",],
                "offence prosecutable by indictment"
            )
        )

    return proceeds_list


def check_section_164_forfeiture_order(section):
    """
    Checks whether the offence is one of the enumerated offences for which a
    cc164.2 forfeiture order is required.
    """

    if section in SECTION_161_FORFEITURE_ORDER_OFFENCES:
        return standard_output(
            True,
            None,
            ["cc164.2"],
            "enumerated offence"
        )


def check_section_109_weapons_prohibition(offence):
    """
    Checks if the offence fits the criteria for a section 109 prohibition 
    order. Some of the preconditions are case-specific, and thus are out of
    scope for this program at this time. Once the program starts to integrate
    NLP, we can start to parse the facts of the case to determine whether the
    offence meets the criteria for a section 109 order. Once this is possible,
    we should also be able to check for section 110 orders, which are almost 
    entirely fact-specific.
    """
    
    return standard_output(
        False,
        None,
        ["cc109"],
        "not a firearms offence"
    )

def check_section_515_mandatory_weapons_prohibition(section):
    pass
