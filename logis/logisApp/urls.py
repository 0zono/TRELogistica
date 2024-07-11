from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('adicionar_municipio/', views.adicionar_municipio, name='adicionar_municipio'),
    path('adicionar_urnas/', views.adicionar_urnas, name='adicionar_urnas'),
    path('adicionar_materiais/', views.adicionar_materiais, name='adicionar_materiais'),
    path('listar_municipios/', views.listar_municipios, name='listar_municipios'),
    path('listar_urnas/', views.listar_urnas, name='listar_urnas'),
    path('listar_materiais/', views.listar_materiais, name='listar_materiais'),
    path('distribuir_tudo/', views.distribuir_tudo, name='distribuir_tudo'),
    path('listar_zonas/', views.listar_zonas, name='listar_zonas'),
    path('adicionar_zonas/', views.adicionar_zonas, name='adicionar_zonas'),
    
    # Paths for "Remover" dropdown
    path('remover_municipio/', views.remover_municipio, name='remover_municipio'),
    path('remover_urnas/', views.remover_urnas, name='remover_urnas'),
    path('remover_materiais/', views.remover_materiais, name='remover_materiais'),
    path('remover_zonas/', views.remover_zonas, name='remover_zonas'),
    
    # Paths for "Distribuir" dropdown
    path('distribuir_tudo/', views.distribuir_tudo, name='distribuir_tudo'),
    path('distribuir_materiais/', views.distribuir_materiais, name='distribuir_materiais'),
    
    # Paths for "Relatórios" dropdown
    path('relatorio_urnas/', views.relatorio_urnas, name='relatorio_urnas'),
    path('relatorio_materiais/', views.relatorio_materiais, name='relatorio_materiais'),
    path('relatorio_zonas/', views.relatorio_zonas, name='relatorio_zonas'),
    path('relatorio_geral/', views.relatorio_geral, name='relatorio_geral'),
]
