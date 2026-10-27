# Consumo de combustible: contraste del historial completo

Fecha: 2026-10-01. Investigación de datos históricos para determinar si permiten identificar consumo instantáneo y promedio. Se realizaron únicamente lecturas y análisis local.

## Hipótesis de visualización posterior

La lectura del tablero motivó una interpretación provisional del campo final como u16 LE / 100 en L/100 km, con conversión recíproca a km/L. La unidad sigue siendo una **suposición**, no una validación del protocolo. No se calcula un promedio nuevo ni litros del viaje a partir de estas muestras. El consumo instantáneo continúa sin identificarse; las conclusiones del análisis original se conservan debajo.

## Conclusión

- **Instantáneo:** no se identificó una señal utilizable en la exportación actual de la radio. El campo pendiente junto al odómetro no sirve como lectura instantánea: puede mantenerse igual durante numerosos recorridos con cambios de velocidad y detenciones. Tampoco hay un caudal de combustible o MAF identificado para calcularlo indirectamente. Esto no demuestra que el vehículo carezca de esos datos en su CAN original u otra interfaz.
- **Promedio:** el campo final de `0x7D/04` sigue siendo un candidato, no un consumo validado. El historial permite caracterizarlo, pero no determina su significado, escala o período de promedio. El código de referencia Changan examinado no aporta esa definición.
- La limitación no es falta de cantidad de capturas. Falta una referencia independiente que identifique el campo y sus unidades, como documentación del protocolo exacto o lecturas del tablero sincronizadas con cambios del campo. Reunir más capturas sin esa referencia no resuelve automáticamente la ambigüedad.

## Alcance y calidad

Se consultó la lista completa `raw/passive.v2`: 110 fragmentos de 105 sesiones. Se excluyeron 3 sesiones sintéticas `smoke-test`. Se descargaron los 107 fragmentos restantes, correspondientes a 102 sesiones, sin modificar datos de producción. No faltó ningún fragmento.

Se analizaron 754.601 registros, con **680.434 tramas válidas** en 89 sesiones y **11 formatos de mensaje**. Otros registros corresponden a GPS, inicio/parada, diagnóstico y estado. Se omitieron 37 registros que no pudieron interpretarse como JSON; no se asumió que contuvieran mediciones de combustible. Las tramas contabilizadas cumplen cabecera, longitud exacta y checksum Raise.

El análisis previo del 21 de septiembre cubría 56 sesiones y 324.588 tramas. Esta revisión incluye los envíos posteriores, hasta el 1 de octubre UTC.

## Campo candidato

`0x7D`, longitud 6, datos `[04, odómetro u24 LE, campo u16 LE]`:

- 642 muestras en 73 sesiones.
- Las lecturas absolutas del odómetro se omiten por privacidad; su variación relativa se conserva en el análisis.
- Campo final entre 670 y 1020; todos los valores observados son múltiplos de 10.
- En pares consecutivos dentro de un mismo segmento de reloj hubo 51 cambios del campo: 49 descensos de 10 y dos saltos hacia 1020. Esos 51 cambios conservaron el mismo entero de odómetro; por tanto, el campo cambia independientemente de sus incrementos de kilómetro.
- Las dos secuencias de salto y descenso no establecen por sí mismas que haya ocurrido un reinicio del consumo. No hay marcas del usuario que identifiquen ese evento.

Capturas en las que todas las muestras del campo tuvieron el mismo valor:

| Valor sin unidad | Distancia CAN observada | Tiempo observado | Tiempo detenido observado | Velocidad máxima |
| --- | ---: | ---: | ---: | ---: |
| 670 | 107,56 km | 4,12 h | 16,9 min | 98,38 km/h |
| 680 | 147,70 km | 5,61 h | 20,6 min | 110,53 km/h |
| 750 | 291,08 km | 9,33 h | 25,0 min | 117,16 km/h |

Son sumas de capturas, no un único intervalo continuo. Las distancias se integran entre muestras de velocidad separadas por hasta 3 segundos, sin cruzar cambios de reloj superiores a un día ni retrocesos mayores a 3 segundos. Se consideran detenidos los intervalos cuyos dos extremos están bajo 1 km/h. Los huecos y bordes no se rellenan. La ausencia de nuevas muestras del candidato no prueba que su fuente física se haya mantenido constante entre ellas; sí impide utilizarlo como una lectura instantánea confiable.

Si se supusiera —sin validación— que 670 significa 6,70 km/L, se mostraría ese valor. Si significara 6,70 L/100 km, correspondería a **14,93 km/L**. Ambas interpretaciones producen números posibles, pero son distintas; confirmar que el tablero usa km/L no demuestra qué unidad retransmite el decodificador. Ni siquiera está establecido que el campo represente combustible.

Las 240.528 tramas de velocidad `0x7D/03` tienen sus dos bytes finales en cero. El firmware los denomina velocidad promedio; no son una fuente alternativa de consumo.

## Contraste con el fabricante

Se recuperó de nuevo el [firmware público XY AUTO 9212A 8.0.1](http://carsoftdown.xygala.com/public/upload/softs/2024/01-04/gongban_9212A_1024x768_hw-ota-v8.0.1.zip) y se verificó su SHA-256 contra la investigación anterior:

`0e7e8c965a7c2a394ce6b1a33a6c3b90ddb860fbd129b0df4f6736b028ccfff7`

Se reconstruyó su imagen de sistema como archivo, sin montarla, arrancarla ni instalarla. Se inspeccionaron estáticamente el host CanBus 1.020 y el plugin Raise Changan `/media/CanBus/plugin/1/15/P1_008.apk`; el SHA-256 del plugin volvió a coincidir:

`1d7e3efff45171d22f820a69fa4294845c9c386aa73dbdb260f2ca0685984787`

- `CanbusLight_P.raiseTurnSignal_7D` define velocidad instantánea y promedio en `0x7D/03`, dividiendo enteros u16 LE por 100. No interpreta el campo final de `0x7D/04`.
- El botón genérico `mIconViewOil` de `MainActivity_P` no implementa una pantalla de consumo para este plugin. Su presencia como recurso compartido no demuestra soporte de combustible.
- Como contraste, los plugins Raise Honda y Suzuki sí contienen actividades explícitas de consumo (`Raise_Honda_Oil_Activity`, `Raise_Suzuki_Oil_Activity`). Interpretan el comando **0x33**, subtipo 1, con al menos 15 bytes y bits que distinguen mpg, km/L y L/100 km. No apareció ningún comando 0x33 en las capturas del Changan. Esas fórmulas no se transfieren a otro mensaje o marca.

El firmware de referencia no es una extracción del APK instalado, por lo que esta inspección no prueba identidad total con el software de la radio ni ausencia absoluta de otras interfaces de combustible.

## Reproducción y seguimiento

[Evidencia agregada](CAN_FUEL_EVIDENCE_2026-10-01.json), sin coordenadas GPS ni identificadores de dispositivos/sesiones.

El script [research-can-fuel.py](../scripts/research-can-fuel.py) procesa una descarga privada que contiene `uploads.json` y `chunks/<chunk_id>.raw`:

```sh
python3 scripts/research-can-fuel.py PRIVATE_INPUT_DIRECTORY PUBLIC_JSON
```

Produce el agregado público y conserva intermediarios privados dentro del directorio de entrada. Excluye sesiones sintéticas, comprueba la integridad de las tramas y separa discontinuidades del reloj. Se ejecutó sobre la descarga completa y reprodujo 680.434 tramas y 642 muestras del candidato.

Las capturas, los APKs de referencia y los resultados intermedios permanecen fuera del repositorio. Para identificar el promedio, el siguiente paso es comparar lecturas **fechadas** del tablero con este campo, idealmente antes y después de un cambio visible o reinicio del promedio. Para obtener instantáneo, se necesita una señal adicional identificada de consumo/caudal o un conjunto suficiente de señales del motor.
