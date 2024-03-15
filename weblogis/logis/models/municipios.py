from django.db import models

class Municipio(models.Model):
    muni_id = models.AutoField(primary_key=True)
    zona_eleitoral = models.ForeignKey(ZonaEleitoral, on_delete=models.CASCADE, related_name='municipios')
    KM_Cuiaba = models.DecimalField(max_digits=10, decimal_places=2)
    sede = models.BooleanField(default=False)
    qtd_secao = models.IntegerField()

    class Meta:
        verbose_name = "Municipio"  # Nome exibido na interface administrativa do Django
        verbose_name_plural = "Municipios"  # Nome exibido na interface administrativa do Django