from django import forms
from .models import Municipio, Urna, MaterialEleitoral, ZonaEleitoral, MunicipioZona, Distribuicao, Solicitacao

class MunicipioForm(forms.ModelForm):
    class Meta:
        model = Municipio
        fields = ['nome']

class UrnaForm(forms.ModelForm):
    class Meta:
        model = Urna
        fields = ['modelo', 'bio', 'zona_eleitoral', 'qtd']

class MaterialEleitoralForm(forms.ModelForm):
    class Meta:
        model = MaterialEleitoral
        fields = ['nome', 'tipo', 'quantidade']



class UploadFileForm(forms.Form):
    file = forms.FileField()

class DistribuicaoUrnaForm(forms.Form):
    stock_zone = forms.ModelChoiceField(queryset=ZonaEleitoral.objects.all(), label="Zona de Estoque")
    modelo = forms.ChoiceField(choices=Urna.MODELO_URNAS, label="Modelo da Urna")
    quantidade = forms.IntegerField(min_value=1, label="Quantidade")
    is_contingency = forms.BooleanField(required=False, label="Contingência")

class ZonaDistributionForm(forms.ModelForm):
    distribuir = forms.BooleanField(required=False, label="Distribuir")
    primario = forms.BooleanField(required=False, label="Primário")
    contingencia = forms.BooleanField(required=False, label="Contingência")
    ambos = forms.BooleanField(required=False, label="Ambos")
    urna_model = forms.ModelChoiceField(queryset=Urna.objects.none(), label="Modelo da Urna")

    class Meta:
        model = ZonaEleitoral
        fields = ['distribuir', 'primario', 'contingencia', 'ambos', 'urna_model']

class DistribuicaoForm(forms.Form):
    distribuir = forms.BooleanField(required=False, label='Distribuir')
    primario = forms.BooleanField(required=False, label='Primário')
    contingencia = forms.BooleanField(required=False, label='Contingência')
    ambos = forms.BooleanField(required=False, label='Ambos')
    urna_model = forms.ChoiceField(choices=[], label='Modelo da Urna', required=False)
    quantidade = forms.IntegerField(min_value=1, required=True, label='Quantidade')

    def __init__(self, *args, **kwargs):
        urna_modelos = kwargs.pop('urna_modelos', {})
        super().__init__(*args, **kwargs)
        if 'zona_estoque_id' in kwargs:
            zona_estoque_id = kwargs['zona_estoque_id']
            if zona_estoque_id in urna_modelos:
                self.fields['urna_model'].choices = [(m, m) for m in urna_modelos[zona_estoque_id]]

DistribuicaoFormSet = forms.formset_factory(DistribuicaoForm, extra=1, max_num=10)
        
class DistribuicaoForm(forms.ModelForm):
    class Meta:
        model = Distribuicao
        fields = []  # Include fields you want to display or use in the form


class ZonaEleitoralForm(forms.ModelForm):
    distribuir = forms.BooleanField(required=False, label="Distribuir")
    primario = forms.BooleanField(required=False, label="Primário")
    contingencia = forms.BooleanField(required=False, label="Contingência")
    ambos = forms.BooleanField(required=False, label="Ambos")
    urna_model = forms.ModelChoiceField(queryset=Urna.objects.all(), required=False, label="Modelo da Urna")

    class Meta:
        model = ZonaEleitoral
        fields = ['nome', 'qtdSecoes', 'qtdUrnasEstoque', 'qtdUrnasMRV', 'qtdUrnasCont']

# Se `ZonaEleitoralFormSet` não está funcionando corretamente, tente ajustar a inicialização:
ZonaEleitoralFormSet = forms.modelformset_factory(ZonaEleitoral, form=ZonaEleitoralForm, extra=0, can_delete=True)

class ZonaEstoqueForm(forms.Form):
    zona_estoque = forms.ModelChoiceField(queryset=ZonaEleitoral.objects.all(), required=True, label="Zona de Estoque")

class AdicionarZonaEleitoralForm(forms.ModelForm):
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all(), required=True, label="Município")

    class Meta:
        model = ZonaEleitoral
        fields = ['nome', 'qtdSecoes', 'qtdUrnasEstoque', 'qtdUrnasMRV', 'qtdUrnasCont']

    def save(self, commit=True):
        zona = super().save(commit=commit)
        municipio = self.cleaned_data['municipio']
        MunicipioZona.objects.create(municipio=municipio, zona=zona)
        return zona


class SolicitacaoForm(forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = ['zona_eleitoral', 'urna', 'quantidade']


class DistribuicaoForm(forms.ModelForm):
    class Meta:
        model = Distribuicao
        fields = ['stock_zone']  # Ajuste conforme necessário
