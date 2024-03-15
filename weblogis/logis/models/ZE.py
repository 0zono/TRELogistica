from django.db import models
import datetime
from django.utils import timezone

class ZE(models.Model):
	idZE = models.CharField(max_length=20, unique=True, verbose_name="Identificador da Zona Eleitoral")
	qtdEleitoresAptos = models.IntegerField(verbose_name="Quantidade de Eleitores Aptos")
	
	def __str__(self):
        	return self.idZE
#problemas com o Meta nesse model
class Meta:
    verbose_name = "Zona Eleitoral"
    verbose_name_plural = "Zonas Eleitorais"