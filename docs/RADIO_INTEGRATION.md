# Integración con la radio: zona horaria, hotspot y BLE

## Zona horaria

En una radio que reinicia o corrige tarde la zona horaria, guardar una región IANA como `America/Santiago` permite aplicar sus reglas estacionales. Guardar solo un desplazamiento UTC pierde los cambios de horario de verano. La app comprueba la propiedad de zona y el ajuste de detección automática, aplica el cambio localmente cuando dispone de root y verifica el resultado. No cambia la hora ni el ajuste de hora automática.

Los eventos de arranque, reactivación y cambio de ajustes desencadenan comprobaciones adicionales. Las operaciones de shell son acotadas y salen del hilo de UI. La ausencia de root se comunica para que el ajuste pueda hacerse en Android; no se presenta una aplicación fallida como éxito.

## Hotspot y Bluetooth

La integración observó el broadcast de estado del hotspot de Android API 27 y, cuando estaba disponible, consultó su estado inicial. Tras activarlo, esperaba por defecto 60 segundos antes de solicitar apagar Bluetooth para dar tiempo al inicio de CarPlay. Si el hotspot se apaga o se deshabilita la regla, la solicitud pendiente se cancela. Una nueva sesión de hotspot reinicia la espera.

Después de la espera inicial, una reactivación confirmada de Bluetooth provoca otra solicitud. Ecos rápidos sin un apagado confirmado se agrupan para evitar un bucle de llamadas. La regla no desempareja dispositivos ni vuelve a encender Bluetooth. En Android moderno, la API puede denegar el apagado programático; las pruebas unitarias de estado no prueban cómo responde una radio concreta ni si una sesión CarPlay ya establecida se mantiene.

## Experimento BLE descartado

Se diseñó un puente HUD → iPhone para transferir registros cuando la radio no tuviera Internet. El protocolo separaba control y datos, enviaba fragmentos numerados y verificaba SHA-256 antes del upload. Era un experimento con credenciales de carga temporales, no una vía para entregar el token permanente del vehículo al teléfono.

El puente se retiró del flujo Android diario después de pruebas insatisfactorias. La recepción pasiva y la sincronización manual por red siguieron siendo el camino utilizado. Se documenta para no confundir un protocolo diseñado con una capacidad validada en campo.
