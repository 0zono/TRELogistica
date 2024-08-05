from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Municipio, Urna, MaterialEleitoral, ZonaEleitoral, MunicipioZona, Secao, DistributionLog
from ..forms import MunicipioForm, UrnaForm, MaterialEleitoralForm, ZonaEleitoralForm, UploadFileForm, DistribuicaoUrnaForm
from django.db.models import Sum, Count
from ..models import ZonaEleitoral, Urna, Solicitacao
from django.http import JsonResponse
import logging
import pandas as pd
from django.core.files.storage import FileSystemStorage

from django.contrib import messages
import json

logger = logging.getLogger(__name__)

def qtd_urnas_necessarias(zona):
    return zona.qtdSecoes

def qtd_cont_necessarias(zona):
    return int(zona.qtdSecoes * 0.15)

def get_qtd_urnas(zona):
    return Solicitacao.objects.filter(zona_eleitoral=zona).aggregate(total=Sum('quantidade'))['total'] or 0

def get_qtd_cont(zona):
    return 0

#Não está sendo utilizado atualmente, será ao alterar a View distribuir_tudo
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

def is_compatible(primary_model, cont_model):
    if primary_model == '2020':
        return cont_model in ['2020', '2023']
    if cont_model == '2020':
        return primary_model in ['2020', '2023']
    return True

@login_required
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
        form = ZonaEleitoralForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_zonas')
    else:
        form = ZonaEleitoralForm()
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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from ..models import ZonaEleitoral, Urna, Solicitacao, DistributionLog

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

        zonas = ZonaEleitoral.objects.exclude(id=zona_estoque_id).order_by('id')
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
                    if urna_queryset.exists():
                        urna = urna_queryset.first()
                        Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=quantidade)
                        Urna.objects.create(modelo=modelo, bio=urna.bio, zona_eleitoral=zona, qtd=quantidade)
                        DistributionLog.objects.create(zona_eleitoral=zona, urna=urna, quantity=quantidade, distributed_by=request.user, distribution_type='MRV')

                for modelo, quantidade in urnas_contingencia_distribuidas.items():
                    urna_queryset = Urna.objects.filter(modelo=modelo, zona_eleitoral=zona_estoque)
                    if urna_queryset.exists():
                        urna = urna_queryset.first()
                        Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=quantidade)
                        Urna.objects.create(modelo=modelo, bio=urna.bio, zona_eleitoral=zona, qtd=quantidade)
                        DistributionLog.objects.create(zona_eleitoral=zona, urna=urna, quantity=quantidade, distributed_by=request.user, distribution_type='CONT')

        return JsonResponse({'messages': messages})

    zonas = ZonaEleitoral.objects.all()
    return render(request, 'logisApp/solicitar_tudo.html', {'zonas': zonas})


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

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_path = fs.path(filename)

            if 'zonamun' in filename.lower():
                if check_all_tables_have_rows():
                    delete_existing_data()
                import_zonamun_data(file_path)
            elif 'secoes' in filename.lower():
                if check_all_tables_have_rows():
                    delete_existing_data()
                import_secoes_data(file_path)

            return redirect('upload_success')
    else:
        form = UploadFileForm()
    return render(request, 'logisApp/upload.html', {'form': form})

def check_all_tables_have_rows():
    return (
        ZonaEleitoral.objects.exists() and
        Municipio.objects.exists() and
        Secao.objects.exists()
    )

def delete_existing_data():
    ZonaEleitoral.objects.all().delete()
    Municipio.objects.all().delete()
    Secao.objects.all().delete()

def import_zonamun_data(file_path):
    zonamun_df = pd.read_excel(file_path)
    for _, row in zonamun_df.iterrows():
        cod_mun = row['COD_MUNIC']
        nome_municipio = row['NOM_MUNIC']

        municipio, created = Municipio.objects.get_or_create(
            cod=cod_mun,
            defaults={'nome': nome_municipio}
        )
        if not created:
            municipio.nome = nome_municipio
            municipio.save()

        zona, _ = ZonaEleitoral.objects.get_or_create(nome=str(row['COD_ZONA']))
        MunicipioZona.objects.get_or_create(municipio=municipio, zona=zona)

def import_secoes_data(file_path):
    secoes_df = pd.read_excel(file_path)
    for _, row in secoes_df.iterrows():
        zona_nome = str(row['COD_ZONA'])
        try:
            zona = ZonaEleitoral.objects.get(nome=zona_nome)
        except ZonaEleitoral.DoesNotExist:
            continue

        Secao.objects.create(
            cod_zona=zona,
            cod_municipio=str(row['COD_MUNIC']),
            cod_local=str(row['COD_LOCAL']),
            cod_secao=str(row['COD_SECAO']),
            ind_especial=str(row['IND_ESPECIAL'])
        )

        zona.qtdSecoes += 1
        zona.save()

@login_required
def listar_distribuicoes(request):
    distribuicoes = DistributionLog.objects.all()
    print(distribuicoes + "/n")  # Verifique os dados no console
    return render(request, 'logisApp/listar_distribuicoes.html', {'logs': distribuicoes})




