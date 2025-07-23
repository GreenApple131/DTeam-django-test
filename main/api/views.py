from rest_framework import generics
from main.models import CV
from .serializers import CVSerializer


# API Views
class CVListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: List all CVs
    POST: Create a new CV
    """

    queryset = CV.objects.all()
    serializer_class = CVSerializer


class CVRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific CV
    PUT/PATCH: Update a specific CV
    DELETE: Delete a specific CV
    """

    queryset = CV.objects.all()
    serializer_class = CVSerializer
    lookup_field = "pk"
