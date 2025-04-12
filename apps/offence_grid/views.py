from django.shortcuts import render
import pandas as pd
import sys
import re
from pathlib import Path

# Add src to Python path for importing tools
src_path = Path(__file__).resolve().parent.parent.parent / 'src'
sys.path.append(str(src_path))

from tools import ca_collateral_consequences
from tools.cc_rules_current import (
    check_discharge_available,
    check_cso_availablity,
    check_intermittent_available,
    check_suspended_sentence_available,
    check_dna_designation,
    check_soira,
    check_section_109_weapons_prohibition,
)

def format_section(section):
    """Format section numbers for display by replacing prefix with § symbol."""
    if not section:
        return section
    # Replace any prefix (like cc_, ycja_, cdsa_) and underscore with "§ "
    return re.sub(r'^[a-z]+_', '§ ', section)

def load_offences():
    """Load offences from the CSV file."""
    csv_path = src_path / 'data/offence/cc-offences-2024-09-16.csv'
    df = pd.read_csv(csv_path)
    return [(row['section'], format_section(row['section']), row['offence_name'], 
             row['maximum_indictable'], row['maximum_sc'],
             row['minimum_indictable'], row['minimum_sc']) 
            for _, row in df.iterrows()]

def parse_minimum(min_value):
    """Parse minimum sentence value into a dictionary format."""
    empty_result = {
        "jail": {"amount": 0, "unit": None},
        "fine": {"amount": 0, "unit": None}
    }
    
    if pd.isna(min_value) or not min_value:
        return empty_result
    
    match = re.match(r'(\d+)([dmy])', min_value)
    if match:
        amount, unit = match.groups()
        unit_map = {'d': 'days', 'm': 'months', 'y': 'years'}
        return {
            "jail": {"amount": int(amount), "unit": unit_map[unit]},
            "fine": {"amount": 0, "unit": None}
        }
    return empty_result

def parse_maximum(max_value):
    """Parse maximum sentence value into a dictionary format."""
    empty_result = {
        "jail": {"amount": 0, "unit": None},
        "fine": {"amount": 0, "unit": None}
    }
    
    if pd.isna(max_value) or not max_value:
        return empty_result
    if isinstance(max_value, str) and max_value.endswith('y'):
        return {
            "jail": {"amount": int(max_value.rstrip('y')), "unit": "years"},
            "fine": {"amount": 0, "unit": None}
        }
    return empty_result

def get_collateral_consequences(section, max_indictable, max_sc, min_indictable, min_sc):
    """Get collateral consequences for an offence."""
    # Parse the maximum and minimum sentences
    indictable_maximum = parse_maximum(max_indictable)
    max_years = indictable_maximum["jail"]["amount"]
    
    # Determine mode based on maximum sentences
    mode = "summary" if pd.isna(max_indictable) and not pd.isna(max_sc) else "indictable"
    if not pd.isna(max_indictable) and not pd.isna(max_sc):
        mode = "hybrid"
    
    # Parse minimum sentences
    summary_minimum = parse_minimum(min_sc)
    indictable_minimum = parse_minimum(min_indictable)
    
    # Get immigration consequences
    immigration_results = ca_collateral_consequences.check_inadmissibility(
        section=section,
        mode=mode,
        indictable_maximum=max_years
    )
    
    # Get sentencing options
    discharge_results = check_discharge_available(
        summary_minimum=summary_minimum,
        indictable_minimum=indictable_minimum,
        indictable_maximum=indictable_maximum
    )
    
    cso_results = check_cso_availablity(
        section=section,
        summary_minimum=summary_minimum,
        indictable_minimum=indictable_minimum,
        indictable_maximum=indictable_maximum,
        mode=mode
    )
    
    intermittent_results = check_intermittent_available(
        summary_minimum=summary_minimum,
        indictable_minimum=indictable_minimum
    )
    
    suspended_results = check_suspended_sentence_available(
        summary_minimum=summary_minimum,
        indictable_minimum=indictable_minimum
    )
    
    # Get ancillary orders
    dna_results = check_dna_designation(
        offence=[section],  # Passing minimal offence data
        mode=mode,
        quantum=indictable_maximum
    )
    
    soira_results = check_soira(
        section=section,
        mode=mode,
        indictable_maximum=indictable_maximum
    )
    
    weapons_results = check_section_109_weapons_prohibition(
        offence=[section]  # Passing minimal offence data
    )
    
    # Combine all results
    return {
        "immigration": immigration_results,
        "sentencing_options": {
            "discharge": {
                "available": discharge_results["status"]["available"],
                "notes": discharge_results["notes"]
            },
            "cso": {
                "available": cso_results["status"]["available"],
                "notes": cso_results["notes"]
            },
            "intermittent": {
                "available": intermittent_results["status"]["available"],
                "notes": intermittent_results["notes"]
            },
            "suspended": {
                "available": suspended_results["status"]["available"],
                "notes": suspended_results["notes"]
            }
        },
        "ancillary_orders": {
            "dna": {
                "available": dna_results["status"]["available"],
                "notes": dna_results["notes"]
            },
            "soira": {
                "available": soira_results[0]["status"]["available"] if soira_results else False,
                "notes": soira_results[0]["notes"] if soira_results else None
            },
            "weapons": {
                "available": weapons_results["status"]["available"],
                "notes": weapons_results["notes"]
            }
        }
    }

def offence_grid(request):
    """Landing page for the offence grid tool."""
    # Load all offences
    offences = load_offences()
    
    # Get selected offences from request
    selected_offences = request.GET.getlist('offences')
    
    # Process selected offences
    results = {}
    if selected_offences:
        for section in selected_offences:
            # Find the matching offence data
            for offence_data in offences:
                if offence_data[0] == section:
                    results[format_section(section)] = get_collateral_consequences(
                        section=section,
                        max_indictable=offence_data[3],
                        max_sc=offence_data[4],
                        min_indictable=offence_data[5],
                        min_sc=offence_data[6]
                    )
                    break
    
    return render(request, 'offence_grid/index.html', {
        'title': 'Offence Grid',
        'offences': [(o[0], f"{o[1]} - {o[2]}") for o in offences],
        'selected_offences': selected_offences,
        'results': results,
    })
