from django.urls import path
from .views import *
from django.urls import reverse_lazy

LOGIN_URL = reverse_lazy('blog:login')

app_name = 'blog'

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('delete/<int:pk>/', delete, name='delete'),
    path('edit/<int:pk>/', edit, name='edit'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('new-post/', create_post, name='new-post'),   
    path('post/<int:pk>/', get_post, name='get-post'),   
    path('register/', register, name='register'),
    
    
]