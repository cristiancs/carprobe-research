# Reconstrucción de viajes y calidad de mediciones

Una sesión de grabación es un contenedor técnico. Un viaje puede abarcar varias sesiones si se corta la alimentación o se cambia el archivo durante una sincronización. El análisis conserva las sesiones originales y reconstruye continuidad solo con evidencia suficiente.

## Reloj y distancia

Algunas capturas comenzaron con un reloj de 2018 y saltaron a la fecha real tras obtener GPS. Los registros originales conservan sus marcas; los intervalos que cruzan una corrección grande se excluyen de distancia, aceleración y puntuación. Sin un reloj monótono persistido, la duración a través del salto es aproximada.

La distancia integra velocidades observadas en intervalos de hasta tres segundos. No interpola recepción ausente. Velocidad CAN validada tiene prioridad; GPS reciente y con precisión suficiente sirve como alternativa cuando CAN falta. La lectura instantánea caduca para evitar mostrar un valor viejo como si fuese actual.

## Unión de sesiones

La unión automática exige el mismo dispositivo, la misma asignación de conductor, una separación temporal corta, posiciones GPS fiables cerca de ambos límites y proximidad espacial. Saltos del reloj, superposición, falta de evidencia, cambio de conductor o una separación manual impiden unir. Ordena por tiempo de captura, no por llegada al servidor. Los gráficos separan los límites de grabación y no inventan ruta durante el hueco.

## Indicadores derivados

Una puntuación experimental de suavidad usa velocidad sin reducir resolución para el gráfico. Descarta intervalos mayores de tres segundos y aceleraciones físicamente inverosímiles. Cuenta un episodio continuo de frenado o aceleración una sola vez. Requiere cobertura, tiempo y distancia mínimos; cuando faltan, muestra resultado indisponible en vez de asignar 100. Umbrales y pesos son heurísticos que requieren calibración, no una calificación certificada de seguridad.

El explorador de mensajes agrupa por comando, longitud y subtipo. Solo entran tramas con checksum válido. Cuenta cambios dentro de una misma sesión y no deduce continuidad de estado durante silencios. Un payload desconocido permanece desconocido hasta contrastarlo con código de referencia o una acción marcada.

## Datos que no se publican aquí

El repositorio contiene conteos y estadísticas agregadas, sin coordenadas, rutas GPS, IDs de dispositivo o sesiones crudas. Los scripts de reproducción leen archivos privados; `research-can.py` genera detalles por sesión y su salida no debe publicarse sin una revisión adicional.
