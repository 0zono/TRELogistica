from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Municipio, Urna, ZonaEleitoral, MunicipioZona, Solicitacao, Distribuicao, DistributionLog
from django.db.models import Sum
from django.http import JsonResponse


def index(request):
    zonas = ZonaEleitoral.objects.all()
    urnas = Urna.objects.all()
    municipios = Municipio.objects.all()
    municipios_zonas = MunicipioZona.objects.all()
    solicitacoes_urnas = Solicitacao.objects.all()

    # Calcular total de seções
    total_secoes = sum(zona.qtdSecoes for zona in zonas)

    # Calcular total de urnas em estoque para a zona com id = 58
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

@login_required
def distribuir_manual(request):
    if request.method == 'POST':
        zona_estoque_id = request.POST.get('zona_estoque_id')
        zonas_ids = request.POST.getlist('zonas_ids')
        tipo_urna = request.POST.get('tipo_urna')  # 'primario', 'contingencia', or 'ambos'
        urna_modelo = request.POST.get('urna_modelo')

        if not zona_estoque_id or not zonas_ids or not tipo_urna or not urna_modelo:
            return JsonResponse({'messages': ['Dados insuficientes para a distribuição.']}, status=400)

        try:
            zona_estoque = ZonaEleitoral.objects.get(id=zona_estoque_id)
        except ZonaEleitoral.DoesNotExist:
            return JsonResponse({'messages': ['Zona de estoque não encontrada.']}, status=404)

        distribuicao = Distribuicao.objects.create(distributed_by=request.user, stock_zone=zona_estoque)
        urnas_estoque = Urna.objects.filter(zona_eleitoral=zona_estoque, modelo=urna_modelo).order_by('-modelo')
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
                    messages.append(f"Zona com ID {zona_id} não encontrada.")
                    continue

        # Fazer a distribuição manual
        for zona_id in zonas_ids:
            try:
                zona = ZonaEleitoral.objects.get(id=zona_id)
            except ZonaEleitoral.DoesNotExist:
                messages.append(f"Zona com ID {zona_id} não encontrada.")
                continue

            urnas_distribuidas = {}
            if tipo_urna in ['primario', 'ambos']:
                qtd_urnas_necessarias = zona.qtdSecoes

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

                zona.qtdUrnasMRV = sum(urnas_distribuidas.values())
                zona.qtdUrnasEstoque = zona.qtdUrnasMRV
                zona.save()

                for modelo, quantidade in urnas_distribuidas.items():
                    urna_queryset = Urna.objects.filter(modelo=modelo, zona_eleitoral=zona_estoque)
                    if urna_queryset.exists() and quantidade > 0:
                        urna = urna_queryset.first()
                        Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=quantidade, distribution=distribuicao)
                        Urna.objects.create(modelo=modelo, bio=urna.bio, zona_eleitoral=zona, qtd=quantidade)
                        DistributionLog.objects.create(distribuicao=distribuicao, urna=urna, quantity=quantidade, distribution_type='PRIMARIO')

            if tipo_urna in ['contingencia', 'ambos']:
                qtd_contingencia_necessarias = int(zona.qtdSecoes * 0.12)
                urnas_distribuidas = {}

                for urna in urnas_estoque:
                    if qtd_contingencia_necessarias > 0 and urna.qtd > 0:
                        if urna.qtd >= qtd_contingencia_necessarias:
                            urnas_distribuidas[urna.modelo] = qtd_contingencia_necessarias
                            urna.qtd -= qtd_contingencia_necessarias
                            qtd_contingencia_necessarias = 0
                        else:
                            urnas_distribuidas[urna.modelo] = urna.qtd
                            qtd_contingencia_necessarias -= urna.qtd
                            urna.qtd = 0
                        urna.save()

                zona.qtdUrnasCont = sum(urnas_distribuidas.values())
                zona.qtdUrnasEstoque += zona.qtdUrnasCont
                zona.save()

                for modelo, quantidade in urnas_distribuidas.items():
                    urna_queryset = Urna.objects.filter(modelo=modelo, zona_eleitoral=zona_estoque)
                    if urna_queryset.exists() and quantidade > 0:
                        urna = urna_queryset.first()
                        Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=quantidade, distribution=distribuicao)
                        Urna.objects.create(modelo=modelo, bio=urna.bio, zona_eleitoral=zona, qtd=quantidade)
                        DistributionLog.objects.create(distribuicao=distribuicao, urna=urna, quantity=quantidade, distribution_type='CONTINGENCIA')

        # Automatic distribution for remaining zones
        remaining_zonas = ZonaEleitoral.objects.exclude(id__in=zonas_ids).exclude(id=zona_estoque_id)
        for zona in remaining_zonas:
            urnas_distribuidas = {}
            qtd_urnas_necessarias = zona.qtdSecoes
            qtd_contingencia_necessarias = int(qtd_urnas_necessarias * 0.12)

            # Distribute primary urnas
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

            zona.qtdUrnasMRV = sum(urnas_distribuidas.values())
            zona.qtdUrnasEstoque = zona.qtdUrnasMRV
            zona.save()

            for modelo, quantidade in urnas_distribuidas.items():
                urna_queryset = Urna.objects.filter(modelo=modelo, zona_eleitoral=zona_estoque)
                if urna_queryset.exists() and quantidade > 0:
                    urna = urna_queryset.first()
                    Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=quantidade, distribution=distribuicao)
                    Urna.objects.create(modelo=modelo, bio=urna.bio, zona_eleitoral=zona, qtd=quantidade)
                    DistributionLog.objects.create(distribuicao=distribuicao, urna=urna, quantity=quantidade, distribution_type='PRIMARIO')

            urnas_distribuidas = {}

            # Distribute contingency urnas
            for urna in urnas_estoque:
                if qtd_contingencia_necessarias > 0 and urna.qtd > 0:
                    if urna.qtd >= qtd_contingencia_necessarias:
                        urnas_distribuidas[urna.modelo] = qtd_contingencia_necessarias
                        urna.qtd -= qtd_contingencia_necessarias
                        qtd_contingencia_necessarias = 0
                    else:
                        urnas_distribuidas[urna.modelo] = urna.qtd
                        qtd_contingencia_necessarias -= urna.qtd
                        urna.qtd = 0
                    urna.save()

            zona.qtdUrnasCont = sum(urnas_distribuidas.values())
            zona.qtdUrnasEstoque += zona.qtdUrnasCont
            zona.save()

            for modelo, quantidade in urnas_distribuidas.items():
                urna_queryset = Urna.objects.filter(modelo=modelo, zona_eleitoral=zona_estoque)
                if urna_queryset.exists() and quantidade > 0:
                    urna = urna_queryset.first()
                    Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=quantidade, distribution=distribuicao)
                    Urna.objects.create(modelo=modelo, bio=urna.bio, zona_eleitoral=zona, qtd=quantidade)
                    DistributionLog.objects.create(distribuicao=distribuicao, urna=urna, quantity=quantidade, distribution_type='CONTINGENCIA')

        return JsonResponse({'messages': messages})

    zonas = ZonaEleitoral.objects.all().order_by('id')
    urna_modelos = Urna.objects.values('modelo').distinct().filter(zona_eleitoral__isnull=False)
    return render(request, 'logisApp/distribuir_manual.html', {'zonas': zonas, 'urna_modelos': urna_modelos})


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
            return JsonResponse({'messages': ['Zona de estoque não selecionada.']}, status=400)
        
        try:
            zona_estoque = ZonaEleitoral.objects.get(id=zona_estoque_id)
        except ZonaEleitoral.DoesNotExist:
            return JsonResponse({'messages': ['Zona de estoque não encontrada.']}, status=404)

        urnas_estoque = Urna.objects.filter(zona_eleitoral=zona_estoque).order_by('-modelo')
        urnas_distribuidas = {}

        # Reset quantities of urnas in other zones
        for zona in ZonaEleitoral.objects.exclude(id=zona_estoque_id):
            zona.qtdUrnasMRV = 0
            zona.qtdUrnasCont = 0
            zona.qtdUrnasEstoque = 0
            zona.save()

        # Calculate total urnas needed
        total_urnas_needed = sum(zona.qtdSecoes for zona in ZonaEleitoral.objects.exclude(id=zona_estoque_id))
        total_contingency_needed = int(total_urnas_needed * 0.12)

        # Distribute primary urnas
        for urna in urnas_estoque:
            if total_urnas_needed > 0 and urna.qtd > 0:
                if urna.qtd >= total_urnas_needed:
                    urnas_distribuidas[urna.modelo] = total_urnas_needed
                    urna.qtd -= total_urnas_needed
                    total_urnas_needed = 0
                else:
                    urnas_distribuidas[urna.modelo] = urna.qtd
                    total_urnas_needed -= urna.qtd
                    urna.qtd = 0
                urna.save()

        # Log primary urnas distribution
        distribuicao = Distribuicao.objects.create(distributed_by=request.user, stock_zone=zona_estoque)
        for modelo, quantidade in urnas_distribuidas.items():
            urna_queryset = Urna.objects.filter(modelo=modelo, zona_eleitoral=zona_estoque)
            if urna_queryset.exists() and quantidade > 0:
                urna = urna_queryset.first()
                for zona in ZonaEleitoral.objects.exclude(id=zona_estoque_id):
                    qtd_urna_per_zone = min(zona.qtdSecoes, quantidade)
                    Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=qtd_urna_per_zone, distribution=distribuicao)
                    Urna.objects.create(modelo=modelo, bio=urna.bio, zona_eleitoral=zona, qtd=qtd_urna_per_zone)
                    DistributionLog.objects.create(distribuicao=distribuicao, urna=urna, quantity=qtd_urna_per_zone, distribution_type='PRIMARIO')
                    quantidade -= qtd_urna_per_zone
                    if quantidade == 0:
                        break

        # Distribute contingency urnas
        urnas_distribuidas.clear()
        for urna in urnas_estoque:
            if total_contingency_needed > 0 and urna.qtd > 0:
                if urna.qtd >= total_contingency_needed:
                    urnas_distribuidas[urna.modelo] = total_contingency_needed
                    urna.qtd -= total_contingency_needed
                    total_contingency_needed = 0
                else:
                    urnas_distribuidas[urna.modelo] = urna.qtd
                    total_contingency_needed -= urna.qtd
                    urna.qtd = 0
                urna.save()

        # Log contingency urnas distribution
        for modelo, quantidade in urnas_distribuidas.items():
            urna_queryset = Urna.objects.filter(modelo=modelo, zona_eleitoral=zona_estoque)
            if urna_queryset.exists() and quantidade > 0:
                urna = urna_queryset.first()
                for zona in ZonaEleitoral.objects.exclude(id=zona_estoque_id):
                    qtd_urna_per_zone = min(int(zona.qtdSecoes * 0.12), quantidade)
                    Solicitacao.objects.create(zona_eleitoral=zona, urna=urna, quantidade=qtd_urna_per_zone, distribution=distribuicao)
                    Urna.objects.create(modelo=modelo, bio=urna.bio, zona_eleitoral=zona, qtd=qtd_urna_per_zone)
                    DistributionLog.objects.create(distribuicao=distribuicao, urna=urna, quantity=qtd_urna_per_zone, distribution_type='CONTINGENCIA')
                    quantidade -= qtd_urna_per_zone
                    if quantidade == 0:
                        break

        return JsonResponse({'messages': ['Distribuição concluída com sucesso.']})
    
    zonas = ZonaEleitoral.objects.all().order_by('id')
    return render(request, 'logisApp/solicitar_tudo.html', {'zonas': zonas})
