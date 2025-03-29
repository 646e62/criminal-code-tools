#############################
##                         ##
## Collateral consequences ##
##                         ##
#############################

from constants import (
    TERRORISM_OFFENCES,
)

from utils import (
    standard_output,
)


def check_inadmissibility(section, mode, indictable_maximum):
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
                "permanent resident",
                ["irpa36(1)"],
                "serious criminality"
            )
        )
        inadmissibilty_list.append(
            standard_output(
                True,
                "foreign national",
                ["irpa36(1)"],
                "serious criminality"
            )
        )

    if mode == "hybrid" or mode == "indictable":
        inadmissibilty_list.append(
            standard_output(
                True,
                "foreign national",
                ["irpa36(2)"],
                "criminality"
            )
        )

    return inadmissibilty_list