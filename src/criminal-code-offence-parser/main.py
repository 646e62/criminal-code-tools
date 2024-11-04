import csv

from parser import (
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


def parse_offence(offence, mode="summary"):
    """
    Parse the offence data for a given offence.
    """

    # Remove any whitespace from the offence input and convert to lowercase
    offence = offence.strip().lower()
    parsed_offence = {}

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
            parsed_offence["section"] = row[0]
            parsed_offence["description"] = row[1]
            parsed_offence["mode"] = mode
            parsed_offence["summary_minimum"] = summary_minimum_quantum
            parsed_offence["summary_maximum"] = summary_maximum_quantum
            parsed_offence["indictable_minimum"] = indictable_minimum_quantum
            parsed_offence["indictable_maximum"] = indictable_maximum_quantum
            parsed_offence["absolute_jurisdiction"] = check_absolute_jurisdiction_offence(
                row[0]
            )

            # Procedural rights
            parsed_offence["prelim_available"] = prelim_available
            parsed_offence["release_by_superior_court_judge"] = section_469_offence

            # Sentencing options
            parsed_offence["cso_available"] = check_cso_availablity(
                row[0],
                summary_minimum_quantum,
                indictable_minimum_quantum,
                indictable_maximum_quantum,
                mode,
            )
            parsed_offence["intermittent_available"] = check_intermittent_available(
                summary_minimum_quantum, indictable_minimum_quantum
            )
            parsed_offence["suspended_sentence_available"] = (
                check_suspended_sentence_available(
                    summary_minimum_quantum, indictable_minimum_quantum
                )
            )
            parsed_offence["discharge_available"] = check_discharge_available(
                summary_minimum_quantum,
                indictable_minimum_quantum,
                indictable_maximum_quantum,
            )

            parsed_offence["prison_and_probation_available"] = check_prison_and_probation(
                mode,
                indictable_minimum_quantum,
            )

            parsed_offence["fine_alone"] = check_fine_alone(
                indictable_minimum_quantum,
                indictable_minimum_quantum,
            )

            parsed_offence["fine_and_probation"] = check_fine_and_probation(
                indictable_minimum_quantum,
            )

            # Ancillary orders
            parsed_offence["dna_designation"] = check_dna_designation(
                row, mode, indictable_maximum_quantum
            )
            parsed_offence["soira"] = check_soira(
                row[0], mode, indictable_maximum_quantum
            )
            parsed_offence["proceeds_of_crime_forfeiture"] = check_proceeds_of_crime_forfeiture(
                row[0], mode
            )
            parsed_offence["section_164.2_forfeiture_order"] = check_section_164_forfeiture_order(
                row[0]
            )

            # Collateral consequences
            parsed_offence["inadmissibility"] = check_inadmissibility(
                row[0], mode, indictable_maximum_quantum["amount"]
            )

            return parsed_offence

    # Return None if the offence is not found
    return None
