from django.urls import path
from . import views

urlpatterns = [
    path('api/corneal-topography/', views.jt_medmontcorneal, name='corneal_topography'),
]
