# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class MyAccountManager(BaseUserManager):
    def create_user(self, nombre, apellido, username, email, password=None, cedula=None):
        if not email:
            raise ValueError('El usuario debe tener un email')
        if not username:
            raise ValueError('El usuario debe tener un username')
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            nombre=nombre,
            apellido=apellido,
            cedula=cedula,
        )
        
        # Configuramos la contraseña encriptada aquí
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

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
    def save(self, *args, **kwargs):
        if self._state.adding:  # Significa que es un nuevo usuario
            self.set_password(self.password)  
        super(Account, self).save(*args, **kwargs)
