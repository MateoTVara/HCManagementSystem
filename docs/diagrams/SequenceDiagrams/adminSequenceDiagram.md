```mermaid
sequenceDiagram
    actor Admin as Administrador
    participant Frontend
    participant Backend as Django Views
    participant DB as PostgreSQL
    participant Auth as Django Auth

    Admin->>Frontend: 1. Ingresa credenciales
    activate Frontend
    Frontend->>Backend: POST /login (username, password)
    deactivate Frontend

    activate Backend
    Backend->>Auth: authenticate()
    activate Auth
    Auth->>DB: SELECT "core_user" WHERE username=X AND role='ADMIN'
    DB-->>Auth: Usuario admin
    Auth-->>Backend: User object (role=ADMIN)
    deactivate Auth
    Backend-->>Frontend: Dashboard admin
    deactivate Backend

    %% Gestión de citas
    Admin->>Frontend: 2. Ver todas las citas
    activate Frontend
    Frontend->>Backend: GET /admin/citas/
    deactivate Frontend

    activate Backend
    Backend->>DB: SELECT "Appointment" JOIN "Doctor" JOIN "Patient"
    DB-->>Backend: Todas las citas con detalles
    Backend-->>Frontend: JSON/HTML citas
    deactivate Backend

    Admin->>Frontend: 3. Registrar nueva cita
    activate Frontend
    Frontend->>Backend: POST /admin/citas/nueva {paciente_id, doctor_id, fecha, hora, motivo}
    deactivate Frontend

    activate Backend
    Backend->>DB: INSERT "Appointment"
    DB-->>Backend: Cita creada
    Backend-->>Frontend: Confirmación
    deactivate Backend

    Admin->>Frontend: 4. Editar cita existente
    activate Frontend
    Frontend->>Backend: PUT /admin/citas/<id>/ {nuevos_datos}
    deactivate Frontend

    activate Backend
    Backend->>DB: UPDATE "Appointment" WHERE id=<id>
    DB-->>Backend: OK
    Backend-->>Frontend: Confirmación
    deactivate Backend

    Admin->>Frontend: 5. Generar reporte de citas
    activate Frontend
    Frontend->>Backend: POST /admin/reportes/citas/ {fecha_inicio, fecha_fin, formato}
    deactivate Frontend

    activate Backend
    Backend->>DB: SELECT "Appointment" WHERE date BETWEEN...
    DB-->>Backend: Datos citas
    Backend->>Backend: Generar PDF/Excel
    Backend-->>Frontend: Archivo reporte
    deactivate Backend

    Admin->>Frontend: 6. Ver calendario de citas
    activate Frontend
    Frontend->>Backend: GET /admin/calendario/?mes=X&año=Y
    deactivate Frontend

    activate Backend
    Backend->>DB: SELECT "Appointment" EXTRACT(day) GROUP BY date
    DB-->>Backend: Conteo citas por día
    Backend-->>Frontend: JSON {fecha: count}
    deactivate Backend

    %% Gestión de pacientes
    Admin->>Frontend: 7. Agregar nuevo paciente
    activate Frontend
    Frontend->>Backend: POST /admin/pacientes/nuevo/ {datos_paciente}
    deactivate Frontend

    activate Backend
    Backend->>DB: INSERT "Patient"
    DB-->>Backend: Paciente creado
    Backend-->>Frontend: Confirmación
    deactivate Backend

    Admin->>Frontend: 8. Listar todos los pacientes
    activate Frontend
    Frontend->>Backend: GET /admin/pacientes/
    deactivate Frontend

    activate Backend
    Backend->>DB: SELECT "Patient"
    DB-->>Backend: Todos los pacientes
    Backend-->>Frontend: JSON/HTML pacientes
    deactivate Backend

    Admin->>Frontend: 9. Editar paciente existente
    activate Frontend
    Frontend->>Backend: PUT /admin/pacientes/<id>/ {nuevos_datos}
    deactivate Frontend

    activate Backend
    Backend->>DB: UPDATE "Patient" WHERE id=<id>
    DB-->>Backend: OK
    Backend-->>Frontend: Confirmación
    deactivate Backend

    %% Gestión de médicos
    Admin->>Frontend: 10. Registrar nuevo médico
    activate Frontend
    Frontend->>Backend: POST /admin/medicos/nuevo/ {user_data, doctor_data}
    deactivate Frontend

    activate Backend
    Backend->>DB: START TRANSACTION
    Backend->>DB: INSERT "User" (username, password, role='DOCTOR')
    DB-->>Backend: User creado (ID)
    Backend->>DB: INSERT "Doctor" (user_id=ID, specialty, dni)
    DB-->>Backend: Doctor creado
    Backend->>DB: COMMIT
    Backend-->>Frontend: Confirmación
    deactivate Backend

    Admin->>Frontend: 11. Editar médico existente
    activate Frontend
    Frontend->>Backend: PUT /admin/medicos/<id>/ {user_data, doctor_data}
    deactivate Frontend

    activate Backend
    Backend->>DB: START TRANSACTION
    Backend->>DB: UPDATE "User" JOIN "Doctor" WHERE doctor.id=<id>
    DB-->>Backend: OK
    Backend->>DB: COMMIT
    Backend-->>Frontend: Confirmación
    deactivate Backend