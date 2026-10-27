# Plataforma XY AUTO y recepción pasiva

## Identidad observada

La unidad estudiada pertenece a la familia XY AUTO 9212A con SoC AC8227L, ABI ARMv7 y runtime Android API 27. El número comercial de Android mostrado por algunas interfaces no sustituyó la comprobación de `ro.build.version.sdk` y del ABI. CAN Pro informó versión 1.020 y usó un plugin Raise/Changan. Estas observaciones describen una unidad y no todas las radios 9212A.

El firmware 9212A 8.0.1 usado para análisis fue descargado de la [fuente pública del fabricante](http://carsoftdown.xygala.com/public/upload/softs/2024/01-04/gongban_9212A_1024x768_hw-ota-v8.0.1.zip). No se instaló. Su plugin y el software de la radio estudiada comparten nombres y formatos, pero la identidad binaria no se verificó. La [comparación de firmware](FIRMWARE_AB_COMPARISON.md) documenta procedencia y hashes.

## Recuperación estática del software de referencia

1. Se reconstruyeron las imágenes `system` y `vendor` desde los archivos de transferencia del OTA para inspección sin arrancarlas.
2. `debugfs` permitió extraer APK, VDEX y archivos de configuración de las imágenes ext4.
3. El DEX de `PvCanset` requirió extracción desde VDEX; el APK por sí solo no contenía las clases esperadas.
4. JADX permitió seguir las llamadas entre CAN Pro, el plugin y el servicio de recepción. Las conclusiones de transporte se contrastaron después con capturas de campo.

No se redistribuyen binarios ni código descompilado del fabricante.

## Por qué el primer descubrimiento falló

El host CAN activo se llama `com.kyhero.car.myhost`; una búsqueda que solo filtraba nombres con `xy`, `can` o `mcu` lo omitía. El APK `CanBus1.apk` exporta `com.kyhero.car.myhost.Canset.AidlToOutDataService`. El host carga un plugin específico desde una ruta con forma `/sdcard/CanBus/plugin/<canId>/<brandId>/`. `PvCanset` funciona principalmente como interfaz de configuración y no fue la fuente pasiva de datos en tiempo real.

En el firmware de referencia, el servicio Binder ofrece registro y baja de listeners mediante las transacciones 1 y 2. La interfaz recuperada estáticamente no coincidió con el descriptor de ejecución observado en la unidad. Consultar `IBinder.getInterfaceDescriptor()` permitió registrarse; aun así, durante la prueba no llegaron callbacks escalares ni genéricos. Un registro correcto de un listener, por sí solo, no demuestra que ese camino transporte los datos buscados.

El contrato de referencia recibe siete listeners en orden: genérico, climatización, puertas, teclas, radar, trayectoria y ajustes. Los callbacks escalares identificados en el análisis estático fueron:

| Listener | Transacciones y valores de referencia |
| --- | --- |
| Climatización | 1 encendido, 2/3 temperaturas, 4 velocidad del ventilador, 5 modo, 6 recirculación, 7 A/C, 8/9 desempañado, 10 PTC. Booleanos como `int32`; temperaturas como `float`. |
| Puertas | 1–4 puertas, 5 maletero, 6 capó; booleanos como `int32`. |
| Teclas | 1 con dos `int32`; la semántica requiere acciones marcadas. |
| Radar | 1–4 sensores delanteros, 5–8 traseros, 9/10 máximos; `int32`. |
| Trayectoria | Valores de giro cuya unidad física no quedó calibrada. |

Esta tabla describe el **APK de referencia**. Como los descriptores y los callbacks difirieron en la radio instalada, no se presenta como un contrato Binder universal.

## Canal recibido en la unidad

La inspección de `CanbusSerial.sendCmd()` identificó el broadcast `xy.auto.canbus.rxpduses` con la trama en el extra `rxpduses` de tipo `byte[]`. El camino `0xff` utiliza `xy.auto.canbus.rxpdusesff`. Una captura estacionaria posterior recibió tramas `0x29`, `0x7D` y `0x3A` correlacionadas con acciones observadas. Esa evidencia confirmó el canal de recepción, sin atribuir de inmediato significado a cada bit.

El parser de investigación acepta una trama Raise solo si tiene cabecera `0x2e`, longitud coherente con el tercer byte y checksum `sum(frame) % 256 == 0x2d`. Conserva la carga original; los [informes CAN](CAN_RESEARCH_2026-09-21.md) separan mensajes válidos, interpretación y campos pendientes.

Otros caminos ensayados tuvieron menos valor: broadcasts supuestos que no emitieron datos, logcat sin privilegios con diagnósticos de la propia app pero sin tramas CAN, y snapshots periódicos que podían perder cambios breves. Las pruebas de emulador verificaron compatibilidad Android, pero no sustituyeron una captura en hardware.

## Límite de seguridad

El host y `PvCanset` también exponen operaciones que cambian configuración o envían comandos. La investigación publicada aquí usa recepción y análisis estático; no demuestra el contrato de transmisión de la radio instalada. El [estudio TPMS](TPMS_CAN_RESEARCH_2026-10-20.md) distingue el comando lógico hallado en el plugin de una transmisión realmente observada.
