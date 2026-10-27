# TPMS reset in XY AUTO / Raise Changan reference firmware

The public 9212A 8.0.1 OTA was downloaded again and verified against the previously recorded SHA-256 (`0e7e8c965a7c2a394ce6b1a33a6c3b90ddb860fbd129b0df4f6736b028ccfff7`). Its Raise/Changan plugin is `/media/CanBus/plugin/1/15/P1_008.apk`, SHA-256 `1d7e3efff45171d22f820a69fa4294845c9c386aa73dbdb260f2ca0685984787`. These are reference firmware files, not APKs read from the installed B7.3.8 radio.

## Findings

- The plugin contains `Raise_Chana_Set_Activity`. Its 13th button is **Tire pressure reset setting**. Its choice list contains only **OK**. Selecting it calls the plugin's CAN sender with data type `131` (`0x83`), setting ID `12` (`0x0C`), value `1` (`0x01`). The plugin first requests settings data on resume and interprets incoming `0x52` setting responses. It can show reset progress, success and failure from `0x52`/setting `12`; a sent command alone is not proof of completion.
- The same plugin's `MainActivity_P` shows the **No Car Information** message only when no feature icons are visible. For both reference CS15 profiles (`Canset_User` `1015004` and `1015017`), its vehicle-settings icon is visible. The default branch also enables that icon. Seeing the empty screen therefore suggests that the installed host loaded a different plugin, failed to load the Raise/Changan plugin, or follows code different from this reference image. The message does not establish which of those occurred.
- CAN Pro's host reads CAN selection from metazone, looks up the selected plugin in `/sdcard/CanBus/plugin/<canId>/<brandId>/`, and writes the derived profile to Android `Settings.System.Canset_User`. It uses a generic fallback plugin when the selection is invalid. Changing metazone or copying reference APKs without verifying the installed unit would be unsafe.
- CarProbe has only validated the passive receive path on this car. The reference plugin sends through a vendor `canbus_service` Binder setter, with framing dependent on the configured baud rate. The installed radio's command transport, selected profile and TPMS acknowledgement have not been checked. CarProbe must not report a successful reset based only on sending these three logical bytes.

## Read-only check in CarProbe

**Ajustes → Presión de neumáticos** displays the current `Canset_User` and `Canset_itemStr` reported by Android. `1015004` or `1015017` matches the two CS15 profiles in the reference firmware; other values explain why the reference CS15 UI may not apply. This readout is diagnostic, not proof that the matching plugin loaded. A physical-radio check of the installed plugin, CAN Pro screen and reset response remains necessary before adding a direct transmit path.

## Field observation

Switching from the 2016–2017 CS15 profile to the 2019 CS15 profile exposed **Tire pressure reset** in the vehicle settings screen. The profile ID and the result displayed by CAN Pro during the reset were not captured. An earlier observation of the old profile showed `1015004` and **Protocol connectionless**; do not carry that status forward as a diagnosis of the new profile.

In a subsequent `raw/passive.v2` capture, three received frames arrived in sequence within approximately 0.8 seconds:

| Received frame | Parsed setting | Value |
| --- | --- | --- |
| `2e52020c049b` | `0x52` / `0x0C` | `0x04` |
| `2e52020c039c` | `0x52` / `0x0C` | `0x03` |
| `2e52020c009f` | `0x52` / `0x0C` | `0x00` |

Two earlier `0x52` frames contained `00 ff`, not setting `0x0C`. Other CAN frames continued immediately before and after the three-frame sequence. A `xy.auto.canbus.connectionsta` broadcast reported `true` repeatedly about one to two minutes beforehand; no contemporaneous false broadcast was captured. The TPMS warning light was already off before this test, so lamp extinction cannot validate its outcome. This is strong evidence of a TPMS-related response sequence, but the installed plugin's value meanings and the vehicle's final TPMS state remain unverified. CarProbe receives only the vendor's inbound broadcast and did not capture the outbound command or its exact transport framing. The reference plugin's logical `0x83 / 0x0C / 0x01` command remains a reference finding, not a field-captured transmit frame.

The installed host's outbound Binder transaction, interface token, argument layout and baud-dependent frame remain unverified. The inbound `rxpduses` broadcast cannot substitute for the outbound transport. A matching `0x52 / 0x0C` response, with validated value meanings, would be needed to assess completion.
