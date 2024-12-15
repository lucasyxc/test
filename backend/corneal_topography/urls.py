from django.urls import path
from . import views

urlpatterns = [
    path('api/corneal-topography/', views.jt_Medmontcorneal, name='corneal_topography'),
]
