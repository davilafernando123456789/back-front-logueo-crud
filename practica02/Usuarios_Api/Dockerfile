
# Usa una imagen base de Python
FROM python:3.11.5

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos de tu proyecto al contenedor
COPY . /app

# Instala las dependencias de tu proyecto
RUN pip install -r requirements.txt

# Comando para ejecutar tu aplicación Flask
CMD ["python", "usuarios.py"]
