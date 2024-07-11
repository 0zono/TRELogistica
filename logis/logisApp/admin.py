from django.contrib import admin
from .models import Municipio, ZonaEleitoral, MunicipioZona, Urna, MaterialEleitoral, ZE_solicita_urna, SolicitaMaterial, Manutencao

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)

@admin.register(ZonaEleitoral)
class ZonaEleitoralAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'qtdSecoes', 'qtdUrnasEstoque')
    search_fields = ('nome',)

@admin.register(MunicipioZona)
class MunicipioZonaAdmin(admin.ModelAdmin):
    list_display = ('id', 'municipio', 'zona')
    search_fields = ('municipio__nome', 'zona__nome')
    list_filter = ('municipio', 'zona')

@admin.register(Urna)
class UrnaAdmin(admin.ModelAdmin):
    list_display = ('id', 'modelo', 'bio', 'zona_eleitoral', 'qtd')
    search_fields = ('modelo',)
    list_filter = ('modelo', 'zona_eleitoral')

@admin.register(MaterialEleitoral)
class MaterialEleitoralAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'tipo', 'quantidade')
    search_fields = ('nome', 'tipo')
    list_filter = ('tipo',)

@admin.register(ZE_solicita_urna)
class ZESolicitaUrnaAdmin(admin.ModelAdmin):
    list_display = ('id', 'zona_eleitoral', 'urna', 'data_solicitacao', 'quantidade')
    search_fields = ('zona_eleitoral__nome', 'urna__modelo')
    list_filter = ('zona_eleitoral', 'urna', 'data_solicitacao')

@admin.register(SolicitaMaterial)
class SolicitaMaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'zona_eleitoral', 'material', 'data_solicitacao', 'quantidade')
    search_fields = ('zona_eleitoral__nome', 'material__nome')
    list_filter = ('zona_eleitoral', 'material', 'data_solicitacao')

@admin.register(Manutencao)
class ManutencaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'urna', 'data_manutencao', 'descricao', 'tecnico_responsavel')
    search_fields = ('urna__modelo', 'tecnico_responsavel')
    list_filter = ('urna', 'data_manutencao')

