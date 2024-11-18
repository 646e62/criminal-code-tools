# Saskatchewan Firearms Act, SS 2023, c 8

from utils import (
    standard_output,
)

from constants import(
    SK_FIREARMS_ACT_SUSPENSION_OFFENCES,
)

def check_firearms_act(section):
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