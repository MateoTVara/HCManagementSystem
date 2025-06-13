```mermaid
sequenceDiagram
    actor Doctor
    participant Frontend as Interfaz Web (Django Templates/JS)
    participant Backend as Django Views
    participant DB as PostgreSQL
    participant Auth as Django Authentication

    Doctor->>Frontend: 1. Ingresa username y contraseña
    activate Frontend
    Frontend->>Backend: POST /login
    deactivate Frontend

    activate Backend
    Backend->>Auth: authenticate()
    activate Auth
    Auth->>DB: SELECT "auth_user"
    DB-->>Auth: Datos usuario
    Auth-->>Backend: User object
    deactivate Auth

    alt Credenciales válidas
        Backend-->>Frontend: Redirect dashboard
    else Error
        Backend-->>Frontend: Mensaje error
    end
    deactivate Backend

    Doctor->>Frontend: 2. Solicita citas del día
    activate Frontend
    Frontend->>Backend: GET /api/citas/hoy
    deactivate Frontend

    activate Backend
    Backend->>DB: SELECT "citas_cita" WHERE fecha=hoy AND doctor=user
    DB-->>Backend: Lista citas
    Backend-->>Frontend: JSON citas
    deactivate Backend

    Doctor->>Frontend: 3. Selecciona cita para detalles
    activate Frontend
    Frontend->>Backend: GET /api/citas/<id>/detalle
    deactivate Frontend

    activate Backend
    Backend->>DB: SELECT JOIN (citas_cita, pacientes_paciente, historiales_historial)
    DB-->>Backend: Datos completos cita
    Backend-->>Frontend: JSON detallado
    deactivate Backend

    loop Pre-consulta
        Doctor->>Frontend: 4.1 Solicita historial médico
        Frontend->>Backend: GET /api/historial/<paciente_id>
        Backend->>DB: SELECT "historiales_historial"
        DB-->>Backend: Historial completo
        Backend-->>Frontend: JSON historial

        Doctor->>Frontend: 4.2 Solicita alergias
        Frontend->>Backend: GET /api/alergias/<paciente_id>
        Backend->>DB: SELECT "pacientes_alergia"
        DB-->>Backend: Lista alergias
        Backend-->>Frontend: JSON alergias
    end

    Doctor->>Frontend: 5. Ingresa diagnóstico/tratamiento
    activate Frontend
    Frontend->>Backend: POST /consultas/nueva {diagnóstico, tratamiento}
    deactivate Frontend

    activate Backend
    Backend->>DB: INSERT "consultas_consulta"
    DB-->>Backend: OK
    Backend-->>Frontend: Confirmación
    deactivate Backend

    Doctor->>Frontend: 6. Prescribe medicamentos
    activate Frontend
    Frontend->>Backend: POST /recetas/nueva {medicamentos}
    deactivate Frontend

    activate Backend
    Backend->>DB: INSERT "recetas_receta"
    DB-->>Backend: OK
    Backend-->>Frontend: Confirmación
    deactivate Backend

    opt Admisión hospitalaria
        Doctor->>Frontend: 7. Solicita registro admisión
        Frontend->>Backend: POST /admisiones/nueva
        Backend->>DB: INSERT "admisiones_admision"
        DB-->>Backend: OK
        Backend-->>Frontend: Confirmación
    end

    opt Urgencia
        Doctor->>Frontend: 8. Solicita contacto emergencia
        Frontend->>Backend: GET /pacientes/<id>/contacto-emergencia
        Backend->>DB: SELECT "pacientes_contactoemergencia"
        DB-->>Backend: Datos contacto
        Backend-->>Frontend: JSON contacto
    end

    opt Revisiones
        Doctor->>Frontend: 9. Solicita prescripciones activas
        Frontend->>Backend: GET /pacientes/<id>/prescripciones-activas
        Backend->>DB: SELECT "recetas_receta" WHERE activa=True
        DB-->>Backend: Lista prescripciones
        Backend-->>Frontend: JSON prescripciones
    end