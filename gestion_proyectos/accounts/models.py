# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.forms import ValidationError
from propuestas.models import Area


class MyAccountManager(BaseUserManager):
    def create_user(
        self, 
        nombre, 
        apellido, 
        username, 
        email, 
        password=None, 
        cedula=None, 
        area_encargada=None, 
        es_gerente=False
    ):
        if not email:
            raise ValueError('El usuario debe tener un email')
        if not username:
            raise ValueError('El usuario debe tener un username')
        
        # Validaciones para evitar configuraciones incorrectas
        if es_gerente and area_encargada:
            raise ValueError("Un gerente no puede estar asignado a un área.")
        if area_encargada and not es_gerente:
            raise ValueError("Un encargado de área debe ser marcado como gerente.")
        
        # Crear el usuario con los datos básicos
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            nombre=nombre,
            apellido=apellido,
            cedula=cedula,
            area_encargada=area_encargada,
            es_gerente=es_gerente,
        )
        
        # Configurar atributos adicionales según el rol
        if area_encargada:  # Es encargado de área
            user.user_type = 'ADMIN'
            user.is_admin = True
        elif es_gerente:  # Es gerente
            user.user_type = 'ADMIN'
            user.is_admin = True
        else:  # Es empleado
            user.user_type = 'EMPLEADO'
            user.is_admin = False
            user.is_staff = False

        # Configurar y encriptar la contraseña
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, nombre, apellido, username, email, password, cedula=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,  # Aquí ya se encripta con set_password en create_user
            nombre=nombre,
            apellido=apellido,
            cedula=cedula
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    


class Account(AbstractBaseUser):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    cedula = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    area_encargada = models.OneToOneField(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name='encargado')
    es_gerente = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)

    USER_TYPE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('EMPLEADO', 'Empleado'),
    )
    user_type = models.CharField(choices=USER_TYPE_CHOICES, max_length=10, default='EMPLEADO')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'nombre', 'apellido', 'cedula']  

    objects = MyAccountManager()
    
    def clean(self):
        if self.es_gerente and self.area_encargada:
            raise ValidationError("Un gerente no puede estar asignado a un área.")

    
    def get_role(self):
        if self.user_type == 'GERENTE':
            return "Gerente"
        elif self.user_type == 'ENCARGADO':
            return f"Encargado de {self.area_encargada.nombre}"
        else:
            return "Empleado"

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
    def save(self, *args, **kwargs):
        if self.area_encargada:  # Si tiene área asignada, es encargado
            self.user_type = 'ADMIN'
            self.is_admin = True
        elif self.es_gerente:  # Si es gerente
            self.user_type = 'ADMIN'
            self.is_admin = True
        else:  # Si no es ni encargado ni gerente, es empleado
            self.user_type = 'EMPLEADO'
            self.is_admin = False
            self.is_staff = False
        
        # Aseguramos que la contraseña esté encriptada
        # if self._state.adding and self.password:  
        #     self.set_password(self.password)  

        super(Account, self).save(*args, **kwargs)
