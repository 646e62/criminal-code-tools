from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import QueuedOffence
from .serializers import QueuedOffenceSerializer

class QueuedOffenceViewSet(viewsets.ModelViewSet):
    serializer_class = QueuedOffenceSerializer
    queryset = QueuedOffence.objects.all()

    def get_queryset(self):
        session_key = self.request.session.session_key or self.request.session.save() or self.request.session.session_key
        return QueuedOffence.objects.filter(session_key=session_key).order_by('order', 'created_at')

    def perform_create(self, serializer):
        session_key = self.request.session.session_key or self.request.session.save() or self.request.session.session_key
        serializer.save(session_key=session_key)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
