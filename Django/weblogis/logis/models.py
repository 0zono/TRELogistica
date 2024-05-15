from django.db import models


class ZE(models.Model):
    idZE = models.CharField(max_length=20, primary_key=True, unique=True, verbose_name="identificador da zona eleitoral")
    qtdEleitoresAptos = models.IntegerField(verbose_name="Quantidade de Eleitores Aptos")

    class Meta:
        verbose_name = "ZonaEleitoral"
        verbose_name_plural = "Zonas Eleitorais"


class UE(models.Model):
    modelo = models.CharField(primary_key=True, unique=True, max_length = 4)
    bio = models.BooleanField()
    ativo = models.BooleanField()


class TSAT(models.Model):
    modelo = models.CharField(primary_key=True, unique=True, max_length = 4)
    quantidade = models.IntegerField()
    bio = models.BooleanField()
    ativo = models.BooleanField()


class Secao(models.Model):
    secao_id = models.AutoField(primary_key=True)
    municipio = models.ForeignKey('Municipios', on_delete=models.CASCADE, related_name='secoes')
    local_numero = models.IntegerField(verbose_name="Número do local da secao.")
    eletricidade_irregular = models.BooleanField(verbose_name="Eletricidade irregular")
    dificil_acesso = models.BooleanField(verbose_name="Acesso dificil?")

    class Meta:
        verbose_name = "secao"
        verbose_name_plural = "secoes"


class Municipios(models.Model):
    muni_id = models.AutoField(primary_key=True)
    zona_eleitoral = models.ForeignKey(ZE, on_delete=models.CASCADE, related_name='municipios')
    KM_Cuiaba = models.DecimalField(max_digits=10, decimal_places=2)
    sede = models.BooleanField(default=False)
    qtd_secao = models.IntegerField(default=0)  # Defina um valor padrão aqui
    mrjs = models.IntegerField(default=0)
    qtd_ue = models.IntegerField(default=0)
    qtd_ue_cont = models.IntegerField(default=0)
    nome = models.CharField(max_length=100, default="sem_nome")  

    class Meta:
        verbose_name_plural = "Municipios"





class ZE_solicita_UE(models.Model):
    solicitacao_id = models.AutoField(primary_key=True, unique=True)
    municipio = models.ForeignKey(Municipios, on_delete=models.CASCADE)
    modelo_ue = models.ForeignKey(UE, on_delete=models.CASCADE)
    qtd = models.IntegerField()
    mrj = models.BooleanField()
    contingencia = models.BooleanField()

