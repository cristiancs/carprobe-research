# Comparación local de firmware XY AUTO 9212A / 9212B

Fecha: 2026-09-20. Análisis estático. No se instaló firmware, no se ejecutaron sus binarios y no se modificó la radio.

## Alcance y archivos

Se seleccionaron dos paquetes internacionales OTA de **la misma versión 8.0.1**, para reducir la confusión entre cambios de versión y diferencias de variante. No se obtuvo un paquete 7.3.9 para 9212A. La comparación de estos dos archivos no describe necesariamente todas las radios A y B.

- A: `gongban_9212A_1024x768_hw-ota-v8.0.1.zip`, 977.024.571 bytes. Fuente: http://carsoftdown.xygala.com/public/upload/softs/2024/01-04/gongban_9212A_1024x768_hw-ota-v8.0.1.zip
- B: `gongban_9212B_hw^ok-ota-v8.0.1.zip`, 969.254.262 bytes. Fuente: http://carsoftdown.xygala.com/public/upload/softs/2023/12-02/gongban_9212B_hw%5Eok-ota-v8.0.1.zip
- Catálogo público de referencia: https://xdaforums.com/t/xy-auto-firmware-9212b-ver-7-3-9.4605241/page-8

Los archivos del fabricante y resultados intermedios no se incorporan al repositorio.

## Datos de la radio instalada

El diagnóstico original identifica `B9212A_00017_V001`, plataforma `ac8227l`, ARMv7, API 27, núcleo 3.18.79 y SoundEffects `com.xy.tda7729` 1.1.17. El usuario informa pantalla 1024×600. El firmware B7.3.8 y MCU 4.2 provienen de las notas previas. No se dispone de una copia completa del firmware instalado ni de la configuración exportada de pantalla.

## Arranque y configuración de hardware

| Dato examinado | Paquete A 8.0.1 | Paquete B 8.0.1 |
| --- | --- | --- |
| Dispositivo declarado en OTA | `8227L_demo` | `8227L_demo` |
| `armkeyword.bin` | `6D2710`, `8.0.1` | `702710`, `8.0.1` |
| Núcleo | 4.14.116, compilado 2023-12-07 | 4.14.116, compilado 2023-11-30 |
| Arquitectura descrita por DTB | AC8227L, Cortex-A7 | AC8227L, Cortex-A7 |
| Tamaño de página de boot | 2048 | 2048 |
| Dirección del núcleo / ramdisk | `0x80008000` / `0x84000000` | Iguales |
| Configuración del núcleo extraída | Idéntica a B | Idéntica a A |
| Configuración LCM compilada | 1024×600, rotación 0 | 1024×600, rotación 0 |
| Controlador LCM configurado | `cpt_clap070wp03xg_lvds` | Igual |
| Controlador táctil configurado | `CONFIG_TOUCHSCREEN_MTK_GT928=y` | Igual |

El DTB incluido en cada núcleo tiene las mismas propiedades en el análisis realizado. Los archivos regulares del ramdisk coinciden salvo los binarios `init` y `sbin/charger`. Los núcleos compilados no son idénticos: compartir configuración no demuestra equivalencia de código.

**Corrección de la interpretación anterior:** el nombre 1024×768 del archivo A no basta para descartar soporte de 1024×600. La configuración compilada contiene precisamente 1024×600. Tampoco prueba que esa sea la configuración efectiva al arrancar: pueden intervenir el cargador, metazone y parámetros del panel. No se ha establecido que el controlador o los tiempos de pantalla coincidan con la radio del usuario.

Los códigos distintos de `armkeyword.bin` son evidencia de identificación diferenciada del paquete; su significado eléctrico exacto y el mecanismo completo de selección todavía no están determinados.

## Comparación completa de los archivos seleccionados

Se completaron las dos descargas y la extracción de las 20 entradas de cada ZIP, con verificación CRC de todas las entradas. Los hashes SHA-256 de los archivos completos son:

- A: `0e7e8c965a7c2a394ce6b1a33a6c3b90ddb860fbd129b0df4f6736b028ccfff7`
- B: `7e6cc5cc49b0d89df73288d24c39e68e3ffe459902691313d5ab881dbdbda6a7`

CRC y SHA-256 documentan integridad e identidad de lo descargado, no autentican al fabricante. Se reconstruyeron las imágenes ext4 del sistema y vendor a partir de los datos Brotli y sus listas de transferencia, sin montarlas ni arrancarlas. La extracción con debugfs incluyó configuración, bibliotecas, framework, aplicaciones de sonido/ajustes/actualización y archivos MCU. En este **subconjunto**, 1.385 archivos coinciden byte por byte, 103 difieren y 7 aparecen solo en un paquete. No es un porcentaje calculado sobre todos los archivos del firmware.

### Identificación y pantalla: diferencias reales

- `build.prop` identifica A como `F9212A_00017_V001` y B como `F9212B_00020_V001`. Ambos son ARMv7/API 27 y declaran `ro.product.xy.cpuinfo=8239`.
- A configura `ro.product.xy.display=6` y `ro.product.xy.hwrotation=6`; B configura ambos en `0`. No se interpreta el valor 6 como un ángulo literal.
- `arm2.bin` tiene el mismo tamaño y difiere en solo 4 bytes. La instrucción ARM en offset `0x398b0` carga **768** en A y **600** en B; la instrucción anterior carga 1024 en ambos. Otras dos instrucciones intercambian valores 1/2.
- `lk.img` tiene el mismo tamaño y difiere en solo 3 bytes. La instrucción Thumb en offset `0x2b4a2` carga **768** en A y **600** en B; también aparece 1024 en ambos y un intercambio de valores 1/2.
- Estos valores son evidencia fuerte de diferentes valores predeterminados de pantalla en el arranque. Las funciones no tienen nombres recuperados que permitan atribuir todos los campos con certeza. No basta que el núcleo comparta `CONFIG_LCM_HEIGHT=600`: el paquete A sí contiene valores 768 en otras capas.
- La aplicación de ajustes común obtiene información de pantalla desde metazone, además de propiedades y orientación. Esto respalda la necesidad de leer la configuración real de la unidad. No se ha probado que conservar metazone sea suficiente para instalar cualquiera de estos paquetes.

### Particiones y actualización

- `scatter.txt`, `tee.img`, el ejecutable `update-binary` y el certificado OTA incluido son idénticos.
- El script OTA difiere únicamente en el identificador de compilación que imprime. Su condición visible comprueba `8227L_demo`, sin identificar A/B ni verificar panel. Otros componentes del proceso podrían hacer verificaciones adicionales; no se afirma que la radio acepte cualquiera de los ZIP.
- Ambos scripts escriben ARM2, LOGO, RECOVERY, LK, ANDROID, VENDOR, BOOTIMG y TEE. Por tanto, no son actualizaciones limitadas a una aplicación.
- Los diagnósticos instalados muestran rutas de sistema/vendor coherentes con esos nombres de partición, pero no incluyen tamaños y desplazamientos suficientes para comparar el mapa real de la unidad.

### Audio y MCU

- `SoundEffects.apk` es **idéntico byte por byte** entre A y B. El manifiesto informa `com.xy.tda7729` **1.1.17**, igual número de versión que en el diagnóstico instalado. No se dispone del APK instalado para comparar sus bytes.
- También coinciden `audio.primary.ac8227l.so`, `libaudiosetting.so`, `libXYPQjni.so`, `libmetazone.so`, las tablas `audio_policy_volumes.xml` y `default_volume_tables.xml` examinadas, y los binarios MCU extraídos.
- **No todo el audio es idéntico:** cambian secciones de código de `libaudiopolicycustomextensions.so`, `libaudiopolicymanagerdefault.so` y `libbundlewrapper.so`. El análisis no identifica esos cambios como una corrección del salto 19→20.
- El APK compartido contiene selección de comportamiento por identificadores, incluidos `00017` y `00020`; su nombre `tda7729` no prueba qué chip físico usa cada radio.
- Ambos paquetes declaran MCU `iap_pv1_9218033_0040`; el historial incluido llega a 4.0. No se ha probado que flashear el paquete reemplace automáticamente la MCU, ni que esos archivos sean apropiados para la MCU 4.2 anotada de la unidad.

### Otras diferencias

A activa propiedades de DRM/Widevine y añade siete archivos relacionados que no aparecen en B dentro del subconjunto comparado. También cambian algunos componentes de framework, módulos del núcleo y bibliotecas de cámara. Las fechas de compilación difieren una semana; esas diferencias no se pueden atribuir automáticamente a la letra A/B.

## Resultado práctico

El análisis confirma que estos paquetes A y B comparten gran parte del software y numerosos componentes de bajo nivel. También encuentra diferencias reales de identificación y configuración de pantalla. **No demuestra intercambiabilidad ni una solución para el salto de volumen.**

El 9212A 8.0.1 sigue siendo un candidato para investigación, pero requiere comparar la configuración original de pantalla/metazone, el mapa de particiones y el firmware instalado. El núcleo instalado 3.18.79 difiere del 4.14.116 de ambos paquetes. No se recomienda flashear ninguno con la evidencia actual.

La comprobación local útil fue extraer, descomprimir, comparar hashes, leer propiedades, recuperar configuración del núcleo y desensamblar regiones concretas de ARM/Thumb. **No se ejecutó un emulador ni se simuló el hardware.** JADX produjo código de análisis de las aplicaciones con algunos errores de descompilación; las comparaciones binarias y propiedades no dependen de esa descompilación.

Evidencia resumida reproducible: [FIRMWARE_AB_EVIDENCE.json](FIRMWARE_AB_EVIDENCE.json). Los archivos fuente del fabricante y resultados intermedios permanecen fuera del repositorio.
