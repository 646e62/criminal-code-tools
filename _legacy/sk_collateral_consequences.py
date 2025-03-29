# Saskatchewan Firearms Act, SS 2023, c 8

from utils import (
    standard_output,
)

from constants import(
    SK_FIREARMS_ACT_SUSPENSION_OFFENCES,
)

def check_firearms_act(section):
    """
    Check if the offence is a firearms act suspension offence.

    Args:
        section (str): The section of the Criminal Code

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether the offence is a firearms act suspension offence
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

    if section in SK_FIREARMS_ACT_SUSPENSION_OFFENCES:
        return standard_output(
            True,
            None,
            ["sk-firarms-act_3-2(1)"],
            "listed offence"
        )
    else:
        return standard_output(
            False,
            None,
            ["sk-firarms-act_3-2(1)"],
            "not a listed offence"
        )

def commercial_vehicle_drivers_record_keeping_regulations(section):
    """
    Check if the offence is a commercial vehicle drivers record keeping regulations
    offence.

    Args:
        section (str): The section of the Criminal Code

    Returns:
        Dict: A dictionary containing:
            - available (bool): Whether the offence is a commercial vehicle drivers record keeping regulations offence
            - quantum (Optional[str]): The quantum of sentence, if applicable
            - sections (List[str]): Relevant Criminal Code sections
            - explanation (str): Explanation of the determination
    """

    pass