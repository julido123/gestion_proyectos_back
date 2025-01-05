from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account


class AccountAdmin(UserAdmin):
    model = Account

    # Configuración de campos al crear un usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'nombre', 'apellido', 'cedula', 'email', 
                'area_encargada', 'es_gerente', 'username', 'password1', 'password2',
                'is_admin', 'is_staff', 'is_active', 'is_superadmin',
            ),
        }),
    )

    # Configuración de campos al editar un usuario
    fieldsets = (
        ('Información personal', {
            'fields': (
                'nombre', 'apellido', 'cedula', 'username', 'email',
                'area_encargada', 'es_gerente', 'password',
            ),
        }),
        ('Permisos', {
            'fields': ('is_admin', 'is_staff', 'is_active', 'is_superadmin', 'user_type'),
        }),
    )

    # Configuración de la lista de usuarios
    list_display = ('username', 'email', 'nombre', 'area_encargada', 'user_type')
    list_filter = ('is_admin', 'user_type', 'is_staff', 'is_active')  # Elimina referencias a 'is_superuser' y 'groups'
    search_fields = ('username', 'email', 'nombre', 'apellido')
    ordering = ('username',)

    # Quitar referencias a 'groups' y 'user_permissions'
    filter_horizontal = ()  # Deja vacío, ya que no usas estos campos

admin.site.register(Account, AccountAdmin)



#admin.site.register(Account)
