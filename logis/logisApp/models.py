from django.contrib import admin
from django.db import models
from django.core.exceptions import ValidationError
import datetime

class Municipio(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class ZonaEleitoral(models.Model):
    nome = models.CharField(max_length=100)
    qtdSecoes = models.IntegerField(default=0)
    qtdUrnasEstoque = models.IntegerField(default=0)
    qtdUrnasMRV = models.IntegerField(default=0)
    qtdUrnasCont = models.IntegerField(default=0)

    def __str__(self):
        return self.nome

class MunicipioZona(models.Model):
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    zona = models.ForeignKey(ZonaEleitoral, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.municipio.nome} - {self.zona.nome}"

def validate_year(value):
    current_year = datetime.datetime.now().year
    if not (1900 <= value <= current_year):
        raise ValidationError(f'{value} não é um ano válido!')

class Urna(models.Model):
    MODELO_URNAS = [
        ('2008', '2008'),
        ('2010', '2010'),
        ('2012', '2012'),
        ('2015', '2015'),
        ('2018', '2018'),
        ('2020', '2020'),
        ('2023', '2023'),
    ]
    modelo = models.CharField(
        max_length=4,
        choices=MODELO_URNAS
    )
    bio = models.BooleanField(default=True)  # Suporte a biometria
    zona_eleitoral = models.ForeignKey(ZonaEleitoral, on_delete=models.CASCADE)  # Urna pertence a uma zona eleitoral
    qtd = models.IntegerField(default=0)

    def __str__(self):
        return self.modelo

class MaterialEleitoral(models.Model):
    TIPO_CHOICES = [
        ('UE', 'Urna Eletrônica'),
        ('Cabine', 'Cabine de Votação'),
        ('Bateria', 'Bateria'),
        ('MidiaResultado', 'Mídia de Resultado'),
        ('MidiaAplicacao', 'Mídia de Aplicação'),
        ('CaboFast', 'Cabo Fast'),
        ('CaboJacare', 'Cabo Jacaré'),
        ('CaboUSB', 'Cabo USB'),
        ('LeitorFlash', 'Leitor de Flash'),
        ('Reposicao', 'Componente de Reposição'),
    ]
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    quantidade = models.IntegerField()

    def __str__(self):
        return f"{self.nome} ({self.tipo})"

class ZE_solicita_urna(models.Model):
    zona_eleitoral = models.ForeignKey(ZonaEleitoral, on_delete=models.CASCADE)
    urna = models.ForeignKey(Urna, on_delete=models.CASCADE)
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    quantidade = models.IntegerField()

    def __str__(self):
        return f"{self.zona_eleitoral.nome} solicitou {self.quantidade} urna(s)"

class SolicitaMaterial(models.Model):
    zona_eleitoral = models.ForeignKey(ZonaEleitoral, on_delete=models.CASCADE)
    material = models.ForeignKey(MaterialEleitoral, on_delete=models.CASCADE)
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    quantidade = models.IntegerField()

    def __str__(self):
        return f"{self.zona_eleitoral.nome} solicitou {self.quantidade} {self.material.nome}(s)"

class Manutencao(models.Model):
    urna = models.ForeignKey(Urna, on_delete=models.CASCADE)
    data_manutencao = models.DateTimeField()
    descricao = models.TextField()
    tecnico_responsavel = models.CharField(max_length=200)

    def __str__(self):
        return f"Manutenção {self.urna.modelo} em {self.data_manutencao}"
