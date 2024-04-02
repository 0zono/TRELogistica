from django.shortcuts import render, redirect
from .models import ZE_solicita_UE, Municipios
from .forms import MunicipioForm, ZEForm
from math import ceil

def index(request):
    return render(request, 'logis/index.html')

def cadastrar_municipio(request):
    return render(request, 'logis/cadastrar_municipio.html')
    
def cadastrar_ze(request):
    if request.method == 'POST':
        form = ZEForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/logis/')  # Redirect to the homepage after adding the ZE
    else:
        form = ZEForm()
    return render(request, 'logis/adicionar_ZE.html', {'form': form})

def alterar_municipio(request):
    return render(request, 'logis/alterar_municipio.html')

def alterar_ze(request):
    return render(request, 'logis/alterar_ze.html')
    
def gerar_solicitacao_urnas(request):
    municipios = Municipios.objects.all()  # Retrieve all municipalities
    context = {
        'municipios': municipios,
    }
    return render(request, 'logis/gerar_solicitacao_urnas.html', context)

def solicitar_ue(cls, municipio_id):
    try:
        municipio_selected = Municipios.objects.get(muni_id=municipio_id)
        x = municipio_selected.qtd_secao + municipio_selected.mrjs + municipio_selected.qtd_ue_cont

        nova_solicitacao = ZE_solicita_UE(
            municipio=municipio_selected,
            unidade_eleitoral=municipio_selected.zona_eleitoral,
            qtd=x,
            mrj=False,
            contingencia=True
        )
        nova_solicitacao.save()
        message = "Nova solicitação criada com sucesso."
        return message, nova_solicitacao
    except Municipios.DoesNotExist:
        message = "Município com o ID especificado não encontrado."
        return message, None

def solicitar_cont(cls, municipio_id):
    try:
        municipio_selected = Municipios.objects.get(muni_id=municipio_id)
        x = ceil(municipio_selected.qtd_secao * 0.12)
        nova_solicitacao_cont = ZE_solicita_UE(
            municipio=municipio_selected,
            unidade_eleitoral=municipio_selected.zona_eleitoral,
            qtd=x,
            mrj=False,
            contingencia=True
        )
        nova_solicitacao_cont.save()
        message = "Nova solicitação de urnas de contingência criada com sucesso."
        return message, nova_solicitacao_cont
    except Municipios.DoesNotExist:
        message = "Município com o ID especificado não encontrado."
        return message, None

def adicionar_municipio(request):
    if request.method == 'POST':
        form = MunicipioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/logis/') 
    else:
        form = MunicipioForm()
    
    context = {
        'form': form,
    }
    return render(request, 'logis/adicionar_municipio.html', context)
