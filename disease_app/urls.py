from django.urls import path
from . import views

app_name = 'disease_app'

urlpatterns = [
    path('',                    views.home,              name='home'),
    path('predict/',            views.predict,           name='predict'),
    path('result/<int:pk>/',    views.result,            name='result'),
    path('history/',            views.history,           name='history'),
    path('about/',              views.about,             name='about'),
    path('delete/<int:pk>/',    views.delete_prediction, name='delete_prediction'),
    path('api/statistics/',     views.statistics,        name='statistics'),
]