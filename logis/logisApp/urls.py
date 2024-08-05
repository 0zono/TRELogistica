from django.urls import path

from .views import UtilViews
from .views import UploadViews
from .views import CrudViews

from django.views.generic import TemplateView

urlpatterns = [
    path('', UtilViews.index, name='index'),
    path('adicionar_municipio/', CrudViews.adicionar_municipio, name='adicionar_municipio'),
    path('adicionar_urnas/', CrudViews.adicionar_urnas, name='adicionar_urnas'),
    path('adicionar_materiais/', CrudViews.adicionar_materiais, name='adicionar_materiais'),
    path('listar_municipios/', CrudViews.listar_municipios, name='listar_municipios'),
    path('listar_urnas/', CrudViews.listar_urnas, name='listar_urnas'),
    path('listar_materiais/', CrudViews.listar_materiais, name='listar_materiais'),
    path('distribuir_tudo/', UtilViews.distribuir_tudo, name='distribuir_tudo'),
    path('listar_zonas/', CrudViews.listar_zonas, name='listar_zonas'),
    path('adicionar_zonas/', CrudViews.adicionar_zonas, name='adicionar_zonas'),
    
    # Paths for "Remover" dropdown
    path('remover_municipio/', CrudViews.remover_municipio, name='remover_municipio'),
    path('remover_urnas/', CrudViews.remover_urnas, name='remover_urnas'),
    path('remover_materiais/', CrudViews.remover_materiais, name='remover_materiais'),
    path('remover_zonas/', CrudViews.remover_zonas, name='remover_zonas'),
    
    # Paths for "Distribuir" dropdown
    path('distribuir_tudo/', UtilViews.distribuir_tudo, name='distribuir_tudo'),
    path('distribuir_materiais/', UtilViews.distribuir_materiais, name='distribuir_materiais'),
    path('distribuir_manual/', UtilViews.distribuir_manual, name='distribuir_manual'),
    path('get_urnas_from_stock/', UtilViews.get_urnas_from_stock, name='get_urnas_from_stock'),
    
    # Paths for "Relatórios" dropdown
    path('relatorio_urnas/', UtilViews.relatorio_urnas, name='relatorio_urnas'),
    path('relatorio_materiais/', UtilViews.relatorio_materiais, name='relatorio_materiais'),
    path('relatorio_zonas/', UtilViews.relatorio_zonas, name='relatorio_zonas'),
    path('relatorio_geral/', UtilViews.relatorio_geral, name='relatorio_geral'),

    path('upload/', UploadViews.upload_file, name='upload_file'),
    path('upload/success/', TemplateView.as_view(template_name="success.html"), name='upload_success'),
    path('listar_distribuicoes/', UploadViews.listar_distribuicoes, name='listar_distribuicoes'),
    path('get_urnas/<int:zona_id>/', UtilViews.get_urnas, name='get_urnas'),


]