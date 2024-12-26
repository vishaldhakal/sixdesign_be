from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ExpenseViewSet,
    ExpenseCategoryListCreateView,
    ExpenseCategoryRetrieveUpdateDestroyView,
)

app_name = 'expense'

router = DefaultRouter()
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('categories/', ExpenseCategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', ExpenseCategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),
    # The following URLs will be automatically added by the router:
    # expenses/my-activity/ - for user activity
    # expenses/summary/ - for user expense summary
] + router.urls 