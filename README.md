# App Web: "Life Organizer"

## Descripción general

"Life Organizer" es una app web multifuncional que combina un gestor de tareas con un diario personal. Los usuarios pueden organizar sus actividades diarias y también registrar sus experiencias, como viajes, eventos importantes y otras notas, todo sin necesidad de gestionar archivos o fotos. Todo se maneja de manera sencilla y eficaz a través de texto.

### Caso de Uso 1: Gestor de Tareas

**Objetivo:** Ayudar a los usuarios a organizar sus actividades diarias con la capacidad de añadir, editar, eliminar y marcar tareas como completadas.

**Flujo de trabajo:**

1. Página principal: El usuario ve un panel dividido en dos secciones: Tareas y Diario Personal.

2. Agregar tarea: El usuario puede agregar nuevas tareas desde la página principal con un título, descripción, fecha de vencimiento y categoría (trabajo, personal, urgente).

3. Editar y eliminar: Las tareas pueden ser editadas o eliminadas si es necesario.

4. Marcar como completada: El usuario puede marcar las tareas completadas, y estas se mueven a una lista separada o se muestran con un estilo diferente (como tachadas).

5. Filtrar tareas: El sistema permite filtrar las tareas por fecha, categoría o estado (pendiente/completada).

**Características:**

- Lista de tareas organizadas.

- Filtros de tareas por categoría y fecha.

- Formularios simples para agregar o editar tareas.

- Autenticación con Flask-Login para gestionar tareas personales.

### Caso de Uso 2: Diario Personal (Eventos, Notas, Experiencias)

**Objetivo:** Permitir a los usuarios registrar eventos importantes, experiencias de vida (como viajes o celebraciones) y notas personales, todo de manera textual.

**Flujo de trabajo:**

1. Página principal: El panel de inicio muestra dos secciones: una para Tareas y otra para el Diario Personal.

2. Agregar entrada de diario: El usuario puede añadir nuevas entradas de diario con un título, fecha, ubicación (opcional) y una descripción del evento o experiencia. Ejemplo: "Viaje a Barcelona", "Cumpleaños 2025", "Reunión de trabajo importante".

3. Ver detalles: El usuario puede ver un resumen de cada entrada de diario, con la opción de editarla o eliminarla si lo desea.

4. Buscar entradas: El sistema permite buscar entradas de diario por fecha, palabras clave o ubicación (si se incluye).

5. Relación con tareas: Las entradas de diario pueden estar relacionadas con tareas. Por ejemplo, si el usuario está planeando un viaje, puede crear tareas relacionadas (como "Reservar hotel", "Comprar boletos") que aparecerán junto a su entrada de diario.

**Características:**

- Crear entradas de diario con título, fecha, descripción y ubicación (opcional).

- Relación de tareas con las entradas del diario para hacer un seguimiento.

- Vista de resumen de entradas con la opción de editar o eliminar.

- Búsqueda de entradas por fecha o palabras clave.

- Autenticación con Flask-Login para un seguimiento personalizado.

### Interacciones entre ambos casos de uso

Sincronización entre Tareas y Diario: Las tareas se pueden vincular a entradas de diario. Por ejemplo, si el usuario está planeando un viaje (entrada de diario), puede agregar tareas relacionadas (reservar vuelos, empacar, etc.) y vincularlas a la entrada correspondiente.

Vista integrada: En la vista de Diario Personal, las tareas relacionadas con el evento o experiencia pueden aparecer como recordatorios de lo que el usuario debe hacer en relación con esa entrada.

### Tecnologías

- Backend: Flask

- Base de datos: PostgreSQL

- Autenticación: Flask-Login

- Frontend: HTML, CSS y JavaScript
