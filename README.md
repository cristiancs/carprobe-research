# CarProbe research

Investigación independiente de una radio XY AUTO con decodificador Raise/Changan CS15. El repositorio reúne hallazgos sobre plataforma, recepción pasiva, señales CAN, captura resistente a cortes, análisis de viajes, firmware e integración Android. Incluye evidencia agregada y scripts para repetir parte del análisis sobre capturas propias.

## Mapa de investigación

| Área | Informe |
| --- | --- |
| Plataforma y origen real de las tramas | [Identidad, extracción estática, Binder y broadcast de recepción](docs/PLATFORM_AND_RECEIVE_PATH.md) |
| Captura y subida | [Recuperación tras cortes, sincronización finita y descompresión GZIP](docs/CAPTURE_AND_SYNC.md) |
| Interpretación de recorridos | [Relojes corregidos por GPS, distancia, unión de sesiones y calidad](docs/JOURNEY_ANALYSIS.md) |
| Integración de la radio | [Zona horaria, hotspot/Bluetooth y puente BLE descartado](docs/RADIO_INTEGRATION.md) |
| Audio y actualizaciones | [Salto de volumen y límites de la investigación](docs/AUDIO_FIRMWARE.md) |
| Señales del vehículo | [Informes y evidencia CAN, combustible y TPMS](#resultados-principales) |

## Resultados principales

| Tema | Evidencia | Límite |
| --- | --- | --- |
| Velocidad | `0x7D/03`, entero u16 little-endian dividido por 100 km/h | Confirmada por código de referencia y contraste con GPS; el firmware examinado no necesariamente coincide byte por byte con la unidad instalada. |
| Intermitentes | Bits 4 y 3 de `0x7D/01` indican izquierda y derecha | Los otros bits requieren identificación adicional. |
| Odómetro | Campo u24 little-endian de `0x7D/04`; sus incrementos concuerdan con distancia integrada | La lectura absoluta aún requiere cotejo con el tablero. |
| Combustible | Campo final de `0x7D/04` como candidato a promedio | Significado y unidad no están validados; no se encontró una señal de consumo instantáneo. |
| TPMS | El plugin de referencia contiene una solicitud de reinicio y respuestas `0x52/0x0C` | La transmisión y el resultado en el vehículo no están confirmados. |

## Informes de protocolo y firmware

- [Descubrimiento inicial](docs/CAN_DISCOVERY_AUDIT.md) y [decodificación CAN](docs/CAN_RESEARCH_2026-09-21.md), con [evidencia numérica](docs/CAN_RESEARCH_EVIDENCE.json).
- [Estudio del campo de combustible](docs/CAN_FUEL_RESEARCH_2026-10-01.md), con [agregados](docs/CAN_FUEL_EVIDENCE_2026-10-01.json).
- [Comparación de firmware 9212A/9212B](docs/FIRMWARE_AB_COMPARISON.md), con [evidencia resumida](docs/FIRMWARE_AB_EVIDENCE.json).
- [Investigación de TPMS](docs/TPMS_CAN_RESEARCH_2026-10-20.md).

## Reproducción

Los scripts usan Python 3 y su biblioteca estándar. Trabajan con capturas obtenidas por el investigador; este repositorio no incluye recorridos, coordenadas GPS, tokens, APK ni firmware del fabricante.

```sh
python3 scripts/research-can.py PRIVATE_NDJSON_DIRECTORY PRIVATE_OUTPUT_JSON
python3 scripts/research-can-fuel.py PRIVATE_INPUT_DIRECTORY PUBLIC_AGGREGATE_JSON
```

`research-can.py` produce detalles por sesión y **su salida debe permanecer privada**. Los fragmentos de una misma sesión deben concatenarse en orden antes de ejecutarlo. `research-can-fuel.py` genera un agregado público, pero escribe intermediarios privados dentro del directorio de entrada. Revise cualquier salida antes de compartirla.

La evidencia procede de un vehículo y de firmware de referencia descargado públicamente. Los textos separan observaciones de campo, análisis estático, hipótesis y trabajo pendiente. No demuestran compatibilidad universal ni constituyen instrucciones para transmitir comandos o instalar firmware. Los binarios del fabricante solo se citan por URL y hash.

Los scripts y textos originales de este repositorio se publican bajo la [licencia MIT](LICENSE). Los paquetes y binarios del fabricante conservan sus propios derechos y no se redistribuyen aquí.
