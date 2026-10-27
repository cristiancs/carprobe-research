# CAN discovery audit — 2026-09-21

Read-only analysis of all 56 available raw/passive.v2 sessions: 363,547 records and 324,588 valid framed CAN messages. All sessions parsed successfully. Counts describe messages, not physical activations. KEY broadcasts are separate from the CAN frame total.

| Signal | Status | Messages | Sessions | Distinct payloads |
| --- | --- | ---: | ---: | ---: |
| 0x29 · 2 B/candidate | candidate | 112,449 | 44 | 7796 |
| 0x30 · 1 B/candidate | candidate | 602 | 34 | 2 |
| 0x20 · 2 B/unknown | unknown | 740 | 20 | 18 |
| 0x3A · 3 B/unknown | unknown | 50 | 13 | 8 |
| KEY/unknown | unknown | 394 | 20 | 10 |
| 0x7D/0x04 · 6 B/unknown | unknown | 300 | 34 | 300 |
| 0x7D/0x03 · 5 B/decoded | decoded | 113,273 | 36 | 1931 |
| 0x7D/0x08 · 3 B/decoded | decoded | 75,176 | 42 | 1148 |
| 0x7D/0x01 · 2 B/decoded | decoded | 17,216 | 37 | 3 |
| 0x22 · 4 B/unknown | unknown | 105 | 14 | 13 |
| 0x7D/0x01 · 2 B/unknown | unknown | 4,640 | 28 | 7 |
| 0x52 · 2 B/unknown | unknown | 35 | 2 | 19 |
| 0xFF · 19 B/unknown | unknown | 2 | 2 | 1 |

Unknown indicator payloads include `01 18`, `01 c0`, `01 c8`, `01 80`, `01 d0`, `01 88`, and `01 d8`. These may combine bits, but no additional physical state is assigned without marked validation. The 0x7D/0x04 channel has 300 distinct payloads; an odometer interpretation remains unconfirmed. 0x3A and 0x52 also require validation. The 0xFF payload contains an ASCII identifier followed by a zero byte; this looks like a decoder identifier rather than a physical vehicle event, but remains unclassified.

This audit is a historical snapshot, not a live fleet-wide counter. No claims of pedal, cruise, door, belt, or headlamp decoding are added.
