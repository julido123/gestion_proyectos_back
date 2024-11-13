from rest_framework import serializers
from accounts.models import Account

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['username', 'email', 'password', 'nombre', 'apellido', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        if Account.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'error': 'El email del usuario ya existe'})
        
        # Crear el usuario sin la segunda llamada a set_password
        account = Account.objects.create_user(
            nombre=self.validated_data['nombre'],
            apellido=self.validated_data['apellido'],
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            password=self.validated_data['password'],
        )
        #account.set_password(self.validated_data['password'])
        account.save()
        return account