import csv
from cc_rules_current import (
    check_offence_type,
    check_prelim_available,
    check_section_469_offence,
    parse_quantum,
    check_cso_availablity,
    check_inadmissibility,
    check_dna_designation,
    check_discharge_available,
    check_intermittent_available,
    check_suspended_sentence_available,
    check_soira,
    check_proceeds_of_crime_forfeiture,
    check_absolute_jurisdiction_offence,
    check_section_164_forfeiture_order,
    check_prison_and_probation,
    check_fine_alone,
    check_fine_and_probation,
)

# Open the CSV file
with open("data/cc-offences-2024-09-16.csv") as csvfile:
    csvreader = csv.reader(csvfile)
    data = list(csvreader)


def parse_offence(
    offence,
    mode="summary",
    full=False,
    procedure=False,
    ancillary_orders=False,
    sentencing=False,
    collateral_consequences=False,
):
    """
    Parse the offence data for a given offence.

    By default, returns only `offence_data`. Additional categories can be added by
    setting `procedure`, `ancillary_orders`, `sentencing`, or `collateral_consequences` to True.
    Setting `full` to True will return all categories.
    """

    # Remove any whitespace from the offence input and convert to lowercase
    offence = offence.strip().lower()
    parsed_offence = {
        "offence_data": {},
    }

    # Find the offence in the data
    for row in data:
        if row[0] == offence:

            # Create the offence variables
            mode = check_offence_type(row)
            prelim_available = check_prelim_available(row[3])
            indictable_minimum_quantum = parse_quantum(row[2])
            indictable_maximum_quantum = parse_quantum(row[3])
            summary_minimum_quantum = parse_quantum(row[4])
            summary_maximum_quantum = parse_quantum(row[5])
            section_469_offence = check_section_469_offence(row[0])

            # Offence data
            parsed_offence["offence_data"]["section"] = row[0]
            parsed_offence["offence_data"]["description"] = row[1]
            parsed_offence["offence_data"]["mode"] = mode
            parsed_offence["offence_data"]["summary_minimum"] = summary_minimum_quantum
            parsed_offence["offence_data"]["summary_maximum"] = summary_maximum_quantum
            parsed_offence["offence_data"][
                "indictable_minimum"
            ] = indictable_minimum_quantum
            parsed_offence["offence_data"][
                "indictable_maximum"
            ] = indictable_maximum_quantum
            parsed_offence["offence_data"]["absolute_jurisdiction"] = (
                check_absolute_jurisdiction_offence(row[0])
            )

            # Add procedure data if requested or if full flag is set
            if full or procedure:
                parsed_offence["procedure"] = {}
                parsed_offence["procedure"]["prelim_available"] = prelim_available
                parsed_offence["procedure"][
                    "release_by_superior_court_judge"
                ] = section_469_offence

            # Add sentencing options if requested or if full flag is set
            if full or sentencing:
                parsed_offence["sentencing"] = {}
                parsed_offence["sentencing"]["cso_available"] = check_cso_availablity(
                    row[0],
                    summary_minimum_quantum,
                    indictable_minimum_quantum,
                    indictable_maximum_quantum,
                    mode,
                )
                parsed_offence["sentencing"]["intermittent_available"] = (
                    check_intermittent_available(
                        summary_minimum_quantum, indictable_minimum_quantum
                    )
                )
                parsed_offence["sentencing"]["suspended_sentence_available"] = (
                    check_suspended_sentence_available(
                        summary_minimum_quantum, indictable_minimum_quantum
                    )
                )
                parsed_offence["sentencing"]["discharge_available"] = (
                    check_discharge_available(
                        summary_minimum_quantum,
                        indictable_minimum_quantum,
                        indictable_maximum_quantum,
                    )
                )

                parsed_offence["sentencing"]["prison_and_probation_available"] = (
                    check_prison_and_probation(
                        mode,
                        indictable_minimum_quantum,
                    )
                )

                parsed_offence["sentencing"]["fine_alone"] = check_fine_alone(
                    indictable_minimum_quantum,
                    indictable_minimum_quantum,
                )

                parsed_offence["sentencing"]["fine_and_probation"] = (
                    check_fine_and_probation(
                        indictable_minimum_quantum,
                    )
                )

            # Add ancillary orders if requested or if full flag is set
            if full or ancillary_orders:
                parsed_offence["ancillary_orders"] = {}
                parsed_offence["ancillary_orders"]["dna_designation"] = (
                    check_dna_designation(row, mode, indictable_maximum_quantum)
                )
                parsed_offence["ancillary_orders"]["soira"] = check_soira(
                    row[0], mode, indictable_maximum_quantum
                )
                parsed_offence["ancillary_orders"]["proceeds_of_crime_forfeiture"] = (
                    check_proceeds_of_crime_forfeiture(row[0], mode)
                )
                parsed_offence["ancillary_orders"]["section_164.2_forfeiture_order"] = (
                    check_section_164_forfeiture_order(row[0])
                )

            # Add collateral consequences if requested or if full flag is set
            if full or collateral_consequences:
                parsed_offence["collateral_consequences"] = {}
                parsed_offence["collateral_consequences"]["inadmissibility"] = (
                    check_inadmissibility(
                        row[0], mode, indictable_maximum_quantum["amount"]
                    )
                )

            return parsed_offence

    # Return None if the offence is not found
    return None
