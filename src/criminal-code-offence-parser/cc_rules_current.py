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

from typing import List, Dict, Union, Optional


# Basic metadata
def check_offence_type(offence: List[str]) -> str:
    """
    Check the type of offence for a given offence.

    Args:
        offence (List[str]): A row from the CSV file containing offence data
            [3] = indictable maximum
            [5] = summary maximum

    Returns:
        str: The type of offence - "summary", "indictable", or "hybrid"

    Raises:
        ValueError: If offence list is empty or doesn't have enough elements
        TypeError: If offence is not a list
    """
    if not isinstance(offence, list):
        raise TypeError("offence must be a list")
    if len(offence) < 6:
        raise ValueError("offence list must have at least 6 elements")

    if offence[3] == "":
        return "summary"
    elif offence[5] == "":
        return "indictable"
    else:
        return "hybrid"


# Procedure
def check_prelim_available(
    indictable_maximum: str,
) -> Dict[str, Union[bool, None, List[str], str]]:
    """
    Check if the preliminary inquiry is available for a given offence.

    Args:
        indictable_maximum (str): The maximum sentence for indictable proceedings

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether preliminary inquiry is available
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination

    Raises:
        TypeError: If indictable_maximum is not a string
    """
    if not isinstance(indictable_maximum, str):
        raise TypeError("indictable_maximum must be a string")

    if indictable_maximum == "14y" or indictable_maximum == "255y":
        prelim_available = standard_output(
            True, None, ["cc535"], "maximum term of 14y or greater"
        )
        return prelim_available

    else:
        prelim_available = standard_output(
            False, None, ["cc535"], "maximum of less than 14y"
        )
        return prelim_available


def reverse_onus():
    pass


def check_section_469_offence(
    section: str,
) -> Dict[str, Union[bool, None, List[str], str]]:
    """
    Quick check to determine whether an offence exists in the 469 list. Has
    implication on which court can adjudicate a show-cause hearing.

    Args:
        section (str): The section of the Criminal Code

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether the offence is listed
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

    if section in SECTION_469_OFFENCES:
        return standard_output(True, None, ["cc469"], "listed offence")

    else:
        return standard_output(False, None, ["cc469"], "not a listed offence")


def check_absolute_jurisdiction_offence(
    section: str,
) -> List[Dict[str, Union[bool, None, List[str], str]]]:
    """
    Check if the offence is an absolute jurisdiction offence.

    Args:
        section (str): The section of the Criminal Code

    Returns:
        List[Dict]: A list of dictionaries containing:
            - available (bool): Whether the offence is an absolute jurisdiction offence
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

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
            standard_output(True, None, ["cc553(a)(ii)"], "false pretences")
        )

    if section in ABSOLUTE_JURISDICITON_OFFENCES_PPOBC:
        absolute_jurisdiction_list.append(
            standard_output(
                True,
                None,
                ["cc553(a)(iii)"],
                "possession of property obtained by crime",
            )
        )

    if section in ABSOLUTE_JURISDICITON_OFFENCES_FRAUD:
        absolute_jurisdiction_list.append(
            standard_output(True, None, ["cc553(a)(iv)"], "fraud")
        )

    if section in ABSOLUTE_JURISDICTION_OFFENCES_MISCHIEF:
        absolute_jurisdiction_list.append(
            standard_output(True, None, ["cc553(a)(v)"], "mischief")
        )

    if section in ABSOLUTE_JURISDICITON_OFFENCES_ATTEMPTS_CONSPIRACIES:
        absolute_jurisdiction_list.append(
            standard_output(
                True,
                None,
                "cc553(b)",
                "attempt or conspiracies in relation to cc554(a) or (c)",
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
                False, None, ["cc553"], "not an absolute jurisdiction offence"
            )
        )

    return absolute_jurisdiction_list


########################
##                    ##
## Sentencing options ##
##                    ##
########################


def check_discharge_available(
    summary_minimum: Dict[str, Dict[str, Union[int, str]]],
    indictable_minimum: Dict[str, Dict[str, Union[int, str]]],
    indictable_maximum: Dict[str, Dict[str, Union[int, str]]],
) -> Dict[str, Union[bool, None, List[str], str]]:
    """
    Discharges are available when the following conditions obtain:
    - The offence does not have a mandatory minimum of any kind
    - The offence is not punishable by 14y or greater

    Args:
        summary_minimum (Dict): The minimum sentence for summary proceedings
        indictable_minimum (Dict): The minimum sentence for indictable proceedings
        indictable_maximum (Dict): The maximum sentence for indictable proceedings

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether discharge is available
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

    if summary_minimum["jail"]["amount"] or indictable_minimum["jail"]["amount"]:
        return standard_output(False, None, ["cc730(1)"], "mandatory minimum sentence")

    elif indictable_maximum["jail"]["amount"] >= 14:
        return standard_output(
            False, None, ["cc730(1)"], "maximum term of 14y or greater"
        )

    else:
        return standard_output(
            True,
            None,
            ["cc730(1)"],
            "no mandatory minimum, punishable by less than 14y",
        )


def check_cso_availablity(
    section: str,
    summary_minimum: Dict[str, Dict[str, Union[int, str]]],
    indictable_minimum: Dict[str, Dict[str, Union[int, str]]],
    indictable_maximum: Dict[str, Dict[str, Union[int, str]]],
    mode: str,
) -> Dict[str, Union[bool, None, List[str], str]]:
    """
    Check if the charge screening officer is available for a given offence. An offence
    qualifies for a CSO if the following conditions obtain:

    - The offence does not have a mandatory minimum term of imprisonment
    - The offence is not an enumerated offence
    - The offence is not:
      - A terrorism or criminal organization offence; AND
      - Punishable by 10y or more term of imprisonment; AND
      - Prosecuted by indictment

    Args:
        section (str): The section of the Criminal Code
        summary_minimum (Dict): The minimum sentence for summary proceedings
        indictable_minimum (Dict): The minimum sentence for indictable proceedings
        indictable_maximum (Dict): The maximum sentence for indictable proceedings
        mode (str): The mode of prosecution

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether CSO is available
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
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
                False, None, ["cc742.1(b)"], "mandatory minimum term of imprisonment"
            )

        else:
            return standard_output(True, None, ["cc742.1"], "no mandatory minimum")

    elif indictable_minimum["jail"]["amount"]:

        if (
            indictable_minimum["jail"]["unit"] == "days"
            or indictable_minimum["jail"]["unit"] == "months"
            or indictable_minimum["jail"]["unit"] == "years"
        ):
            return standard_output(
                False, None, ["cc742.1(b)"], "mandatory minimum term of imprisonment"
            )

        else:
            return standard_output(True, None, ["cc742.1"], None)

    elif section in EXCLUDED_CSO_OFFENCES:
        return standard_output(
            False, None, ["cc742.1(c)"], "enumerated excluded offence"
        )

    elif (
        section in TERRORISM_OFFENCES
        and int(indictable_maximum["jail"]["amount"]) >= 10
        and mode == "indictable"
    ):
        return standard_output(
            False, None, ["cc742.1(d)"], "serious indictable terrorism offence"
        )

    elif (
        section in TERRORISM_OFFENCES
        and int(indictable_maximum["jail"]["amount"]) >= 10
        and mode == "hybrid"
    ):
        return standard_output(
            True,
            "summary conviction only",
            ["cc742.1(d)"],
            "serious indictable terrorism offence",
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
            "serious indictable criminal organization offence",
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
            "serious indictable criminal organization offence",
        )

    else:
        return standard_output(True, None, ["cc742.1"], None)


def check_intermittent_available(
    summary_minimum: Dict[str, Dict[str, Union[int, str]]],
    indictable_minimum: Dict[str, Dict[str, Union[int, str]]],
) -> Dict[str, Union[bool, None, List[str], str]]:
    """
    Where facilities are available, the court may order that anyone sentenced
    to 90 days or less serve their sentence intermittently. The only excluded
    offences are those with a mandatory minimum term of imprisonment longer
    than 90 days.

    Args:
        summary_minimum (Dict): The minimum sentence for summary proceedings
        indictable_minimum (Dict): The minimum sentence for indictable proceedings

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether intermittent sentence is available
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

    if (
        summary_minimum["jail"]["amount"] == 0
        and indictable_minimum["jail"]["amount"] == 0
    ):
        return standard_output(
            True, None, ["cc732(1)"], "no minimum term of imprisonment"
        )

    elif (
        summary_minimum["jail"]["amount"]
        and int(summary_minimum["jail"]["amount"]) <= 90
    ):
        return standard_output(
            True, None, ["cc732(1)"], "minimum does not exceed 90 days"
        )

    elif (
        indictable_minimum["jail"]["amount"]
        and int(indictable_minimum["jail"]["amount"]) <= 90
    ):
        return standard_output(
            True, None, ["cc732(1)"], "minimum does not exceed 90 days"
        )

    else:
        return standard_output(
            False,
            None,
            ["cc732"],
            "mandatory minimum term of imprisonment exceeds 90 days",
        )


def check_suspended_sentence_available(
    summary_minimum: Dict[str, Dict[str, Union[int, str]]],
    indictable_minimum: Dict[str, Dict[str, Union[int, str]]],
) -> Dict[str, Union[bool, None, List[str], str]]:
    """
    A suspended sentence is available for any offence without a mandatory
    minimum and where the offender is sentenced to two years or less. The
    latter can be mapped out in a later version of the program, when we start
    to parse imposed sentences, rather than simply creating an offence grid.

    Args:
        summary_minimum (Dict): The minimum sentence for summary proceedings
        indictable_minimum (Dict): The minimum sentence for indictable proceedings

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether suspended sentence is available
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

    if summary_minimum["jail"]["amount"] or summary_minimum["fine"]["amount"]:
        return standard_output(False, None, ["cc731(1)"], "mandatory minimum sentence")

    elif indictable_minimum["jail"]["amount"] or indictable_minimum["fine"]["amount"]:
        return standard_output(False, None, ["cc731(1)"], "mandatory minimum sentence")

    else:
        return standard_output(
            True, None, ["cc731(1)"], "no mandatory minimum sentence"
        )


def check_prison_and_probation(
    mode: str, indictable_minimum: Dict[str, Dict[str, Union[int, str]]]
) -> Dict[str, Union[bool, None, List[str], str]]:
    """
    A suspended sentence is available for any offence that doesn't have a
    mandatory minimum exceeding two years. If the offence is hybrid,
    probation is available on summary conviction proceedings. If the offence
    is straight indictable, probation is available where the minimum term of
    imprisonment is less than two years.

    Args:
        mode (str): The mode of prosecution
        indictable_minimum (Dict): The minimum sentence for indictable proceedings

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether prison and probation is available
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
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


def check_fine_alone(
    summary_minimum: Dict[str, Dict[str, Union[int, str]]],
    indictable_minimum: Dict[str, Dict[str, Union[int, str]]],
) -> Dict[str, Union[bool, None, List[str], str]]:
    """
    Checks to see whether the offence has a mandatory minimum prison term. If
    so, a fine alone is not available. Otherwise, it is.

    Args:
        summary_minimum (Dict): The minimum sentence for summary proceedings
        indictable_minimum (Dict): The minimum sentence for indictable proceedings

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether fine alone is available
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

    fine_alone_available = {}

    if (
        summary_minimum["jail"]["amount"] == None
        or indictable_minimum["jail"]["amount"] == None
    ):
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


def check_fine_and_probation(
    indictable_minimum: Dict[str, Dict[str, Union[int, str]]]
) -> Dict[str, Union[bool, None, List[str], str]]:
    """
    The same rules apply to this check as to the check for prison and
    probation. If the offence has a mandatory minimum term of imprisonment that
    exceeds two years, probation is not available. Otherwise, it is.

    The function only checks for indictable offences, as summary maximums are
    all below two years.

    Args:
        indictable_minimum (Dict): The minimum sentence for indictable proceedings

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether fine and probation is available
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

    if int(indictable_minimum["jail"]["amount"]) == 0:
        return standard_output(
            True, None, ["cc732(1)"], "no minimum term of imprionment"
        )

    if int(indictable_minimum["jail"]["amount"]) < 730:
        return standard_output(True, None, ["cc732(1)"], None)

    else:
        return standard_output(
            False,
            None,
            ["cc732(1)"],
            "mandatory minimum term of imprisonment exceeds two years",
        )


def check_fine_probation_intermittent(
    summary_minimum: Dict[str, Dict[str, Union[int, str]]],
    indictable_minimum: Dict[str, Dict[str, Union[int, str]]],
) -> Dict[str, Union[bool, None, List[str], str]]:
    """
    Check to see whether the offence has a mandatory minimum term of
    imprisonment exceeding 90 days. If so, an intermittent sentence is not
    available. Otherwise, it is.

    Args:
        summary_minimum (Dict): The minimum sentence for summary proceedings
        indictable_minimum (Dict): The minimum sentence for indictable proceedings

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether fine, probation, and intermittent sentence is available
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

    fine_probation_intermittent_available = check_intermittent_available(
        summary_minimum, indictable_minimum
    )

    return fine_probation_intermittent_available


# Ancillary orders
def check_dna_designation(
    offence: List[str], mode: str, quantum: Dict[str, Dict[str, Union[int, str]]]
) -> Dict[str, Union[bool, None, List[str], str]]:
    """
    Check if the offence is a designated DNA offence.

    Args:
        offence (List[str]): A row from the CSV file containing offence data
        mode (str): The mode of prosecution
        quantum (Dict): The sentence for the offence

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether DNA designation is available
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

    if offence[0] in PRIMARY_DESIGNATED_DNA_OFFENCES:
        return standard_output(True, None, ["cc487.04"], "primary designated offence")

    elif offence[0] in SECONDARY_DESIGNATED_DNA_OFFENCES:
        return standard_output(True, None, ["cc487.04"], "secondary designated offence")

    elif (
        (mode == "indictable" or mode == "hybrid")
        and quantum["jail"]["unit"] == "years"
        and int(quantum["jail"]["amount"]) >= 5
    ):
        return standard_output(True, None, ["cc487.04"], "secondary designated offence")

    else:
        return standard_output(False, None, ["cc487.04"], "not a designated offence")


def check_soira(
    section: str, mode: str, indictable_maximum: Dict[str, Dict[str, Union[int, str]]]
) -> List[Dict[str, Union[bool, None, List[str], str]]]:
    """
    SOIRA orders are available when an offender is convicted of one or more of
    the designated offences. The duration of the order depends on several
    factors, including:
    - The mode the offence was prosecuted in;
    - The maximum term of imprisonment;
    - Whether the offender was convicted of multiple designated offences in the
    same proceeding; and
    - The offender's prior criminal record.


    Args:
        section (str): The section of the Criminal Code
        mode (str): The mode of prosecution
        indictable_maximum (Dict): The maximum sentence for indictable proceedings

    Returns:
        List[Dict]: A list of dictionaries containing:
            - available (bool): Whether SOIRA is available
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

    soira_list = []

    # Check to see whether the offence is a designated SOIRA offence
    if section in PRIMARY_SOIRA_OFFENCES_CURRENT:
        soira_list.append(
            standard_output(
                True,
                "primary",
                ["cc490.011[primary offence](a)"],
                "primary designated offence",
            )
        )

    elif section in SECONDARY_SOIRA_OFFENCES:
        soira_list.append(
            standard_output(
                True,
                "secondary",
                ["cc490.011[secondary offence](a)"],
                "secondary designated offence",
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
                "attempted designated offence",
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
                "conspiracy to commit designated offence",
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
            "not a designated offence",
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

    elif indictable_maximum and isinstance(indictable_maximum, dict) and "amount" in indictable_maximum:
        max_amount = int(indictable_maximum["amount"])
        
        if max_amount in [2, 5]:
            soira_list[0]["section"].append("cc490.011(2)(a)")
            soira_list[0]["duration"] = {
                "amount": 10,
                "unit": "years",
            }
        elif max_amount in [10, 14]:
            soira_list[0]["section"].append("cc490.011(2)(b)")
            soira_list[0]["duration"] = {
                "amount": 20,
                "unit": "years",
            }
        elif max_amount > 14:
            soira_list[0]["section"].append("cc490.011(2)(c)")
            soira_list[0]["duration"] = {
                "amount": "life",
                "unit": None,
            }
    # cc490.13(3) & (5) are implementable once we have data for an offender's
    # criminal record

    return soira_list


def check_proceeds_of_crime_forfeiture(
    section: str, mode: str
) -> List[Dict[str, Union[bool, None, List[str], str]]]:
    """
    Check if the offence is a proceeds of crime offence.

    Args:
        section (str): The section of the Criminal Code
        mode (str): The mode of prosecution

    Returns:
        List[Dict]: A list of dictionaries containing:
            - available (bool): Whether proceeds of crime forfeiture is available
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

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
                "strictly summary conviction offence",
            )
        )

        return proceeds_list

    elif section in PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_CRIMINAL_ORGANIZATION:
        proceeds_list.append(
            standard_output(
                True,
                None,
                ["cc462.37(2.02)(a)"],
                "particular circumstances — criminal organization offence",
            )
        )

    elif section in PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_CDSA:
        proceeds_list.append(
            standard_output(
                True,
                None,
                ["cc462.37(2.02)(b)"],
                "particular circumstances — CDSA offence",
            )
        )

    elif section in PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_CANNABIS:
        proceeds_list.append(
            standard_output(
                True,
                None,
                ["cc462.37(2.02)(c)"],
                "particular circumstances — cannabis offence",
            )
        )

    elif section in PROCEEDS_OF_CRIME_PARTICULAR_CIRCUMSTANCES_HUMAN_TRAFFICKING:
        proceeds_list.append(
            standard_output(
                True,
                None,
                ["cc462.37(2.02)(d)"],
                "particular circumstances — human trafficking offence",
            )
        )

    else:
        proceeds_list.append(
            standard_output(
                False,
                None,
                [
                    "cc462.3[designated offence]",
                    "cc462.37(1)",
                ],
                "offence prosecutable by indictment",
            )
        )

    return proceeds_list


def check_section_164_forfeiture_order(
    section: str,
) -> Dict[str, Union[bool, None, List[str], str]]:
    """
    Checks whether the offence is one of the enumerated offences for which a
    cc164.2 forfeiture order is required.

    Args:
        section (str): The section of the Criminal Code

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether section 164 forfeiture order is available
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

    if section in SECTION_161_FORFEITURE_ORDER_OFFENCES:
        return standard_output(True, None, ["cc164.2"], "enumerated offence")


def check_section_109_weapons_prohibition(
    offence: List[str],
) -> Dict[str, Union[bool, None, List[str], str]]:
    """
    Checks if the offence fits the criteria for a section 109 prohibition
    order. Some of the preconditions are case-specific, and thus are out of
    scope for this program at this time. Once the program starts to integrate
    NLP, we can start to parse the facts of the case to determine whether the
    offence meets the criteria for a section 109 order. Once this is possible,
    we should also be able to check for section 110 orders, which are almost
    entirely fact-specific.

    Args:
        offence (List[str]): A row from the CSV file containing offence data

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether section 109 weapons prohibition is available
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

    return standard_output(False, None, ["cc109"], "not a firearms offence")


def check_section_515_mandatory_weapons_prohibition(section: str):
    pass
