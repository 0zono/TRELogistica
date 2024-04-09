from django.shortcuts import render, redirect
from .models import ZE_solicita_UE, Municipios, UE
from .forms import MunicipioForm, ZEForm, secaoForm
from math import ceil

def index(request):
    return render(request, 'logis/index.html')
    
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
    if request.method == 'GET':
        municipio_id = request.GET.get('municipio_id')
        if municipio_id:
            message_ue, nova_solicitacao_ue = solicitar_ue(municipio_id)
            message_cont, nova_solicitacao_cont = solicitar_cont(municipio_id)
            context = {
                'message_ue': message_ue,
                'message_cont': message_cont,
                'nova_solicitacao_ue': nova_solicitacao_ue,
                'nova_solicitacao_cont': nova_solicitacao_cont,
            }
            return render(request, 'logis/gerar_solicitacao_urnas.html', context)

    municipios = Municipios.objects.all()
    context = {
        'municipios': municipios,
    }
    return render(request, 'logis/gerar_solicitacao_urnas.html', context)

def solicitar_ue(municipio_id):
    try:
        municipio_selected = Municipios.objects.get(muni_id=municipio_id)
        x = municipio_selected.qtd_secao + municipio_selected.mrjs + municipio_selected.qtd_ue_cont
        modelo_ue = UE.objects.get(modelo='2020')  # Modify this line to select the appropriate UE model instance
        nova_solicitacao = ZE_solicita_UE(
            municipio=municipio_selected,
            modelo_ue=modelo_ue,
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

def solicitar_cont(municipio_id):
    try:
        municipio_selected = Municipios.objects.get(muni_id=municipio_id)
        x = ceil(municipio_selected.qtd_secao * 0.12)
        modelo_ue = UE.objects.get(modelo='2020')  # Modify this line to select the appropriate UE model instance
        nova_solicitacao_cont = ZE_solicita_UE(
            municipio=municipio_selected,
            modelo_ue=modelo_ue,
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

def adicionar_secao(request):
    if request.method == 'POST':
        form = secaoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/logis/') 
    else:
        form = secaoForm()
    
    context = {
        'form': form,
    }
    return render(request, 'logis/adicionar_secao.html', context)