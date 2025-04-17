import csv
from cc_rules_current import (
    check_offence_type,
    check_prelim_available,
    check_section_469_offence,
    check_cso_availablity,
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

from ca_collateral_consequences import (
    check_inadmissibility,
)

from utils import (
    parse_quantum,
)

from map import (
    CC_DISAMBIGUATION,
    CC_GRADUATED_OFFENCES
)

from constants import(
    STATUTE_CODES
)

# Constants
CSV_FILE_PATH = "data/cc-offences-2024-09-16.csv"
VALID_MODES = ["summary", "indictable"]

# Global variables
data = None

def initialize():
    """Initialize global data by reading the CSV file."""
    global data
    try:
        # Open the CSV file
        with open(CSV_FILE_PATH) as csvfile:
            csvreader = csv.reader(csvfile)
            data = list(csvreader)
        return True
    except FileNotFoundError:
        print(f"Error: Could not find CSV file at {CSV_FILE_PATH}")
        return False
    except csv.Error as e:
        print(f"Error reading CSV file: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def generate_basic_offence_details(row: list) -> dict:
    """
    Generates the basic offence details that every function call should include.
    
    Args:
        row (list): A row from the CSV file containing offence data.
            [0] = statutory code and section number
            [1] = offence title
            [2] = indictable minimum
            [3] = indictable maximum
            [4] = summary minimum
            [5] = summary maximum
    
    Returns:
        dict: A dictionary containing basic offence details including:
            - section: statutory code and section number
            - description: offence title
            - mode: type of offence (summary/indictable/hybrid)
            - summary_minimum/maximum: quantum for summary proceedings
            - indictable_minimum/maximum: quantum for indictable proceedings
    """
    offence_data = {}

    # Create the offence variables
    mode = check_offence_type(row)
    indictable_minimum_quantum = parse_quantum(row[2])
    indictable_maximum_quantum = parse_quantum(row[3])
    summary_minimum_quantum = parse_quantum(row[4])
    summary_maximum_quantum = parse_quantum(row[5])

    # Offence data
    offence_data["section"] = row[0]
    offence_data["description"] = row[1]
    offence_data["mode"] = mode
    offence_data["summary_minimum"] = summary_minimum_quantum
    offence_data["summary_maximum"] = summary_maximum_quantum
    offence_data["indictable_minimum"] = indictable_minimum_quantum
    offence_data["indictable_maximum"] = indictable_maximum_quantum

    return offence_data


def generate_procedure_details(row):
    """
    Generates basic information about procedural rights or requirements for 
    certain offences.
    """
    procedure_data = {}

    # Create the offence variables
    prelim_available = check_prelim_available(row[3])
    section_469_offence = check_section_469_offence(row[0])

    procedure_data["prelim_available"] = prelim_available
    procedure_data["absolute_jurisdiction"] = (
        check_absolute_jurisdiction_offence(row[0])
    )
    procedure_data["release_by_superior_court_judge"] = section_469_offence

    return procedure_data


def generate_sentencing_details(row):
    """
    Generates basic information about sentencing options for certain offences.
    """
    sentencing_data = {}

    # Create the offence variables
    mode = check_offence_type(row)
    indictable_minimum_quantum = parse_quantum(row[2])
    indictable_maximum_quantum = parse_quantum(row[3])
    summary_minimum_quantum = parse_quantum(row[4])

    sentencing_data["cso_available"] = check_cso_availablity(
        row[0],
        summary_minimum_quantum,
        indictable_minimum_quantum,
        indictable_maximum_quantum,
        mode,
    )
    sentencing_data["intermittent_available"] = check_intermittent_available(
        summary_minimum_quantum, indictable_minimum_quantum
    )
    sentencing_data["suspended_sentence_available"] = check_suspended_sentence_available(
        summary_minimum_quantum, indictable_minimum_quantum
    )
    sentencing_data["discharge_available"] = check_discharge_available(
        summary_minimum_quantum, 
        indictable_minimum_quantum, 
        indictable_maximum_quantum
    )
    sentencing_data["prison_and_probation_available"] = check_prison_and_probation(
        mode,
        indictable_minimum_quantum,
    )
    sentencing_data["fine_alone"] = check_fine_alone(
        indictable_minimum_quantum,
        indictable_minimum_quantum,
    )
    sentencing_data["fine_and_probation"] = check_fine_and_probation(
        indictable_minimum_quantum,
    )

    return sentencing_data


def generate_ancillary_order_details(row):
    """
    Generates basic information about ancillary orders for certain offences.
    """
    ancillary_order_data = {}

    mode = check_offence_type(row)
    indictable_maximum_quantum = parse_quantum(row[3])

    ancillary_order_data["dna_designation"] = check_dna_designation(row, mode, indictable_maximum_quantum)
    ancillary_order_data["soira"] = check_soira(row[0], mode, indictable_maximum_quantum)
    ancillary_order_data["proceeds_of_crime_forfeiture"] = check_proceeds_of_crime_forfeiture(row[0], mode)
    ancillary_order_data["section_164.2_forfeiture_order"] = check_section_164_forfeiture_order(row[0])

    return ancillary_order_data


def generate_collateral_consequence_details(row):
    """
    Generates basic information about collateral consequences for certain offences.
    """
    collateral_consequence_data = {}

    mode = check_offence_type(row)
    indictable_maximum_quantum = parse_quantum(row[3])

    collateral_consequence_data["inadmissibility"] = check_inadmissibility(
        row[0], mode, indictable_maximum_quantum["jail"]["amount"]
    )

    return collateral_consequence_data


def parse_offence(
        offence: str,
        mode: str = "summary",
        full: bool = False,
        procedure: bool = False,
        ancillary_orders: bool = False,
        sentencing: bool = False,
        collateral_consequences: bool = False,
) -> list:
    """
    Parse the offence data for a given offence.

    Args:
        offence (str): The offence code to parse
        mode (str): The mode of proceeding ("summary" or "indictable")
        full (bool): If True, returns all categories of information
        procedure (bool): If True, includes procedural details
        ancillary_orders (bool): If True, includes ancillary order details
        sentencing (bool): If True, includes sentencing details
        collateral_consequences (bool): If True, includes collateral consequence details

    Returns:
        list: A list of dictionaries containing the requested offence information

    Raises:
        ValueError: If mode is not "summary" or "indictable"
        KeyError: If offence code is not found
        RuntimeError: If data hasn't been initialized
    """
    global data
    if data is None:
        if not initialize():
            raise RuntimeError("Failed to initialize data. Please check the CSV file.")

    # Input validation
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid mode: {mode}. Must be one of {VALID_MODES}")

    # If full is True, set all detail flags to True
    if full:
        procedure = ancillary_orders = sentencing = collateral_consequences = True

    def offence_parser(row):
        parsed_offence = {
            "offence_data": generate_basic_offence_details(row)
        }

        if procedure:
            parsed_offence["procedure"] = generate_procedure_details(row)

        if sentencing:
            parsed_offence["sentencing"] = generate_sentencing_details(row)

        if ancillary_orders:
            parsed_offence["ancillary_orders"] = generate_ancillary_order_details(row)

        if collateral_consequences:
            parsed_offence["collateral_consequences"] = generate_collateral_consequence_details(row)

        return parsed_offence

    offence = offence.strip().lower()
    parsed_offence_list = []
    
    # Check to see if the offence is in the data. If not, check if it is a key in the
    # disambiguation or graduated offences dictionaries. Offences in these dictionaries
    # will be in list format. The program will need to cycle through each offence in the
    # list and add the results of the parser to the parsed_offence_list.

    for row in data:
        if row[0] == offence:
            parsed_offence_list.append(offence_parser(row))
            return parsed_offence_list
        
    if offence in CC_DISAMBIGUATION:
        for disambiguated_offence in CC_DISAMBIGUATION[offence]:
            for row in data:
                if row[0] == disambiguated_offence:
                    parsed_offence_list.append(offence_parser(row))
        return parsed_offence_list
    
    if offence in CC_GRADUATED_OFFENCES:
        for graduated_offence in CC_GRADUATED_OFFENCES[offence]:
            for row in data:
                if row[0] == graduated_offence:
                    parsed_offence_list.append(offence_parser(row))
        return parsed_offence_list

    raise KeyError(f"Offence code '{offence}' not found")


def report(offence_code: str) -> None:
    """
    Generates a comprehensive human-readable report from the offence parser data.
    
    Args:
        offence_code (str): The offence code to generate a report for (e.g., "cc_266")
        
    Raises:
        RuntimeError: If the data hasn't been initialized
    """
    global data
    if data is None:
        if not initialize():
            raise RuntimeError("Failed to initialize data. Please check the CSV file.")
    
    offence_list = parse_offence(offence_code, full=True)

    for offence in offence_list:
        # Extract basic information
        statute_code = offence["offence_data"]["section"].split("_")[0]
        section_number = offence["offence_data"]["section"].split("_")[1]
        statute_name = STATUTE_CODES[statute_code]["name"]
        offence_name = offence["offence_data"]["description"]
        mode = offence["offence_data"]["mode"]

        # Print header
        print("\n" + "=" * 80)
        print(f"{statute_name} s. {section_number} — {offence_name.title()}")
        print("=" * 80 + "\n")

        # Offence Summary
        print("OFFENCE SUMMARY")
        print("-" * 50)
        print(f"Mode: {mode.title()}")
        if mode in ["summary", "hybrid"]:
            print(f"Summary Maximum: {format_quantum(offence['offence_data']['summary_maximum'])}")
            print(f"Summary Minimum: {format_quantum(offence['offence_data']['summary_minimum'])}")
        if mode in ["indictable", "hybrid"]:
            print(f"Indictable Maximum: {format_quantum(offence['offence_data']['indictable_maximum'])}")
            print(f"Indictable Minimum: {format_quantum(offence['offence_data']['indictable_minimum'])}")
        print("\n")

        # Basic Information
        print("BASIC INFORMATION")
        print("-" * 50)
        print(f"Mode of Proceeding: {mode.title()}")

        # Sentencing Ranges
        print("\nSENTENCING RANGES")
        print("-" * 50)
        
        def format_quantum(quantum):
            if not quantum:
                return "None"
            fine = quantum.get("fine", {})
            jail = quantum.get("jail", {})
            parts = []
            if fine.get("amount"):
                parts.append(f"${fine['amount']} {fine['unit']}")
            if jail.get("amount"):
                if jail.get("unit") == "years" and int(jail["amount"]) == 255:
                    parts.append("life")
                else:
                    parts.append(f"{jail['amount']} {jail['unit']}")
            return " and ".join(parts) if parts else "None"

        # Summary Proceedings
        if mode in ["summary", "hybrid"]:
            print("\nSummary Proceedings:")
            print(f"  Minimum: {format_quantum(offence['offence_data']['summary_minimum'])}")
            print(f"  Maximum: {format_quantum(offence['offence_data']['summary_maximum'])}")

        # Indictable Proceedings
        if mode in ["indictable", "hybrid"]:
            print("\nIndictable Proceedings:")
            print(f"  Minimum: {format_quantum(offence['offence_data']['indictable_minimum'])}")
            print(f"  Maximum: {format_quantum(offence['offence_data']['indictable_maximum'])}")

        # Procedure
        if "procedure" in offence:
            print("\nPROCEDURAL INFORMATION")
            print("-" * 50)
            
            # Preliminary Inquiry
            if "prelim_available" in offence["procedure"]:
                prelim = offence["procedure"]["prelim_available"]
                if isinstance(prelim, dict):
                    status = prelim.get('status', {})
                    if isinstance(status, tuple):
                        status = status[0] if status else {}
                    avail = status.get('available', False)
                    print(f"Preliminary Inquiry Available: {avail}")
                    if prelim.get('notes'):
                        print(f"  Reason: {prelim['notes']}")

            # Absolute Jurisdiction
            if "absolute_jurisdiction" in offence["procedure"]:
                abs_juris = offence["procedure"]["absolute_jurisdiction"]
                if abs_juris and isinstance(abs_juris, list) and abs_juris[0]:
                    status = abs_juris[0].get('status', {})
                    if isinstance(status, tuple):
                        status = status[0] if status else {}
                    avail = status.get('absolute_jurisdiction', False)
                    print(f"Absolute Jurisdiction: {avail}")
                    if abs_juris[0].get('notes'):
                        print(f"  Reason: {abs_juris[0]['notes']}")

            # Superior Court Judge Release
            if "release_by_superior_court_judge" in offence["procedure"]:
                scj_release = offence["procedure"]["release_by_superior_court_judge"]
                if isinstance(scj_release, dict):
                    status_dict = scj_release.get('status', {})
                    avail = status_dict.get('available', False)
                    print(f"Superior Court Judge Release Required: {'Required' if avail else 'Not Required'}")
                    if scj_release.get('notes'):
                        print(f"  Reason: {scj_release['notes']}")
                    if scj_release.get('sections'):
                        print(f"  Sections: {', '.join(scj_release['sections'])}")

        # Sentencing Options
        if "sentencing" in offence:
            print("\nSENTENCING OPTIONS")
            print("-" * 50)
            
            sent = offence.get("sentencing", {})
            options = [
                ("Conditional Sentence", sent.get("cso_available")),
                ("Intermittent Sentence", sent.get("intermittent_available")),
                ("Suspended Sentence", sent.get("suspended_sentence_available")),
                ("Discharge", sent.get("discharge_available")),
                ("Prison and Probation", sent.get("prison_and_probation_available")),
                ("Fine Alone", sent.get("fine_alone")),
                ("Fine and Probation", sent.get("fine_and_probation"))
            ]
            
            for option, status in options:
                if status:
                    # Handle tuple status
                    if isinstance(status, tuple):
                        status_dict = status[0] if status else {}
                        if isinstance(status_dict, dict):
                            avail = status_dict.get('available', False)
                            print(f"{option}: {'Available' if avail else 'Not Available'}")
                            if status_dict.get('notes'):
                                print(f"  Reason: {status_dict['notes']}")
                    # Handle dictionary status
                    elif isinstance(status, dict):
                        status_dict = status.get('status', {})
                        if isinstance(status_dict, dict):
                            avail = status_dict.get('available', False)
                            print(f"{option}: {'Available' if avail else 'Not Available'}")
                            if status.get('notes'):
                                print(f"  Reason: {status['notes']}")

        # Ancillary Orders
        if "ancillary_orders" in offence:
            print("\nANCILLARY ORDERS")
            print("-" * 50)
            
            anc = offence.get("ancillary_orders", {})
            
            # DNA Orders
            dna = anc.get("dna_designation", {})
            if dna:
                status = dna.get('status', {})
                if isinstance(status, tuple):
                    status = status[0] if status else {}
                avail = status.get('available', False)
                print(f"DNA Order: {'Available' if avail else 'Not Available'}")
                if dna.get("notes"):
                    print(f"  Reason: {dna['notes']}")

            # SOIRA Orders
            soira_list = anc.get("soira", [])
            if soira_list and isinstance(soira_list, list):
                soira = soira_list[0]
                if isinstance(soira, dict):
                    status = soira.get('status', {})
                    avail = status.get('available', False) if isinstance(status, dict) else False
                    print(f"SOIRA Registration: {'Available' if avail else 'Not Available'}")
                    if avail:
                        duration = soira.get("duration", {})
                        if duration and duration.get('amount'):
                            if duration.get('amount') == "life":
                                print("  Duration: Life")
                            else:
                                print(f"  Duration: {duration.get('amount')} {duration.get('unit', '')}")
                        if soira.get("sections"):
                            print(f"  Sections: {', '.join(soira['sections'])}")
                        if soira.get("notes"):
                            print(f"  Reason: {soira['notes']}")

            # Proceeds of Crime
            poc = anc.get("proceeds_of_crime_forfeiture", {})
            if poc:
                if isinstance(poc, dict):
                    avail = poc.get('available', False)
                    print(f"Proceeds of Crime Forfeiture: {'Available' if avail else 'Not Available'}")
                    if poc.get('notes'):
                        print(f"  Reason: {poc['notes']}")

            # Section 164.2 Forfeiture
            s164_list = anc.get("section_164.2_forfeiture_order", [])
            if s164_list and isinstance(s164_list, list):
                s164 = s164_list[0]
                if isinstance(s164, dict):
                    print("Section 164.2 Forfeiture Order Available")
                    if s164.get("notes"):
                        print(f"  Reason: {s164['notes']}")

        # Collateral Consequences
        if "collateral_consequences" in offence:
            print("\nCOLLATERAL CONSEQUENCES")
            print("-" * 50)
            
            collateral = offence["collateral_consequences"]
            
            # Immigration Status
            inadmissibility = collateral.get("inadmissibility", [])
            if inadmissibility and isinstance(inadmissibility, list):
                for item in inadmissibility:
                    if isinstance(item, dict):
                        # Extract status information
                        if isinstance(item.get('status'), dict):
                            avail = item['status'].get('available', False)
                            status_notes = item['status'].get('notes')
                            print(f"Immigration Status: {'Applicable' if avail else 'Not Applicable'}")
                            if status_notes:
                                print(f"  Status Reason: {status_notes}")
                        else:
                            print(f"Immigration Status: {item.get('status', 'Unknown')}")
                        
                        # Extract section information
                        section = item.get('section', [])
                        if isinstance(section, list):
                            section = ', '.join(section)
                        if section:
                            print(f"  Section: {section}")
                        
                        # Extract notes
                        if item.get('notes'):
                            print(f"  Reason: {item['notes']}")

        print("\n" + "=" * 80 + "\n")


def main():
    """Main function to handle CSV processing and error handling."""
    initialize()

if __name__ == "__main__":
    main()
