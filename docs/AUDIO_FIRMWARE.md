# Salto de volumen y límites de una comparación de firmware

En la unidad estudiada se observó un salto audible entre los niveles 19 y 20, tanto en Bluetooth como en otra fuente y con controles de la radio o del volante. La observación no identificó todavía la capa responsable: perfil de ganancia, DSP, aplicación de sonido, MCU o firmware.

Un archivo `raw/events` con extensión `.bin` resultó ser texto de captura comprimido con GZIP, no una copia de firmware. La extensión por sí sola no permite clasificar un objeto almacenado. Los diagnósticos identificaron la familia 9212A, AC8227L, runtime API 27 y `SoundEffects` 1.1.17. El nombre del paquete de sonido no prueba qué chip físico está instalado.

La [comparación local](FIRMWARE_AB_COMPARISON.md) de paquetes públicos 9212A y 9212B 8.0.1 encontró el mismo APK `SoundEffects` y parte de la pila de audio, pero diferencias en bibliotecas de audio, identidad y valores de pantalla en etapas tempranas del arranque. Compartir configuración de núcleo y soporte compilado para 1024×600 no demuestra que los paquetes sean intercambiables: LK y ARM2 conservan diferencias coherentes con valores predeterminados de pantalla distintos.

No se verificó una versión 9212A más nueva compatible con la unidad ni un changelog que demuestre una corrección del salto 19→20. Los reportes sobre 9212B o un video con síntoma parecido son pistas, no pruebas de una reparación para 9212A. Flashear un OTA amplio para probar un problema de audio podría afectar arranque y pantalla; la evidencia disponible no establece una ruta de actualización segura.

El siguiente contraste útil sería recuperar la configuración efectiva de pantalla/metazone y el APK de sonido instalado, además de probar de forma controlada opciones de Loudness y ganancia. Esas comprobaciones no forman parte de los archivos públicos de este repositorio.
