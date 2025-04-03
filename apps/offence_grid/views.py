from django.shortcuts import render
import pandas as pd
import sys
import re
from pathlib import Path

# Add src to Python path for importing tools
src_path = Path(__file__).resolve().parent.parent.parent / 'src'
sys.path.append(str(src_path))

from tools import ca_collateral_consequences

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
             row['maximum_indictable'], row['maximum_sc']) 
            for _, row in df.iterrows()]

def parse_maximum(max_value):
    """Parse maximum sentence value to extract years."""
    if pd.isna(max_value) or not max_value:
        return 0
    if isinstance(max_value, str) and max_value.endswith('y'):
        return int(max_value.rstrip('y'))
    return 0

def get_collateral_consequences(section, max_indictable, max_sc):
    """Get collateral consequences for an offence."""
    # Parse the maximum sentence
    max_years = parse_maximum(max_indictable)
    
    # Determine mode based on maximum sentences
    mode = "summary" if pd.isna(max_indictable) and not pd.isna(max_sc) else "indictable"
    if not pd.isna(max_indictable) and not pd.isna(max_sc):
        mode = "hybrid"
    
    # Call the check_inadmissibility function
    results = ca_collateral_consequences.check_inadmissibility(
        section=section,
        mode=mode,
        indictable_maximum=max_years
    )
    
    # Process results into a more usable format
    if not results:
        return {
            'available': False,
            'sections': [],
            'reason': 'No immigration consequences identified'
        }
    
    # Combine all results into a single response
    all_sections = []
    all_reasons = []
    for result in results:
        if result.get('sections'):
            # Format each section before adding to the list
            all_sections.extend([format_section(s) for s in result['sections']])
        if result.get('notes'):
            all_reasons.append(result['notes'])
    
    return {
        'available': True,
        'sections': list(set(all_sections)),  # Remove duplicates
        'reason': ' | '.join(set(all_reasons))  # Join unique reasons
    }

def offence_grid(request):
    """Landing page for the offence grid tool."""
    offences = load_offences()
    selected_offence = request.GET.get('offence')
    result = None
    
    if selected_offence:
        # Find the selected offence details
        offence_details = next(
            (o for o in offences if o[0] == selected_offence), 
            None
        )
        
        if offence_details:
            section, formatted_section, name, max_indictable, max_sc = offence_details
            result = get_collateral_consequences(section, max_indictable, max_sc)
    
    return render(request, 'offence_grid/index.html', {
        'title': 'Offence Grid',
        'offences': [(o[0], o[2]) for o in offences],  # Pass raw section for value, name for display
        'formatted_offences': [(o[0], f"{o[1]} - {o[2]}") for o in offences],  # Include formatted version
        'selected_offence': selected_offence,
        'result': result,
    })
