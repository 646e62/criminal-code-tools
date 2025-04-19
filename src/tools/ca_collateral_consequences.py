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


def check_inadmissibility(section, mode, indictable_maximum, citizenship_status):
    """
    Checks to see whether the offence renders the defendant liable for IRPA
    consequences.
    """
    # print(f"[check_inadmissibility] Citizenship status received: {citizenship_status}")
    inadmissibilty_list = []

    # Determine whether this check is still necessary, given the changes in 
    # v0.0.5
    try:
        indictable_maximum = int(indictable_maximum)
    except:
        indictable_maximum = 0

    if citizenship_status == "canadian":
        return [standard_output(
            False,
            None,
            ["irpa_34(1)"],
            {"notes": "no admissibility consequences for citizens"}
        )]

    if section in TERRORISM_OFFENCES:
        inadmissibilty_list.append(
            standard_output(
                True,
                "both",
                ["irpa_34(1)"],
                "security"
            )
        )

    if section == "cc_240.1":
        inadmissibilty_list.append(
            standard_output(
                True,
                "both",
                ["irpa_35(1)(c.1)"],
                "human or international rights violations",
            )
        )
        inadmissibilty_list.append(
            standard_output(
                True,
                "foreign national",
                ["irpa_35(1)(c.1)"],
                "human or international rights violations",
            )
        )

    if indictable_maximum >= 10:
        inadmissibilty_list.append(
            standard_output(
                True,
                "both",  # indicates both permanent residents and foreign nationals
                ["irpa_36(1)"],
                "serious criminality"
            )
        )

    if mode == "indictable" or (mode == "hybrid" and indictable_maximum > 0):
        # Only add criminality if we haven't already added serious criminality
        if not any(result["notes"] == "serious criminality" for result in inadmissibilty_list):
            inadmissibilty_list.append(
                standard_output(
                    True,
                    "foreign national",
                    ["irpa_36(2)"],
                    "criminality"
                )
            )
    elif mode == "summary":
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
