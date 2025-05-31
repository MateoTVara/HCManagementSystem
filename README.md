# HCManagementSystem

Sistema de gestión de citas web para un centro de salud, desarrollado con Django y PostgreSQL, que incluye un microservicio en Spring Boot para exportar listas usando ApachePOI.

## Requisitos previos

- Python 3.13.3
- Java JDK 21.0.2
- PostgreSQL (configurado según el archivo `HCManagementSystem/settings.py`)
- Git

## Clonar el repositorio

```bash
git clone https://github.com/MateoTVara/HCManagementSystem.git
cd HCManagementSystem
```

## Crear y activar entorno virtual

### 1. Crear y activar entorno virtual
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar la base de datos PostgreSQL
Edita el archivo `HCManagementSystem/settings.py` para ajustar los datos de conexión a tu base PostgreSQL (usuario, contraseña, host, puerto y nombre de base).

### 4. Ejecutar migraciones
```bash
python manage.py migrate
```

### 5. Correr servidor Django
```bash
python manage.py runserver
```



## Configuración y ejecución del microservicio Spring Boot

### 1. Ir a la carpeta del microservicio
```bash
cd java_service
```

### 2. Ejecutar el microservicio
```bash
.\gradlew bootRun

o

./gradlew bootRun
```