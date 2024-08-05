from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Municipio, Urna, MaterialEleitoral, ZonaEleitoral, MunicipioZona, Secao, DistributionLog
from ..forms import MunicipioForm, UrnaForm, MaterialEleitoralForm, UploadFileForm, AdicionarZonaEleitoralForm, SolicitacaoForm, DistribuicaoForm
from django.db.models import Sum, Count
from ..models import ZonaEleitoral, Urna, Solicitacao
from django.http import JsonResponse
import logging
import pandas as pd
from django.core.files.storage import FileSystemStorage

from django.contrib import messages
import json

def add_primary_model(zona, modelo, quantidade):
    urna, created = Urna.objects.get_or_create(modelo=modelo, zona_eleitoral=zona, defaults={'qtd': 0})
    urna.qtd += quantidade
    urna.save()
    Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=quantidade)
#Não está sendo utilizado atualmente, será ao alterar a View distribuir_tudo#
def add_contingency_model(zona, modelo, quantidade):
    urna, created = Urna.objects.get_or_create(modelo=modelo, zona_eleitoral=zona, defaults={'qtd': 0})
    urna.qtd += quantidade
    urna.save()
    Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=quantidade)

@login_required
def adicionar_municipio(request):
    if request.method == 'POST':
        form = MunicipioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_municipios')
    else:
        form = MunicipioForm()
    return render(request, 'logisApp/adicionar_municipio.html', {'form': form})

@login_required
def adicionar_urnas(request):
    if request.method == 'POST':
        form = UrnaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_urnas')
    else:
        form = UrnaForm()
    return render(request, 'logisApp/adicionar_urnas.html', {'form': form})

@login_required
def adicionar_materiais(request):
    if request.method == 'POST':
        form = MaterialEleitoralForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_materiais')
    else:
        form = MaterialEleitoralForm()
    return render(request, 'logisApp/adicionar_materiais.html', {'form': form})

@login_required
def adicionar_zonas(request):
    if request.method == 'POST':
        form = AdicionarZonaEleitoralForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_zonas')  # Ajuste o nome da URL conforme necessário
    else:
        form = AdicionarZonaEleitoralForm() 
    return render(request, 'logisApp/adicionar_zona.html', {'form': form})

@login_required
def listar_municipios(request):
    municipios = Municipio.objects.all()
    return render(request, 'logisApp/listar_municipios.html', {'municipios': municipios})

@login_required
def listar_urnas(request):
    urnas = Urna.objects.all()
    return render(request, 'logisApp/listar_urnas.html', {'urnas': urnas})

@login_required
def listar_materiais(request):
    materiais = MaterialEleitoral.objects.all()
    return render(request, 'logisApp/listar_materiais.html', {'materiais': materiais})

@login_required
def listar_zonas(request):
    zonas = ZonaEleitoral.objects.all()
    urnas = Urna.objects.all()
    context = {
        'zonas': zonas,
        'urnas': urnas,
    }
    return render(request, 'logisApp/listar_zonas.html', context)

@login_required
def remover_municipio(request):
    if request.method == 'POST':
        municipio_id = request.POST.get('municipio_id')
        municipio = get_object_or_404(Municipio, id=municipio_id)
        municipio.delete()
        messages.success(request, f'O município {municipio.nome} foi removido com sucesso.')
        return redirect('remover_municipio')
    
    municipios = Municipio.objects.all()
    return render(request, 'logisApp/remover_municipio.html', {'municipios': municipios})

@login_required
def remover_urnas(request):
    if request.method == 'POST':
        urna_id = request.POST.get('urna_id')
        urna = get_object_or_404(Urna, id=urna_id)
        urna.delete()
        messages.success(request, f'A urna {urna.modelo} foi removida com sucesso')
        return redirect('remover_urnas')
    
    urnas = Urna.objects.all()
    return render(request, 'logisApp/remover_urnas.html', {'urnas': urnas})

@login_required
def remover_materiais(request):
    if request.method == 'POST':
        material_id = request.POST.get('material_id')
        material = get_object_or_404(MaterialEleitoral, id=material_id)
        material.delete()
        messages.success(request, f'O material {material.nome} foi removido com sucesso.')
        return redirect('remover_materiais')
    
    materiais = MaterialEleitoral.objects.all()
    return render(request, 'logisApp/remover_materiais.html', {'materiais': materiais})

@login_required
def remover_zonas(request):
    if request.method == 'POST':
        zona_id = request.POST.get('zona_id')
        zona = get_object_or_404(ZonaEleitoral, id=zona_id)
        zona.delete()
        messages.success(request, f'A zona {zona.nome} foi removida com sucesso.')
        return redirect('remover_zonas')
    
    zonas = ZonaEleitoral.objects.all()
    return render(request, 'logisApp/remover_zonas.html', {'zonas': zonas})


@login_required
def criar_distribuicao(request):
    if request.method == 'POST':
        # Cria um formulário com os dados do POST
        form = DistribuicaoForm(request.POST)
        if form.is_valid():
            distribuicao = form.save(commit=False)
            distribuicao.distributed_by = request.user  # Define o usuário que fez a distribuição
            distribuicao.save()

            # Processa as solicitações e atualiza os logs
            urna_model = form.cleaned_data.get('urna_model')
            quantidade = form.cleaned_data.get('quantidade')

            if urna_model and quantidade:
                urnas = Urna.objects.filter(modelo=urna_model)
                for urna in urnas:
                    if urna.qtd >= quantidade:
                        urna.qtd -= quantidade
                        urna.save()
                        DistributionLog.objects.create(
                            distribuicao=distribuicao,
                            urna=urna,
                            quantity=quantidade,
                            distribution_type='MRV'  # Ou 'CONT' se for o caso
                        )
                        break  # Interrompe o loop se a quantidade foi atendida
            
            messages.success(request, 'Distribuição criada com sucesso.')
            return redirect('listar_distribuicoes')  # Redireciona para a lista de distribuições ou outra página
    else:
        # Cria um formulário vazio
        form = DistribuicaoForm()
    
    return render(request, 'logisApp/criar_distribuicao.html', {'form': form})


@login_required
def criar_solicitacao(request):
    if request.method == 'POST':
        # Cria um formulário com os dados do POST
        form = SolicitacaoForm(request.POST)
        if form.is_valid():
            # Salva a solicitação
            solicitacao = form.save(commit=False)
            solicitacao.distribution = None  # Defina a distribuição se necessário
            solicitacao.save()
            messages.success(request, f'Solicitação de {solicitacao.quantidade} urna(s) criada com sucesso.')
            return redirect('listar_solicitacoes')  # Redireciona para a lista de solicitações ou outra página
    else:
        # Cria um formulário vazio
        form = SolicitacaoForm()
    
    return render(request, 'logisApp/criar_solicitacao.html', {'form': form})
