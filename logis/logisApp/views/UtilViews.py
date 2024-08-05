from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Municipio, Urna, MaterialEleitoral, ZonaEleitoral, MunicipioZona, Secao, DistributionLog, Distribuicao, Solicitacao
from ..forms import MunicipioForm, UrnaForm, MaterialEleitoralForm, ZonaEleitoralForm, UploadFileForm, ZonaDistributionForm, ZonaEstoqueForm, ZonaEleitoralFormSet, DistribuicaoForm, DistribuicaoFormSet
from django.db.models import Sum, Count
from django.http import JsonResponse
import logging
import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import json
from django.forms import modelformset_factory
from django.core.paginator import Paginator

def index(request):
    zonas = ZonaEleitoral.objects.all()
    urnas = Urna.objects.all()
    municipios = Municipio.objects.all()
    municipios_zonas = MunicipioZona.objects.all()
    solicitacoes_urnas = Solicitacao.objects.all()

    # Calcular total de seções
    total_secoes = sum(zona.qtdSecoes for zona in zonas)

    # Calcular total de urnas em estoque para a zona com id = 53
    try:
        zona_estoque = ZonaEleitoral.objects.get(id=58)
        total_urnas_estoque = zona_estoque.qtdUrnasEstoque
    except ZonaEleitoral.DoesNotExist:
        total_urnas_estoque = 0

    # Calcular total de urnas utilizáveis
    total_urnas_utilizaveis = sum(zona.qtdUrnasMRV + zona.qtdUrnasCont for zona in zonas)

    context = {
        'zonas': zonas,
        'urnas': urnas,
        'municipios': municipios,
        'municipios_zonas': municipios_zonas,
        'solicitacoes_urnas': solicitacoes_urnas,
        'total_secoes': total_secoes,
        'total_urnas_estoque': total_urnas_estoque,
        'total_urnas_utilizaveis': total_urnas_utilizaveis,
    }
    return render(request, 'logisApp/index.html', context)


def qtd_urnas_necessarias(zona):
    return zona.qtdSecoes

def qtd_cont_necessarias(zona):
    return int(zona.qtdSecoes * 0.15)

def get_qtd_urnas(zona):
    return Solicitacao.objects.filter(zona_eleitoral=zona).aggregate(total=Sum('quantidade'))['total'] or 0

def get_qtd_cont(zona):
    return 0


def is_compatible(primary_model, cont_model):
    if primary_model == '2020':
        return cont_model in ['2020', '2023']
    if cont_model == '2020':
        return primary_model in ['2020', '2023']
    return True

def checar_compatibilidade(pkMRV, pkCont):
    try:
        MRV = Urna.objects.get(pk=pkMRV)
        cont = Urna.objects.get(pk=pkCont)
        MODELO_URNAS = [
            '2008', '2010', '2012', '2015', '2018', '2020', '2023'
        ]
        modelo_MRV = MRV.modelo
        modelo_cont = cont.modelo
        if modelo_MRV == '2020':
            return modelo_cont in ['2020', '2023']
        elif modelo_cont == '2020':
            return modelo_MRV in ['2020', '2023']
        return True
    except Urna.DoesNotExist:
        return False

def mrvNecessarias(pk):
    zona = ZonaEleitoral.objects.get(pk=pk)
    qtd = zona.qtdSecoes
    return qtd

def contNecessarias(pk):
    zona = ZonaEleitoral.objects.get(pk=pk)
    qtd = zona.qtdSecoes * 0.15
    return qtd

def is_compatible(primary_model, contingency_model):
    return True

@login_required
def distribuir_manual(request):
    if request.method == 'POST':
        zona_estoque_id = request.POST.get('zona_estoque_id')
        zonas_ids = request.POST.getlist('zonas_ids')
        tipo_urna = request.POST.get('tipo_urna')  # 'primario' or 'contingencia'

        if not zona_estoque_id or not zonas_ids or not tipo_urna:
            return JsonResponse({'messages': ['Dados insuficientes para a distribuição.']}, status=400)

        try:
            zona_estoque = ZonaEleitoral.objects.get(id=zona_estoque_id)
        except ZonaEleitoral.DoesNotExist:
            return JsonResponse({'messages': ['Zona de estoque não encontrada.']}, status=404)

        distribuicao = Distribuicao.objects.create(distributed_by=request.user, stock_zone=zona_estoque)
        urnas_estoque = Urna.objects.filter(zona_eleitoral=zona_estoque).order_by('-modelo')
        messages = []

        # Zerar a quantidade de urnas nas zonas de destino
        for zona_id in zonas_ids:
            if zona_id != zona_estoque_id:
                try:
                    zona = ZonaEleitoral.objects.get(id=zona_id)
                    zona.qtdUrnasMRV = 0
                    zona.qtdUrnasCont = 0
                    zona.qtdUrnasEstoque = 0
                    zona.save()
                except ZonaEleitoral.DoesNotExist:
                    continue

        # Fazer a distribuição
        for zona_id in zonas_ids:
            try:
                zona = ZonaEleitoral.objects.get(id=zona_id)
            except ZonaEleitoral.DoesNotExist:
                messages.append(f"Zona com ID {zona_id} não encontrada.")
                continue

            if tipo_urna == 'primario':
                qtd_urnas_necessarias = zona.qtdSecoes
            elif tipo_urna == 'contingencia':
                qtd_urnas_necessarias = int(zona.qtdSecoes * 0.12)
            else:
                return JsonResponse({'messages': ['Tipo de urna inválido.']}, status=400)

            urnas_distribuidas = {}

            for urna in urnas_estoque:
                if qtd_urnas_necessarias > 0 and urna.qtd > 0:
                    if urna.qtd >= qtd_urnas_necessarias:
                        urnas_distribuidas[urna.modelo] = qtd_urnas_necessarias
                        urna.qtd -= qtd_urnas_necessarias
                        qtd_urnas_necessarias = 0
                    else:
                        urnas_distribuidas[urna.modelo] = urna.qtd
                        qtd_urnas_necessarias -= urna.qtd
                        urna.qtd = 0
                    urna.save()

            if qtd_urnas_necessarias > 0:
                messages.append(f"Zona {zona.nome} não tem urnas suficientes para o tipo {tipo_urna}.")
            else:
                if tipo_urna == 'primario':
                    zona.qtdUrnasMRV = sum(urnas_distribuidas.values())
                elif tipo_urna == 'contingencia':
                    zona.qtdUrnasCont = sum(urnas_distribuidas.values())
                
                zona.qtdUrnasEstoque = zona.qtdUrnasMRV + zona.qtdUrnasCont
                zona.save()

                for modelo, quantidade in urnas_distribuidas.items():
                    urna_queryset = Urna.objects.filter(modelo=modelo, zona_eleitoral=zona_estoque)
                    if urna_queryset.exists() and quantidade > 0:
                        urna = urna_queryset.first()
                        Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=quantidade, distribution=distribuicao)
                        Urna.objects.create(modelo=modelo, bio=urna.bio, zona_eleitoral=zona, qtd=quantidade)
                        DistributionLog.objects.create(distribuicao=distribuicao, urna=urna, quantity=quantidade, distribution_type=tipo_urna.upper())

        return JsonResponse({'messages': messages})

    zonas = ZonaEleitoral.objects.all().order_by('id')
    return render(request, 'logisApp/distribuir_manual.html', {'zonas': zonas})





@login_required
def get_urnas_from_stock(request):
    stock_zone_id = request.GET.get('stock_zone_id')
    urnas = Urna.objects.filter(zona_eleitoral_id=stock_zone_id).values('modelo', 'qtd')
    return JsonResponse(list(urnas), safe=False)

def add_primary_model(zona, modelo, quantidade):
    urna, created = Urna.objects.get_or_create(modelo=modelo, zona_eleitoral=zona, defaults={'qtd': 0})
    urna.qtd += quantidade
    urna.save()
    Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=quantidade)

def add_contingency_model(zona, modelo, quantidade):
    urna, created = Urna.objects.get_or_create(modelo=modelo, zona_eleitoral=zona, defaults={'qtd': 0})
    urna.qtd += quantidade
    urna.save()
    Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=quantidade)



# Funções de apoio
def get_urnas_zona(request, zona_id):
    urnas = Urna.objects.filter(zona_eleitoral_id=zona_id)
    return JsonResponse(list(urnas.values('id', 'modelo', 'qtd')), safe=False)

def get_municipios_zona(request, zona_id):
    municipios = MunicipioZona.objects.filter(zona_id=zona_id)
    return JsonResponse(list(municipios.values('municipio__nome', 'municipio__id')), safe=False)



@login_required
def distribuir_tudo(request):
    if request.method == 'POST':
        zona_estoque_id = request.POST.get('zona_estoque_id')
        
        if not zona_estoque_id:
            return JsonResponse({'messages': ['ID da zona de estoque não fornecido.']}, status=400)

        try:
            zona_estoque = ZonaEleitoral.objects.get(id=zona_estoque_id)
        except ZonaEleitoral.DoesNotExist:
            return JsonResponse({'messages': ['Zona de estoque não encontrada.']}, status=404)

        # Ensure Distribuicao instance creation
        distribuicao = Distribuicao.objects.create(distributed_by=request.user)

        zonas = ZonaEleitoral.objects.exclude(id=zona_estoque_id)
        urnas_estoque = Urna.objects.filter(zona_eleitoral=zona_estoque).order_by('-modelo')
        messages = []

        for zona in zonas:
            qtd_urnas_mrv_necessarias = zona.qtdSecoes
            qtd_urnas_contingencia_necessarias = int(qtd_urnas_mrv_necessarias * 0.12)

            urnas_primarias_distribuidas = {}
            urnas_contingencia_distribuidas = {}

            for urna in urnas_estoque:
                if qtd_urnas_mrv_necessarias > 0 and urna.qtd > 0:
                    if urna.qtd >= qtd_urnas_mrv_necessarias:
                        urnas_primarias_distribuidas[urna.modelo] = qtd_urnas_mrv_necessarias
                        urna.qtd -= qtd_urnas_mrv_necessarias
                        qtd_urnas_mrv_necessarias = 0
                    else:
                        urnas_primarias_distribuidas[urna.modelo] = urna.qtd
                        qtd_urnas_mrv_necessarias -= urna.qtd
                        urna.qtd = 0
                    urna.save()

            for urna in urnas_estoque:
                if qtd_urnas_contingencia_necessarias > 0 and urna.qtd > 0:
                    primary_model = next(iter(urnas_primarias_distribuidas), None)
                    if primary_model and is_compatible(primary_model, urna.modelo):
                        if urna.qtd >= qtd_urnas_contingencia_necessarias:
                            urnas_contingencia_distribuidas[urna.modelo] = qtd_urnas_contingencia_necessarias
                            urna.qtd -= qtd_urnas_contingencia_necessarias
                            qtd_urnas_contingencia_necessarias = 0
                        else:
                            urnas_contingencia_distribuidas[urna.modelo] = urna.qtd
                            qtd_urnas_contingencia_necessarias -= urna.qtd
                            urna.qtd = 0
                        urna.save()

            if qtd_urnas_mrv_necessarias > 0 or qtd_urnas_contingencia_necessarias > 0:
                messages.append(f"Zona {zona.nome} não tem urnas suficientes.")
            else:
                zona.qtdUrnasEstoque = sum(urnas_primarias_distribuidas.values()) + sum(urnas_contingencia_distribuidas.values())
                zona.qtdUrnasMRV = sum(urnas_primarias_distribuidas.values())
                zona.qtdUrnasCont = sum(urnas_contingencia_distribuidas.values())
                zona.save()

                for modelo, quantidade in urnas_primarias_distribuidas.items():
                    urna_queryset = Urna.objects.filter(modelo=modelo, zona_eleitoral=zona_estoque)
                    if urna_queryset.exists() and quantidade > 0:
                        urna = urna_queryset.first()
                        solicitacao = Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=quantidade, distribution=distribuicao)
                        Urna.objects.create(modelo=modelo, bio=urna.bio, zona_eleitoral=zona, qtd=quantidade)
                        DistributionLog.objects.create(distribuicao=distribuicao, urna=urna, quantity=quantidade, distribution_type='MRV')

                for modelo, quantidade in urnas_contingencia_distribuidas.items():
                    urna_queryset = Urna.objects.filter(modelo=modelo, zona_eleitoral=zona_estoque)
                    if urna_queryset.exists() and quantidade > 0:
                        urna = urna_queryset.first()
                        solicitacao = Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=quantidade, distribution=distribuicao)
                        Urna.objects.create(modelo=modelo, bio=urna.bio, zona_eleitoral=zona, qtd=quantidade)
                        DistributionLog.objects.create(distribuicao=distribuicao, urna=urna, quantity=quantidade, distribution_type='CONT')

        return JsonResponse({'messages': messages})

    zonas = ZonaEleitoral.objects.all().order_by('id')
    return render(request, 'logisApp/solicitar_tudo.html', {'zonas': zonas})

@login_required
def distribuir_materiais(request):
    return render(request, 'logisApp/distribuir_materiais.html')

@login_required
def relatorio_urnas(request):
    return render(request, 'logisApp/relatorio_urnas.html')

@login_required
def relatorio_materiais(request):
    return render(request, 'logisApp/relatorio_materiais.html')

@login_required
def relatorio_zonas(request):
    return render(request, 'logisApp/relatorio_zonas.html')

@login_required
def relatorio_geral(request):
    zonas = ZonaEleitoral.objects.all()
    urnas = Urna.objects.all()
    
    zona_urnas_data = []
    for zona in zonas:
        urnas_da_zona = urnas.filter(zona_eleitoral=zona)
        zona_urnas_data.append({
            'nome': zona.nome,
            'urnas': list(urnas_da_zona.values('modelo', 'qtd'))
        })
    
    context = {
        'zona_urnas_data': zona_urnas_data,
    }
    return render(request, 'logisApp/relatorio_geral.html', context)


def get_urnas(request):
    zona_id = request.GET.get('zona_id')
    if zona_id:
        zona = ZonaEleitoral.objects.get(id=zona_id)
        urnas = Urna.objects.filter(zona_eleitoral=zona)
        urnas_data = [
            {'id': urna.id, 'modelo': urna.modelo, 'qtd': urna.qtd}
            for urna in urnas
        ]
        return JsonResponse({'urnas': urnas_data})
    return JsonResponse({'urnas': []})

