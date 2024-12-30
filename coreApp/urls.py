from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('catalog', views.catalog, name='catalog'),
    path('search', views.search, name='search'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('logout', views.logout, name='logout'),
    path('book_detail/<str:pk>/', views.load_book, name='load_book'),
    path('toggle_bookmark/<int:book_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarked_books/', views.bookmarked_books, name='bookmarked_books'),
    path('settings/', views.settings, name='settings'),
    path('profile_update/', views.profile_update, name='profile_update'),
    path('password_change/', views.password_change, name='password_change'),
    path('api/books/search/', views.GoogleBooksAPIView.as_view(), name='books-search'),

] 