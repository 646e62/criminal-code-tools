UNAVAILABLE_COURT_DECISIONS = [
    "2024oncj629", "2024oncj637", "2024canlii119277", "2024canlii115862", 
    "2024canlii115109", "2024canlii116228", "2024canlii112388", 
    "2024canlii110263", "2024canlii108836", "2024canlii100969",
    "2024canlii100813", "2024canlii98985", "2024canlii98439", 
    "2024canlii98004", "2024canlii93152", "2024canlii93149",
    "2024canlii92654", "2024canlii90910", "2024canlii77399",
    "2024canlii27145", "2024canlii344", "2024canlii343", "2024abcj58",
    "2024canlii122870",

]

LATEST_CASE_CHECKED = {
    "bcpc": "2024bcpc230",
    "abcj": "2024abcj261",
    "skpc": "2024skpc40",
    "mbpc": "2024mbpc96",
    "oncj": "2024oncj645",
    "qccq": "2024qccq7422",
    "nbpc": "2024nbpc8",
    "nspc": "2024nspc50",
    "pepc": "2009canlii101169",
    "nlpc": "2024canlii123250",
    "yktc": "2024yktc42",
    "nttc": "2024nwttc7",
    "nucj": "2024nucj34",
}

# Stores cases where the database entry doesn't completely match the decision's
# logic. The key is the case number, and the value is a tuple where the first
# item is the reason for the discrepancy and the second is a description of how
# the discrepancy was resolved in the database entry.

PROBLEM_CASES = {
    "2024bcpc114": (
        "uncalculated totality in the original decision", 
        "manually adjusted for totality by running sentences concurrent"
        ),
    "2024bcpc82": (
        "offence date not included, unclear if the court ordered probation",
        "used the decision date as the offence date, assumed no probation"
    ),
    "2024bcpc37": (
        "offence date unclear",
        "inferred between dates from the decision text (para 4)"
    ),
    "2024bcpc56": (
        "offence date not included",
        "used the decision date as the offence date"
    ),
}
