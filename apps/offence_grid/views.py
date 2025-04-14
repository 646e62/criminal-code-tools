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
    reverse_onus,
    check_section_469_offence,
    check_section_515_mandatory_weapons_prohibition,
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
    consequences = {}

    # Parse the sentences
    summary_min = parse_minimum(min_sc)
    indictable_min = parse_minimum(min_indictable)
    indictable_max = parse_maximum(max_indictable)

    # Determine mode based on maximum sentences
    mode = "summary" if pd.isna(max_indictable) and not pd.isna(max_sc) else "indictable"
    if not pd.isna(max_indictable) and not pd.isna(max_sc):
        mode = "hybrid"

    # Get bail information
    consequences['bail'] = {
        'reverse_onus': reverse_onus(),
        'section_469': check_section_469_offence(section),
        'mandatory_weapons_prohibition': check_section_515_mandatory_weapons_prohibition(section)
    }

    # Get immigration consequences
    max_years = indictable_max["jail"]["amount"] if indictable_max["jail"]["amount"] else 0
    consequences['immigration'] = ca_collateral_consequences.check_inadmissibility(
        section=section,
        mode=mode,
        indictable_maximum=max_years
    )

    # Get sentencing options
    consequences['sentencing_options'] = {
        'discharge': check_discharge_available(
            summary_minimum=summary_min,
            indictable_minimum=indictable_min,
            indictable_maximum=indictable_max
        ),
        'cso': check_cso_availablity(
            section=section,
            summary_minimum=summary_min,
            indictable_minimum=indictable_min,
            indictable_maximum=indictable_max,
            mode=mode
        ),
        'intermittent': check_intermittent_available(
            summary_minimum=summary_min,
            indictable_minimum=indictable_min
        ),
        'suspended': check_suspended_sentence_available(
            summary_minimum=summary_min,
            indictable_minimum=indictable_min
        )
    }

    # Get ancillary orders
    consequences['ancillary_orders'] = {
        'dna': check_dna_designation(
            offence=[section],
            mode=mode,
            quantum=indictable_max
        ),
        'soira': check_soira(
            section=section,
            mode=mode,
            indictable_maximum=indictable_max
        ),
        'weapons': check_section_109_weapons_prohibition([
            section,
            None,  # offence name not needed
            max_indictable,
            max_sc,
            min_indictable,
            min_sc
        ])
    }

    return consequences

def get_offence_summary(section, max_indictable, max_sc, min_indictable, min_sc):
    """Generate a summary of the offence including mode and sentences."""
    summary = {}
    
    # Parse the quantum values
    max_indictable_dict = parse_maximum(max_indictable) if max_indictable else None
    max_sc_dict = parse_maximum(max_sc) if max_sc else None
    min_indictable_dict = parse_minimum(min_indictable) if min_indictable else None
    min_sc_dict = parse_minimum(min_sc) if min_sc else None
    
    # Determine mode
    if max_indictable_dict and max_sc_dict:
        summary['mode'] = 'Hybrid'
    elif max_indictable_dict:
        summary['mode'] = 'Indictable'
    else:
        summary['mode'] = 'Summary'
    
    # Add sentence information
    if max_indictable_dict:
        summary['indictable_maximum'] = max_indictable_dict
        summary['indictable_minimum'] = min_indictable_dict or {'jail': {'amount': None, 'unit': None}, 'fine': {'amount': None, 'unit': None}}
    
    # For hybrid offences without explicit summary max, use 729 days
    if summary['mode'] in ['Hybrid', 'Summary']:
        if max_sc_dict and (max_sc_dict['jail']['amount'] or max_sc_dict['fine']['amount']):
            summary['summary_maximum'] = max_sc_dict
        else:
            summary['summary_maximum'] = {'jail': {'amount': 729, 'unit': 'days'}, 'fine': {'amount': None, 'unit': None}}
        summary['summary_minimum'] = min_sc_dict or {'jail': {'amount': None, 'unit': None}, 'fine': {'amount': None, 'unit': None}}
    
    return summary

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
                    # Get offence summary
                    summary = get_offence_summary(
                        section=section,
                        max_indictable=offence_data[3],
                        max_sc=offence_data[4],
                        min_indictable=offence_data[5],
                        min_sc=offence_data[6]
                    )
                    
                    # Get collateral consequences
                    consequences = get_collateral_consequences(
                        section=section,
                        max_indictable=offence_data[3],
                        max_sc=offence_data[4],
                        min_indictable=offence_data[5],
                        min_sc=offence_data[6]
                    )
                    
                    # Combine summary and consequences
                    results[format_section(section)] = {
                        'summary': summary,
                        **consequences
                    }
                    break
    
    return render(request, 'offence_grid/index.html', {
        'title': 'Offence Grid',
        'offences': [(o[0], f"{o[1]} - {o[2]}") for o in offences],
        'selected_offences': selected_offences,
        'results': results,
    })
