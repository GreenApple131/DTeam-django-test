from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import CV, Skill, Project


class CVListView(ListView):
    model = CV
    template_name = 'main/cv_list.html'
    context_object_name = 'cvs'
    paginate_by = 10
    
    def get_queryset(self):
        return CV.objects.prefetch_related('skills', 'project_set').order_by('-updated_at')


class CVDetailView(DetailView):
    model = CV
    template_name = 'main/cv_detail.html'
    context_object_name = 'cv'
    
    def get_queryset(self):
        return CV.objects.prefetch_related('skills', 'project_set')


# Function-based view alternative
def cv_list(request):
    cvs = CV.objects.prefetch_related('skills', 'project_set').order_by('-updated_at')
    return render(request, 'main/cv_list.html', {'cvs': cvs})


def cv_detail(request, pk):
    cv = get_object_or_404(CV, pk=pk)
    return render(request, 'main/cv_detail.html', {'cv': cv})
