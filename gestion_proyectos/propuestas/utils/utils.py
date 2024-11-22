import os
from django.core.exceptions import ValidationError
import random


def validate_file_type(file):
    allowed_types = [
        'image/jpeg', 'image/png', 'image/gif',
        'application/pdf', 'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain', 'text/csv'
    ]
    max_file_size_mb = 10
    max_file_size_bytes = max_file_size_mb * 1024 * 1024

    if file.content_type not in allowed_types:
        raise ValidationError(f"El tipo de archivo '{file.content_type}' no está permitido.")

    if file.size > max_file_size_bytes:
        raise ValidationError(f"El archivo '{file.name}' supera el tamaño máximo de {max_file_size_mb} MB.")
    
    
    


def simple_unique_file_path(instance, filename):
    # Obtén el nombre base y la extensión del archivo
    name, extension = os.path.splitext(filename)
    # Genera un número aleatorio de 1 a 99999
    random_number = random.randint(1, 99999)
    # Concatena el nombre original con el número y la extensión
    unique_name = f"{name}_{random_number}{extension}"
    # Devuelve la ruta del archivo
    return os.path.join('uploads/', unique_name)