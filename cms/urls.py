from django.urls import path
from . import views

app_name = 'cms'

urlpatterns = [
    # Category URLs
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:id>/', views.CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),
    
    # Tag URLs
    path('tags/', views.TagListCreateView.as_view(), name='tag-list-create'),
    path('tags/<int:id>/', views.TagRetrieveUpdateDestroyView.as_view(), name='tag-detail'),
    
    # Service URLs
    path('services/', views.ServiceListCreateView.as_view(), name='service-list-create'),
    path('services/<int:id>/', views.ServiceRetrieveUpdateDestroyView.as_view(), name='service-detail'),
    
    # Portfolio URLs
    path('portfolios/', views.PortfolioListCreateView.as_view(), name='portfolio-list-create'),
    path('portfolios/<slug:slug>/', views.PortfolioRetrieveUpdateDestroyView.as_view(), name='portfolio-detail'),
    
    # Blog URLs
    path('blogs/', views.BlogListCreateView.as_view(), name='blog-list-create'),
    path('blogs/<slug:slug>/', views.BlogRetrieveUpdateDestroyView.as_view(), name='blog-detail'),
] 