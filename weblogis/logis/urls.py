from django.urls import path
from . import views

app_name = "logis"
urlpatterns = [
    path('', views.index, name='index'),
    path('cadastrar_municipio/', views.cadastrar_municipio, name='cadastrar_municipio'),
    path('cadastrar_ze/', views.cadastrar_ze, name='cadastrar_ze'),
    path('alterar_municipio/', views.alterar_municipio, name='alterar_municipio'),
    path('alterar_ze/', views.alterar_ze, name='alterar_ze'),
    path('gerar_solicitacao_urnas/', views.gerar_solicitacao_urnas, name='gerar_solicitacao_urnas'),
    path('adicionar_municipio/', views.adicionar_municipio, name='adicionar_municipio'),
]
