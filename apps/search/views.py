from django.shortcuts import render
from django.db.models import Q
from apps.data_processing.models import CaseMetadata, FactPattern
from apps.search.models import Category
import re

def parse_search_query(query_string):
    """Parse a search query string into a Q object using boolean logic.
    
    Supports:
    - AND (space between terms)
    - OR (| between terms)
    - NOT (- before term)
    - Phrases (terms in quotes)
    - Parentheses for grouping
    
    Example: 'assault AND ("grievous bodily" OR battery) -domestic'
    """
    if not query_string:
        return Q()
    
    # Handle quoted phrases first
    phrases = re.findall(r'"([^"]*)"', query_string)
    for phrase in phrases:
        query_string = query_string.replace(f'"{phrase}"', f'__{phrase.replace(" ", "_")}__')
    
    # Split on spaces, preserving quoted phrases
    tokens = []
    current_token = []
    for char in query_string:
        if char == ' ' and not current_token:
            continue
        elif char == ' ' and not any(current_token[-1].startswith('__') for token in tokens if token):
            if current_token:
                tokens.append(''.join(current_token))
                current_token = []
        else:
            current_token.append(char)
    if current_token:
        tokens.append(''.join(current_token))
    
    # Restore phrases
    tokens = [token.replace('__', '').replace('_', ' ') if token.startswith('__') else token for token in tokens]
    
    def create_term_filter(term):
        """Create a Q object for a single search term."""
        if term.startswith('-'):
            # Exclude term from all searchable fields
            term = term[1:]
            return (
                ~Q(style_of_cause__icontains=term) & 
                ~Q(citation__icontains=term) & 
                ~Q(keywords__icontains=term) &
                ~Q(factpattern__canlii_keywords__icontains=term)
            )
        
        # Include term in any searchable field
        return (
            Q(style_of_cause__icontains=term) | 
            Q(citation__icontains=term) |
            Q(keywords__icontains=term) |
            Q(factpattern__canlii_keywords__icontains=term)
        )
    
    def parse_expression(tokens):
        """Recursively parse tokens into a Q object."""
        if not tokens:
            return Q()
        
        result = Q()
        current_op = 'AND'
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            
            if token == '(':
                # Find matching closing parenthesis
                depth = 1
                j = i + 1
                while j < len(tokens) and depth > 0:
                    if tokens[j] == '(':
                        depth += 1
                    elif tokens[j] == ')':
                        depth -= 1
                    j += 1
                if depth == 0:
                    sub_expr = parse_expression(tokens[i+1:j-1])
                    if current_op == 'AND':
                        result &= sub_expr
                    else:
                        result |= sub_expr
                    i = j
                else:
                    # Malformed parentheses, treat as literal
                    term_filter = create_term_filter(token)
                    if current_op == 'AND':
                        result &= term_filter
                    else:
                        result |= term_filter
                    i += 1
            
            elif token.upper() == 'AND':
                current_op = 'AND'
                i += 1
            
            elif token == '|' or token.upper() == 'OR':
                current_op = 'OR'
                i += 1
            
            else:
                term_filter = create_term_filter(token)
                if current_op == 'AND':
                    result &= term_filter
                else:
                    result |= term_filter
                i += 1
        
        return result

    return parse_expression(tokens)

def search_view(request):
    """View for searching cases by categories and text query."""
    # Get all available categories
    categories = Category.objects.all().order_by('name')
    
    # Get selected categories from request
    selected_categories = request.GET.getlist('categories')
    
    # Get search query from request
    search_query = request.GET.get('q', '').strip()
    
    # Initialize queryset with all cases
    cases = CaseMetadata.objects.all().order_by('-decision_date')
    
    # Filter cases if categories are selected
    if selected_categories:
        category_filters = Q()
        for category in selected_categories:
            category_filters |= Q(categories__contains=[category])
        cases = cases.filter(category_filters)
    
    # Apply text search if query exists
    if search_query:
        cases = cases.filter(parse_search_query(search_query)).distinct()
    
    context = {
        'categories': categories,
        'selected_categories': selected_categories,
        'search_query': search_query,
        'cases': cases,
    }
    
    return render(request, 'search/search.html', context)
