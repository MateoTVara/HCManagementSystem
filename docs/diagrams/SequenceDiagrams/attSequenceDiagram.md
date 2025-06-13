```mermaid
sequenceDiagram
    actor Personal as Personal de Atención
    participant Frontend
    participant Backend as Django Views
    participant DB as PostgreSQL
    participant Auth as Django Auth

    Personal->>Frontend: 1. Ingresa credenciales
    activate Frontend
    Frontend->>Backend: POST /login (username, password)
    deactivate Frontend

    activate Backend
    Backend->>Auth: authenticate()
    activate Auth
    Auth->>DB: SELECT "core_user" WHERE username=X
    DB-->>Auth: Usuario
    Auth-->>Backend: User object (role=ATTENDANT)
    deactivate Auth

    alt Autenticación exitosa
        Backend-->>Frontend: Redirige a dashboard
    else Error
        Backend-->>Frontend: Mensaje de error
    end
    deactivate Backend

    Personal->>Frontend: 2. Registra nuevo paciente
    activate Frontend
    Frontend->>Backend: POST /pacientes/ {datos del paciente}
    deactivate Frontend

    activate Backend
    Backend->>DB: INSERT "Patient" (dni, first_name, ...)
    DB-->>Backend: Paciente creado (ID)
    Backend-->>Frontend: Confirmación + ID paciente
    deactivate Backend

    opt Actualización de paciente
        Personal->>Frontend: 2.1 Actualiza datos paciente
        Frontend->>Backend: PUT /pacientes/<id>/ {datos actualizados}
        Backend->>DB: UPDATE "Patient" WHERE id=<id>
        DB-->>Backend: OK
        Backend-->>Frontend: Confirmación
    end

    Personal->>Frontend: 3. Búsqueda paciente (nombre, apellido, DNI)
    activate Frontend
    Frontend->>Backend: GET /pacientes/?search=query
    deactivate Frontend

    activate Backend
    Backend->>DB: SELECT "Patient" WHERE (first_name, last_name, dni) ILIKE query
    DB-->>Backend: Lista pacientes
    Backend-->>Frontend: JSON pacientes
    deactivate Backend

    Personal->>Frontend: 4. Agenda nueva cita
    activate Frontend
    Frontend->>Backend: GET /doctores/disponibles?fecha=...&hora=...
    deactivate Frontend

    activate Backend
    Backend->>DB: SELECT "Doctor" EXCEPT citas en esa fecha/hora
    DB-->>Backend: Lista doctores disponibles
    Backend-->>Frontend: JSON doctores
    deactivate Backend

    Personal->>Frontend: Selecciona doctor, ingresa motivo
    activate Frontend
    Frontend->>Backend: POST /citas/ {paciente_id, doctor_id, fecha, hora, motivo}
    deactivate Frontend

    activate Backend
    Backend->>DB: Verificar conflicto (UniqueConstraint doctor+fecha+hora)
    alt Horario disponible
        Backend->>DB: INSERT "Appointment"
        DB-->>Backend: Cita creada
        Backend-->>Frontend: Confirmación
    else Conflicto
        Backend-->>Frontend: Error "Horario ocupado"
    end
    deactivate Backend

    Personal->>Frontend: 5. Reagendar cita
    activate Frontend
    Frontend->>Backend: PUT /citas/<id>/reagendar {nueva_fecha, nueva_hora}
    deactivate Frontend

    activate Backend
    Backend->>DB: Verificar nueva fecha/hora (disponibilidad doctor)
    alt Disponible
        Backend->>DB: UPDATE "Appointment" (fecha, hora)
        DB-->>Backend: OK
        Backend-->>Frontend: Confirmación
    else Ocupado
        Backend-->>Frontend: Error
    end
    deactivate Backend

    Personal->>Frontend: 6. Cancelar cita
    activate Frontend
    Frontend->>Backend: PATCH /citas/<id>/cancelar {status: 'X'}
    deactivate Frontend

    activate Backend
    Backend->>DB: UPDATE "Appointment" SET status='X'
    DB-->>Backend: OK
    Backend-->>Frontend: Confirmación
    deactivate Backend

    Personal->>Frontend: 7. Cambia estado a "en consulta"
    activate Frontend
    Frontend->>Backend: PATCH /citas/<id>/estado {status: 'C'} 
    deactivate Frontend

    activate Backend
    Backend->>DB: UPDATE "Appointment" SET status='C'
    DB-->>Backend: OK
    Backend-->>Frontend: Confirmación
    deactivate Backend

    Personal->>Frontend: 8. Gestiona contacto emergencia
    activate Frontend
    Frontend->>Backend: POST /contactos-emergencia/ {paciente_id, ...}
    deactivate Frontend

    activate Backend
    Backend->>DB: INSERT "EmergencyContact"
    DB-->>Backend: Contacto creado
    Backend-->>Frontend: Confirmación
    deactivate Backend