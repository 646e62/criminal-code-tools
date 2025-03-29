from django.shortcuts import render

# Create your views here.

def offence_grid(request):
    """Landing page for the offence grid tool."""
    return render(request, 'offence_grid/index.html', {
        'title': 'Offence Grid',
    })
