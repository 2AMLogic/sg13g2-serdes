* R18 pad-capacitance bench on the EXTRACTED pad-metal capacitance (issue #94, DR-012).
* Pad leg = lumped pad-metal C from layout extraction + the PDK ESD clamp diodes.
* Cmetal = 70.66 fF: `klt extract --deck sg13g2 --parasitics` on pad_esd.gds, net padp, WITH bondpad TM2
*   (layout/analog/pads/records/2026-11-12-fc8a7fa/record.md; padn identical). Interconnect C to substrate only.
* NOT INCLUDED: bondwire/package, pad-to-pad coupling, any distributed 5 GHz effect, and the 4.57 ohm series
*   rsil (OSDI model not simulated here, sim/README.md); Cmetal is quasi-static, not a 5 GHz extraction.
* Three legs show the budget split: total (metal + both clamps), metal only, ESD only.
Vdd vdd 0 1.2
Vp padp 0 dc 0.6 ac 1
Cm padp 0 70.66f
XDh vdd padp 0 diodevdd_2kv m=1
XDl vdd padp 0 diodevss_2kv m=1
Vpm padm 0 dc 0.6 ac 1
Cmo padm 0 70.66f
Vpe pade 0 dc 0.6 ac 1
XDh2 vdd pade 0 diodevdd_2kv m=1
XDl2 vdd pade 0 diodevss_2kv m=1
* Probes: H sources, branch current for 1 V ac; C = -Im(I)/(2 pi f) is computed in the record (klayout-tools#4217).
Hip iz 0 Vp 1
Him izm 0 Vpm 1
Hie ize 0 Vpe 1
