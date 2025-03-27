from django.shortcuts import render
from django.db.models import Q
from apps.data_processing.models import CaseMetadata
from apps.search.models import Category

# Create your views here.

def search_view(request):
    """View for searching cases by categories."""
    # Get all available categories
    categories = Category.objects.all().order_by('name')
    
    # Get selected categories from request
    selected_categories = request.GET.getlist('categories')
    
    # Initialize queryset with all cases
    cases = CaseMetadata.objects.all().order_by('-decision_date')
    
    # Filter cases if categories are selected
    if selected_categories:
        # Create a Q object for each category
        # This will match cases that have the category in their categories list
        category_filters = Q()
        for category in selected_categories:
            category_filters |= Q(categories__contains=[category])
        cases = cases.filter(category_filters)
    
    context = {
        'categories': categories,
        'selected_categories': selected_categories,
        'cases': cases,
    }
    
    return render(request, 'search/search.html', context)
