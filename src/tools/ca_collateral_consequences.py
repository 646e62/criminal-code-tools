#############################
##                         ##
## Collateral consequences ##
##                         ##
#############################

from .constants import (
    TERRORISM_OFFENCES,
)

from .utils import (
    standard_output,
)


def check_inadmissibility(section, mode, indictable_maximum):
    print(mode)
    """
    Checks to see whether the offence renders the defendant liable for IRPA
    consequences.
    """
    inadmissibilty_list = []

    # Determine whether this check is still necessary, given the changes in 
    # v0.0.5
    try:
        indictable_maximum = int(indictable_maximum)
    except:
        indictable_maximum = 0

    if section in TERRORISM_OFFENCES:
        inadmissibilty_list.append(
            standard_output(
                True,
                "permanent resident",
                ["irpa34(1)"],
                "security"
            )
        )

    if section == "cc240.1":
        inadmissibilty_list.append(
            standard_output(
                True,
                "permanent resident",
                ["irpa35(1)(c.1)"],
                "human or international rights violations",
            )
        )
        inadmissibilty_list.append(
            standard_output(
                True,
                "foreign national",
                ["irpa35(1)(c.1)"],
                "human or international rights violations",
            )
        )

    if indictable_maximum >= 10:
        inadmissibilty_list.append(
            standard_output(
                True,
                "both",  # indicates both permanent residents and foreign nationals
                ["irpa36(1)"],
                "serious criminality"
            )
        )

    if mode == "hybrid" or mode == "indictable":
        # Only add criminality if we haven't already added serious criminality
        print("Hit")
        if not any(result["notes"] == "serious criminality" for result in inadmissibilty_list):
            inadmissibilty_list.append(
                standard_output(
                    True,
                    "foreign national",
                    ["irpa36(2)"],
                    "criminality"
                )
            )

    if mode == "summary":
        inadmissibilty_list.append(
            standard_output(
                False,
                None,
                None,
                None
            )
        )

    # If no consequences were found, add a "none" result
    if not inadmissibilty_list:
        inadmissibilty_list.append(
            standard_output(
                False,
                None,
                [],
                "none"
            )
        )

    return inadmissibilty_list
