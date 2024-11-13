from rest_framework import serializers
from .models import Idea, Sede, Area, Calificacion
from django.contrib.auth import get_user_model
from accounts.models import Account

User = get_user_model()

class IdeaSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')  # Solo lectura, el usuario se asigna en la vista
    sede = serializers.CharField()
    area = serializers.CharField()

    class Meta:
        model = Idea
        fields = ['id', 'titulo', 'descripcion', 'usuario', 'tipo', 'sede', 'area', 'estado']
        read_only_fields = ['fecha_creacion', 'usuario']

    def validate_sede(self, value):
        try:
            return Sede.objects.get(nombre=value)
        except Sede.DoesNotExist:
            raise serializers.ValidationError("Sede no encontrada")

    def validate_area(self, value):
        try:
            return Area.objects.get(nombre=value)
        except Area.DoesNotExist:
            raise serializers.ValidationError("Área no encontrada")

    def create(self, validated_data):
        # Reemplaza los valores de 'sede' y 'area' por las instancias correspondientes
        validated_data['sede'] = validated_data.pop('sede')
        validated_data['area'] = validated_data.pop('area')
        return super().create(validated_data)
    

####################################


class CalificacionSerializer(serializers.ModelSerializer):
    usuario = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True 
    )
    idea = serializers.PrimaryKeyRelatedField(queryset=Idea.objects.all())
    promedio = serializers.FloatField(read_only=True)  # Eliminar `source='promedio'`

    class Meta:
        model = Calificacion
        fields = ['idea', 'usuario', 'factibilidad', 'viabilidad', 'impacto', 'comentario', 'promedio', 'puntuacion_general']
####################################


class AccountRankingSerializer(serializers.ModelSerializer):
    total_ideas = serializers.IntegerField()
    promedio_calificacion = serializers.FloatField()

    class Meta:
        model = Account
        fields = ['username', 'total_ideas', 'promedio_calificacion']




class SedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = ['id', 'nombre']


class AreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Area
        fields = ['id', 'nombre']