from rest_framework import serializers
from .models import Idea, Sede, Area, Calificacion, ArchivoAdjunto
from django.contrib.auth import get_user_model
from accounts.models import Account
from propuestas.services.idea_service import calcular_calificacion_definitiva 


User = get_user_model()

class ArchivoAdjuntoSerializer(serializers.ModelSerializer):
    archivo_url = serializers.SerializerMethodField()

    class Meta:
        model = ArchivoAdjunto
        fields = ['id', 'archivo_url']

    def get_archivo_url(self, obj):
        # Obtiene la URL completa del archivo
        url = obj.archivo.url
        # Reemplaza '/media/' con una cadena vacía, dejando solo la ruta relativa desde 'uploads/'
        if url.startswith('/media/'):
            return url.replace('/media/', '')
        return url


class IdeaSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField(source='usuario.username')
    sede = serializers.PrimaryKeyRelatedField(queryset=Sede.objects.all())
    area = serializers.PrimaryKeyRelatedField(queryset=Area.objects.all())
    archivos = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )


    class Meta:
        model = Idea
        fields = ['id', 'usuario', 'titulo', 'descripcion', 'tipo', 'sede', 'area', 'archivos']
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
    tipo = serializers.SerializerMethodField()
    estado_revision = serializers.SerializerMethodField()
    
    class Meta:
        model = Idea
        fields = ['id', 'fecha_creacion', 'usuario', 'titulo', 'descripcion', 'tipo', 'sede', 'area', 'archivos', 'estado_revision']

    def get_tipo(self, obj):
        return obj.get_tipo_display()

    def get_estado_revision(self, obj):
        return obj.get_estado_revision_display()


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Formatear la fecha
        if instance.fecha_creacion:
            representation['fecha_creacion'] = instance.fecha_creacion.strftime('%d/%m/%Y')
        return representation
    

    

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
    usuario = serializers.ReadOnlyField(source='usuario.username')
    sede = serializers.CharField()
    area = serializers.CharField()
    calificaciones = serializers.SerializerMethodField()  # Personalizamos las calificaciones
    fecha_creacion = serializers.SerializerMethodField()
    estado_ejecucion = serializers.SerializerMethodField()
    estado_revision = serializers.SerializerMethodField()
    tipo = serializers.SerializerMethodField()
    archivos = ArchivoAdjuntoSerializer(source='archivos_adjuntos', many=True)

    class Meta:
        model = Idea
        fields = [
            'id', 'fecha_creacion', 'usuario', 'titulo', 'descripcion', 'tipo',
            'sede', 'area', 'estado_ejecucion', 'estado_revision', 'calificaciones', 'archivos'
        ]
        read_only_fields = ['usuario']

    def get_calificaciones(self, obj):
        """Incluye las calificaciones del encargado, gerente y definitiva, ordenadas según el tipo de usuario."""
        calificaciones = Calificacion.objects.filter(idea=obj)
        encargado_calificacion = calificaciones.filter(tipo_calificacion='encargado').first()
        gerente_calificacion = calificaciones.filter(tipo_calificacion='gerente').first()

        # Formato para las calificaciones existentes
        calificaciones_list = []
        if encargado_calificacion:
            calificaciones_list.append({
                "tipo": "encargado",
                **CalificacionSerializer2(encargado_calificacion).data
            })
        if gerente_calificacion:
            calificaciones_list.append({
                "tipo": "gerente",
                **CalificacionSerializer2(gerente_calificacion).data
            })

        # Agregar la calificación definitiva
        definitiva = calcular_calificacion_definitiva(obj)
        if definitiva:
            calificaciones_list.append({
                "tipo": "definitiva",
                # "factibilidad": definitiva["promedio_factibilidad"],
                # "viabilidad": definitiva["promedio_viabilidad"],
                # "impacto": definitiva["promedio_impacto"],
                "puntuacion_general": definitiva["promedio_general"],
                "comentario": None  # No aplica comentario para la calificación definitiva
            })

        # Obtener el usuario que realiza la solicitud
        request = self.context.get('request')
        if request:
            user = request.user

            # Caso 1: Usuario es encargado
            if hasattr(user, 'area_encargada') and user.area_encargada:
                calificaciones_list.sort(key=lambda x: 0 if x['tipo'] == 'encargado' else 1)

            # Caso 2: Usuario es gerente
            elif getattr(user, 'es_gerente', False):
                calificaciones_list.sort(key=lambda x: 0 if x['tipo'] == 'gerente' else 1)

            # Caso 3: Otros usuarios (no modificar el orden)
        
        return calificaciones_list

    def get_fecha_creacion(self, obj):
        return obj.fecha_creacion.strftime('%d/%m/%Y')

    def get_estado_ejecucion(self, obj):
        return obj.get_estado_ejecucion_display()

    def get_estado_revision(self, obj):
        return obj.get_estado_revision_display()

    def get_tipo(self, obj):
        return obj.get_tipo_display()

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
        fields = ['estado_ejecucion']  # Permitir solo la actualización del estado

class UpdateCalificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calificacion
        fields = ['factibilidad', 'viabilidad', 'impacto', 'puntuacion_general', 'comentario']  # Campos editables