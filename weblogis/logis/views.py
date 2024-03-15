from django.shortcuts import render

def index(request):
    return render(request, 'logis/index.html')

def cadastrar_municipio(request):
    return render(request, 'logis/cadastrar_municipio.html')
	
def cadastrar_ze(request):
    return render(request, 'logis/cadastrar_ze.html')

def alterar_municipio(request):
    return render(request, 'logis/alterar_municipio.html')

def alterar_ze(request):
    return render(request, 'logis/alterar_ze.html')
	
def gerar_solicitacao_urnas(request):
    return render(request, 'logis/geraSolic.html')
