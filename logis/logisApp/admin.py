from django.contrib import admin
from .models import Municipio, ZonaEleitoral, MunicipioZona, Urna, MaterialEleitoral, Solicitacao, SolicitaMaterial, Manutencao, Secao, DistributionLog, Distribuicao

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('id','cod', 'nome')
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

@admin.register(Solicitacao)
class SolicitacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'zona_eleitoral', 'urna', 'data_solicitacao', 'quantidade', 'distribution_id')
    search_fields = ('zona_eleitoral__nome', 'urna__modelo')
    list_filter = ('zona_eleitoral', 'urna', 'data_solicitacao', 'distribution')
    readonly_fields = ('data_solicitacao',)

    def distribution_id(self, obj):
        return obj.distribution.id if obj.distribution else None

    distribution_id.short_description = 'Distribuição ID'

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

@admin.register(Secao)
class SecaoAdmin(admin.ModelAdmin):
    list_display = ('cod_zona', 'cod_municipio', 'cod_local', 'cod_secao', 'ind_especial')
    search_fields = ('cod_zona__nome', 'cod_municipio', 'cod_local', 'cod_secao', 'ind_especial')
    list_filter = ('cod_zona', 'cod_municipio', 'ind_especial')

@admin.register(DistributionLog)
class DistributionLogAdmin(admin.ModelAdmin):
    list_display = (
        'zona_eleitoral_name', 
        'urna', 
        'material_eleitoral', 
        'quantity', 
        'distributed_by', 
        'distribution_type', 
        'timestamp'
    )
    search_fields = (
        'zona_eleitoral_name', 
        'urna__modelo', 
        'material_eleitoral__nome', 
        'distributed_by__username', 
        'distribution_type'
    )
    list_filter = (
        'distribution_type', 
        'timestamp'
    )
    date_hierarchy = 'timestamp'

@admin.register(Distribuicao)
class DistribuicaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'distributed_by')
    search_fields = ('distributed_by__username',)
    list_filter = ('timestamp', 'distributed_by')
    readonly_fields = ('timestamp',)