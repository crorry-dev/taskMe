from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskProofViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'proofs', TaskProofViewSet, basename='proof')

urlpatterns = [
    path('', include(router.urls)),
]
