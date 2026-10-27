# Captura resistente a cortes y sincronización acotada

Estos son aprendizajes de una grabadora Android que recibe tramas pasivas de una radio instalada en un vehículo. Describen el diseño y fallos observados; no incluyen tokens, registros ni rutas recorridas.

## Guardar antes de interpretar

La captura conserva los bytes recibidos y metadatos de origen antes de decodificar señales. El servicio en primer plano continúa grabando aunque se cierre la pantalla. El GPS se registra por separado; ausencia de tramas CAN no se rellena con posiciones ni con una supuesta conexión activa. Un indicador de última señal solo avanza al recibir una carga CAN no vacía.

Cada registro se añade como un miembro GZIP independiente dentro de un archivo NDJSON comprimido. Así, los miembros ya escritos pueden recuperarse después de un corte brusco. Los archivos activos terminan en `.tmp`; al siguiente arranque se sellan los miembros recuperables y se marca la terminación como interrumpida. La finalización normal y la recuperación no dependen de que Android ejecute `onDestroy()` al quitar energía al vehículo.

El dispositivo estudiado también invocó callbacks antiguos de `LocationListener`, incluido `onStatusChanged`, pese a compilar la app contra un SDK moderno. La primera sesión en movimiento falló por un `AbstractMethodError`. Implementar explícitamente los callbacks de compatibilidad evitó ese fallo en la siguiente versión.

## Sincronización manual y finita

La captura actual no sube datos automáticamente al arrancar, recuperar red o cerrar el servicio. Una sincronización iniciada por el usuario sella el bloque actual mientras la recepción continúa en otro archivo. Se fija un punto de corte y la pertenencia de archivos y eventos a esa sincronización se guarda en SQLite. Los registros nuevos quedan para la siguiente ejecución.

Los envíos usan identificadores idempotentes y hash SHA-256. El servidor comprueba longitud y digest antes de almacenar; repetir una clave con los mismos bytes se acepta como duplicado, mientras que bytes distintos producen conflicto. La cola conserva fallos para reintento y elimina únicamente material reconocido. El indicador de último éxito solo avanza cuando todo el conjunto seleccionado fue confirmado.

Los eventos pequeños se agrupan para evitar una petición por evento. Las páginas de la cola avanzan más allá de filas intentadas, incluso cuando algunas fallan, para que el mismo error no impida enviar el resto. Los manifiestos de sesión se envían antes de sus eventos y fragmentos crudos.

## Presupuesto de almacenamiento

La grabadora mide contenido pendiente y espacio libre por separado. Avisa antes del límite, pausa al llegar al presupuesto o a la reserva de espacio y reanuda cuando hay margen. Pausar no borra capturas pendientes. Es un presupuesto protector basado en metadatos y reservas por escritura, no una cuota exacta del sistema de archivos; SQLite y cachés pueden ocupar espacio adicional.

## Lección de descompresión

Un archivo con miles de miembros GZIP concatenados llevó al dashboard en Cloudflare a superar su memoria cuando todos los bytes se entregaron a `fflate` en una llamada. Limitar solo los bytes *descomprimidos* no acotó las copias intermedias del inflador. La lectura del servidor pasó a `zlib` en flujo con backpressure y presupuesto de entrada y salida; el camino de navegador divide las entradas en bloques pequeños. Una prueba con 6.000 miembros confirmó la lectura completa bajo ese patrón. Los objetos originales no requirieron modificación.
