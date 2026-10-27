# Investigación CAN Raise / Changan — 21 de septiembre de 2026

Actualización: la [revisión de combustible del 1 de octubre](CAN_FUEL_RESEARCH_2026-10-01.md) amplía el análisis a 102 sesiones reales y 680.434 tramas. El campo final de `0x7D/04` continúa sin unidad ni significado físico confirmados; no se debe tratar como consumo instantáneo o promedio validado.

## Resultado

Se analizaron las **56 capturas raw/passive.v2 disponibles**, con **363.547 registros y 324.588 tramas válidas**, y se contrastaron con el plugin Raise Changan incluido en el firmware de referencia XY AUTO 9212A 8.0.1. El resultado supera el inventario inicial: varias familias ya tienen interpretación sustentada por código y observaciones.

**Límite de procedencia:** este plugin proviene del firmware descargado, no de una extracción del APK instalado. El catálogo incluye CS15 2016–2017 y 2019 dentro del mismo plugin. La coincidencia de formatos y broadcasts permite identificar funciones, pero no demuestra que todos los ajustes y perfiles sean idénticos al vehículo 2022. No se transmitieron comandos al vehículo ni se ejecutó código del fabricante.

| Señal | Hallazgo | Evidencia y límite |
| --- | --- | --- |
| `0x20`, 2 bytes | Botones del volante: código y estado | `Raise_Chana_Key` consume este comando. 740 mensajes. Los 394 broadcasts KEY tienen un 0x20 a ≤0,5 s. Las funciones son remapeables; el broadcast KEY revela la orden resultante. |
| `KEY` | Volumen +/−, siguiente/anterior, silencio e inicio | `ENUM_KEY` identifica 0C/0D, 0A/0B, 05 y 29. Diez payloads corresponden a **seis funciones**, no diez botones. Incluyen pulsación/liberación y repeticiones. |
| `0x22`, 4 bytes | Radar trasero de estacionamiento | `car_radar.json` asigna los bytes a canales 4–7. 105 mensajes en 14 capturas; 104 tienen velocidad CAN a ≤3 s, máximo 2,19 km/h y mediana 0,50 km/h. Los valores son niveles, no metros ni pedal de freno. |
| `0x3A`, 3 bytes | Estado de puertas, capó y maletero | `car_door.json` usa bits 0–5 del primer byte; `isDataPass` acepta al menos la longitud requerida, no exige exactamente 2 bytes. 50 mensajes en 13 capturas; los dos bytes finales son FF FF y quedan sin interpretar. Los lados pueden invertirse por configuración. |
| `0x30`, 1 byte | Solicitud de cámara derecha | `CanbusRight_P` usa bit 7 para `enterRightVideo`. 602 mensajes. Esto no demuestra que haya cámara instalada o que se muestre su imagen. |
| `0x52`, 2 bytes | Respuesta de configuración del vehículo | `Raise_Chana_Set_Activity.initDataState` interpreta identificador de ajuste + valor. 35 mensajes con 19 payloads en dos capturas. No se atribuyen nombres específicos de ajustes sin comprobar perfil. |
| `0x29`, 2 bytes | Dirección/trayectoria redundante | `car_trajectory.json`: entero firmado big-endian, dirección izquierda positiva en referencia. 80.154 pares a ≤200 ms con 0x7D/08: r = −0,997615. La unidad física sigue sin calibrar. |
| `0x7D/01`, 2 bytes | Intermitentes como **bits independientes** | `CanbusLight_P.rx360AppData` extrae bit 4 izquierdo y bit 3 derecho. `18` contiene ambos; `C8`, `D0`, `D8`, `88` siguen incluyendo información válida de intermitentes. No se infiere el estado del interruptor de emergencia. |
| `0x7D/04`, 6 bytes | Odómetro acumulado inferido con evidencia fuerte | Subtipo + u24 little-endian; 300 mensajes en 34 capturas. Se omiten las lecturas absolutas del vehículo; falta cotejarlas con el tablero. Los dos últimos bytes permanecen sin identificar. |
| `0xFF`, 19 bytes | Texto identificador | Cadena ASCII + NUL, observada dos veces; el valor se omite por prudencia. No es un evento de conducción y no se interpreta la semántica de sus componentes. |

## Comprobación del odómetro

La comparación agregada entre la primera y última lectura de las 34 capturas da **245 km** de incremento frente a **245,19 km** integrados de velocidad CAN, después de ordenar los fragmentos y corregir discontinuidades mayores a 24 horas. Esta comparación no es una calibración independiente: ambas señales vienen del mismo decodificador y los relojes tienen correcciones.

Para comprobar que la coincidencia no depende del total agregado:

- Se compararon intervalos entre **incrementos observados**, evitando usar actualizaciones del campo adicional como si fueran nuevos límites de kilómetro.
- Se excluyeron cruces de correcciones del reloj; la integración excluye huecos superiores a tres segundos.
- **82 intervalos** con cobertura CAN ≥90% contienen un incremento de 1 km cada uno. Error absoluto mediano: **3,73 m**; máximo: **43,39 m**. La integración utiliza solo las muestras interiores y puede subestimar bordes/huecos.
- Como contraste independiente, **109 intervalos** con cobertura de velocidad GPS ≥90% y precisión reportada de 1–25 m tienen error absoluto mediano de **49,34 m por km**. GPS no confirma el kilometraje absoluto del tablero.

Esto justifica mostrar «Odómetro inferido» y su lectura, manteniendo explícita la comprobación pendiente del valor absoluto. No se usa para reemplazar la distancia de viaje ni para puntuar conducción.

## Botones

| Orden de la radio | Código KEY | Mensajes, incluyendo estados/repeticiones |
| --- | --- | ---: |
| Subir volumen | 0C | 97 |
| Bajar volumen | 0D | 117 |
| Siguiente | 0A | 166 |
| Anterior | 0B | 2 |
| Silencio | 05 | 2 |
| Inicio | 29 | 10 |

La proximidad temporal no implica emparejamiento causal exclusivo: en una de las 394 asociaciones la trama más cercana tiene estado raw 0 mientras el broadcast indica pulsación. Puede haber repetición o reordenamiento de entrega. Por eso no se cuentan estos mensajes como pulsaciones físicas independientes ni se fija un mapeo universal de los códigos raw 0x20.

## Iluminación: lo que todavía no se puede separar

Hay 48 broadcasts `xy.xygala.lamplet`. Los **14 con estado 1** tienen una trama `0x7D/01 C0` a menos de 100 ms. Nueve broadcasts con estado 0 tienen trama a ≤1 s sin los bits altos; los otros 25 no tienen pareja en esa ventana.

Esto sustenta una relación de los bits 6/7 con iluminación, pero **no permite distinguir aún posición, bajas o altas**. El estado 80 aparece también, por lo que no sería correcto renombrar todo C0/80 como una misma luz confirmada. Se decodifican los bits de intermitentes y se conservan los restantes como pendientes.

El campo final de 0x7D/04 toma valores como 680 y 750, y en una captura cambia de 1020 hacia valores menores. Una interpretación de consumo medio resulta plausible, pero no cuenta con prueba suficiente y no se incorpora como combustible, RPM ni autonomía.

No apareció evidencia suficiente para declarar identificados pedal de freno, acelerador, cinturón o estado explícito de control crucero.

## Consecuencias para el decodificador

- Explorador CAN con interpretación de cada mensaje y explicación de su evidencia/límites.
- Botones agrupados por orden, manteniendo sus estados y payloads originales.
- Odómetro inferido visible en Señales, también para capturas históricas.
- Intermitentes izquierdo/derecho extraídos por bits, permitiendo ambos encendidos y otros bits simultáneos. Se cuentan flancos de encendido; mensajes repetidos no añaden destellos. Se separan huecos y correcciones de reloj.
- Velocidad instantánea corregida a **u16 LE / 100**, tal como la implementa el plugin. Los otros dos bytes corresponden a un campo separado etiquetado Average_speed en el firmware. En todo el historial ambos fueron cero, por lo que el cambio no altera velocidades históricas.
- No se asignan metros a niveles de radar ni unidades físicas a dirección. Tampoco se cambian los datos raw.

Evidencia numérica sin recorridos GPS: [CAN_RESEARCH_EVIDENCE.json](CAN_RESEARCH_EVIDENCE.json).

## Fuentes y reproducción

Fuente primaria: paquete del fabricante descrito en [FIRMWARE_AB_COMPARISON.md](FIRMWARE_AB_COMPARISON.md), disponible en [archivo XY AUTO 9212A 8.0.1](http://carsoftdown.xygala.com/public/upload/softs/2024/01-04/gongban_9212A_1024x768_hw-ota-v8.0.1.zip).

Dentro de su imagen system: `/media/CanBus/plugin/1/15/P1_008.apk`.

SHA-256 del plugin: `1d7e3efff45171d22f820a69fa4294845c9c386aa73dbdb260f2ca0685984787`.

Referencias extraídas mediante análisis estático:

- `can1_020.json`: Raise id 1, Chana id 15, perfiles CS15 4 y 17.
- `com/kyhero/car/myplugin/canbus/CanbusKey_P.java`: `Raise_Chana_Key`, `sendKey` y remapeo.
- `com/canbus/canconst/ENUM_KEY.java`: nombres de códigos y estados.
- `assets/car_radar.json`, `JsonRadar.java` y `RadarView.java`: canales y niveles.
- `assets/car_door.json`, `JsonDoor.java`, `CanbusDoor_P.java`, `ToolClass.isDataPass`: campos, longitudes mínimas e inversión de lados.
- `CanbusRight_P.java`: cámara derecha.
- `Raise_Chana_Set_Activity.java`: respuestas 0x52.
- `assets/car_trajectory.json`: entero de dirección.
- `CanbusLight_P.java`: intermitentes independientes y velocidad u16.

Los originales y resultados intermedios no se incorporan al repositorio; tampoco se incluyen APKs ni recorridos GPS. El análisis estadístico reproducible está en [`scripts/research-can.py`](../scripts/research-can.py) y recibe un directorio de NDJSON privados y una ruta de salida JSON privada. Los fragmentos de cada captura deben concatenarse primero en orden de captura. El informe inicial [CAN_DISCOVERY_AUDIT.md](CAN_DISCOVERY_AUDIT.md) conserva el inventario previo a esta interpretación.
