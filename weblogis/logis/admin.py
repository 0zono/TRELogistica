from django.contrib import admin
from .models import Municipios
from .models import ZE
from .models import ZE_solicita_UE
from .models import UE
from .models import TSAT
from .models import Secao

admin.site.register(Municipios)
admin.site.register(ZE)
admin.site.register(ZE_solicita_UE)
admin.site.register(UE)
admin.site.register(TSAT)
admin.site.register(Secao)