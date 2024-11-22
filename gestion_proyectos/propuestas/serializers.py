from rest_framework import serializers
from .models import Idea, Sede, Area, Calificacion, ArchivoAdjunto
from django.contrib.auth import get_user_model
from accounts.models import Account


User = get_user_model()

class ArchivoAdjuntoSerializer(serializers.ModelSerializer):
    archivo_url = serializers.SerializerMethodField()

    class Meta:
        model = ArchivoAdjunto
        fields = ['id', 'archivo_url']

    def get_archivo_url(self, obj):
        # Genera la URL completa del archivo
        request = self.context.get('request')
        return request.build_absolute_uri(obj.archivo.url) if request else obj.archivo.url


class IdeaSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')
    sede = serializers.CharField()
    area = serializers.CharField()
    archivos = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Idea
        fields = ['id', 'usuario', 'titulo', 'descripcion', 'tipo', 'sede', 'area', 'estado', 'archivos']
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
        archivos = validated_data.pop('archivos', [])
        print("Archivos validados:", archivos)
        total_size = sum(file.size for file in archivos)
        max_total_size = 30 * 1024 * 1024  # 30 MB máximo

        if total_size > max_total_size:
            raise serializers.ValidationError("El tamaño total de los archivos excede el límite permitido de 30 MB.")

        # Crea la instancia de Idea
        idea = Idea.objects.create(**validated_data)

        # Guarda los archivos relacionados
        for archivo in archivos:
            ArchivoAdjunto.objects.create(idea=idea, archivo=archivo)

        return idea
    
    
    
class IdeaSinCalificarSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')
    sede = serializers.CharField(source='sede.nombre')
    area = serializers.CharField(source='area.nombre')
    archivos = ArchivoAdjuntoSerializer(source='archivos_adjuntos', many=True)

    class Meta:
        model = Idea
        fields = ['id', 'usuario', 'titulo', 'descripcion', 'tipo', 'sede', 'area', 'estado', 'archivos']
    

    

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
        
        
        
class CalificacionSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Calificacion
        fields = ['id', 'puntuacion_general', 'factibilidad', 'viabilidad', 'impacto', 'comentario']

        

####################################


class IdeaWithCalificationsSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')  # Solo lectura
    sede = serializers.CharField()
    area = serializers.CharField()
    calificaciones = CalificacionSerializer2(many=True, source='calificacion_set')
    fecha_creacion = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = ['id', 'fecha_creacion', 'usuario', 'titulo', 'descripcion', 'tipo', 'sede', 'area', 'estado', 'calificaciones']
        read_only_fields = ['usuario']

    def get_fecha_creacion(self, obj):
        # Formatea la fecha en día/mes/año
        return obj.fecha_creacion.strftime('%d/%m/%Y')

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

###################################3


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
        
        
        
class UpdateIdeaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = ['estado']  # Permitir solo la actualización del estado

class UpdateCalificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calificacion
        fields = ['factibilidad', 'viabilidad', 'impacto', 'puntuacion_general', 'comentario']  # Campos editables