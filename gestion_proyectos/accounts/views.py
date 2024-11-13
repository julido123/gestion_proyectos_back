from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from accounts.models import Account
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib import auth
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    data = {}
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        # Verificar si el usuario existe
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            data['error'] = "El usuario no existe"
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        # Autenticar la contraseña del usuario
        account = auth.authenticate(username=username, password=password)
        if account is not None:
            data['response'] = 'El login fue exitoso'
            data['username'] = account.username
            data['email'] = account.email
            data['nombre'] = account.nombre  # Agregado
            data['apellido'] = account.apellido  # Agregado
            data['user_type'] = account.user_type
            refresh = RefreshToken.for_user(account)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
            return Response(data)
        else:
            data['error'] = "Contraseña incorrecta"
            return Response(data, status=status.HTTP_400_BAD_REQUEST)