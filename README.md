# SIGCA – Sistema Integrado de Gestión de Citas y Agenda

## Descripción

SIGCA es una aplicación web desarrollada para el Centro
Integral Horizonte, cuyo propósito es centralizar y
automatizar la gestión de citas de diferentes
especialidades de atención.

El proyecto corresponde al curso Procesos de Ingeniería
de Software de la Universidad CENFOTEC.

## Integrantes

- Katherine González Arias
- Ronald Picado Hernández
- Jeffry Valverde Fallas

## Funcionalidades del MVP

- HU-01: Autenticación de usuarios.
- HU-02: Consulta de disponibilidad de profesionales.
- HU-03: Registro de citas.
- HU-04: Reprogramación y cancelación de citas.

## Tecnologías utilizadas

- Python 3.12
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- SQLite
- HTML5
- CSS3
- Bootstrap
- JavaScript
- Jinja2
- Pytest
- Git y GitHub
- GitHub Actions

## Arquitectura

El sistema utiliza una arquitectura modular que separa
la presentación, las rutas HTTP, las reglas de negocio
y la persistencia de datos.

## Estructura del proyecto

```text
SIGCA_Cenfotec/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── appointments/
│   ├── auth/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   ├── extensions.py
│   └── models.py
├── tests/
├── .env.example
├── .gitignore
├── config.py
├── create_admin.py
├── seed_data.py
├── requirements.txt
├── run.py
└── README.md
```

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Katherine506/SIGCA_Cenfotec.git
cd SIGCA_Cenfotec
```

### 2. Crear el entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar las dependencias

```powershell
python -m pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

```powershell
Copy-Item .env.example .env
```

Generar una clave secreta segura:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Agregar la clave generada al archivo .env:

```env
SECRET_KEY=REEMPLAZAR_CON_CLAVE_GENERADA
DATABASE_URL=sqlite:///sigca.db
```

El archivo .env no debe incluirse en el repositorio.

### 5. Crear el usuario administrador

```powershell
python create_admin.py
```

Ingresar el nombre, correo electrónico y contraseña
solicitados por el programa.

### 6. Cargar datos de demostración

```powershell
python seed_data.py
```

Este comando carga profesionales ficticios y sus
respectivos horarios de atención.

### 7. Ejecutar la aplicación

```powershell
python run.py
```

Acceder desde el navegador:

http://127.0.0.1:5000

## Pruebas automatizadas

Ejecutar todas las pruebas:

```powershell
python -m pytest -v
```

Ejecutar las pruebas con cobertura:

```powershell
python -m pytest -v --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml --junitxml=test-results.xml --cov-fail-under=80
```

## Resultados de calidad

Resultados de la ejecución local del 23 de noviembre
de 2026:

| Indicador                  | Resultado |
| -------------------------- | --------: |
| Pruebas ejecutadas         |        82 |
| Pruebas aprobadas          |        82 |
| Pruebas fallidas           |         0 |
| Tasa de aprobación         |     100 % |
| Cobertura de código        |   91,15 % |
| Umbral mínimo de cobertura |      80 % |

### Distribución de pruebas

| Componente               | Cantidad |
| ------------------------ | -------: |
| Configuración inicial    |        2 |
| HU-01: Autenticación     |        8 |
| HU-02: Disponibilidad    |       17 |
| HU-03: Registro de citas |       25 |
| HU-04: Gestión de citas  |       30 |
| Total                    |       82 |

## Integración continua

El proyecto utiliza GitHub Actions para automatizar:

- Configuración del entorno de ejecución.
- Instalación de dependencias.
- Ejecución de pruebas automatizadas.
- Verificación de pruebas de regresión.
- Validación de cobertura mínima del 80 %.
- Generación de reportes HTML y XML.
- Publicación de artefactos de pruebas.

## Metodología de desarrollo

El proyecto adopta Scrum como marco de trabajo,
complementado con prácticas de Extreme Programming (XP),
incluyendo pruebas automatizadas, integración continua
y desarrollo incremental.

## Estrategia de control de versiones

- main: rama principal.
- develop: rama de integración.
- feature/\*: ramas de desarrollo de funcionalidades.

Los cambios se gestionan mediante commits y Pull Requests.

## Limitaciones del MVP

- Base de datos SQLite orientada a un entorno académico.
- Duración fija de 30 minutos por cita.
- Uso de datos ficticios para demostración.
- Sin integración con expedientes médicos.
- Sin notificaciones automáticas.
- Sin integración con sistemas externos.
- Sin despliegue en un ambiente de producción.

## Deuda técnica

Se identificaron advertencias de deprecación relacionadas
con WTForms, las cuales deberán atenderse en futuras
versiones.

También se recomienda fortalecer las pruebas de seguridad,
ampliar la cobertura de escenarios excepcionales y
establecer protecciones para las ramas del repositorio.

## Contexto académico

Universidad CENFOTEC.

Curso: BISOFT-34 – Procesos de Ingeniería de Software.

Año: 2026.

Proyecto desarrollado con fines académicos.
