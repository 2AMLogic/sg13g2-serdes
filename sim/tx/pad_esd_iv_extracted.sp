* R19 clamp-characteristic bench on the EXTRACTED pad_esd layout (issue #94, DR-013).
* Devices are what `klt extract --deck sg13g2 --parasitics` found in pad_esd.gds
* (layout/analog/pads/records/2026-11-12-fc8a7fa/extract-pad_esd.json), padp leg:
*   dpantenna a=padp c=rail   area 35.0028 um2  perimeter 58.08 um   (high-side clamp, pad -> VDD)
*   dantenna  a=vsubs c=padp  area 35.0028 um2  perimeter 58.08 um   (low-side clamp, VSS -> pad)
*   rsil      cp--padp        5.119632 ohm (extracted r_ohm, ideal R here: OSDI r3_cmc not simulated, sim/README.md)
* The PDK dantenna/dpantenna models are fitted for REVERSE bias only; forward-direction bipolar
* effects are not modelled (PDK diodes.lib). So the forward IV here is a lower bound on a real clamp.
* DC IV only. NOT a TLP or HBM result and NOT an ESD qualification claim.
Vdd vdd 0 1.2
Vp src 0 dc 0
Rs src padp 5.119632
Xdp padp vdd dpantenna DEV_A=35.0028 DEV_P=58.08
Xdn 0 padp dantenna DEV_A=35.0028 DEV_P=58.08
