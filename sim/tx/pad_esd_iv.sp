* R19 clamp-characteristic bench (issue #94): DC current of the PDK ESD clamp diodes
* (diodevdd_2kv to vdd, diodevss_2kv to vss) versus pad voltage, per PVT corner.
* This is a DC IV of the clamp models, NOT a TLP or HBM result and NOT an ESD
* qualification claim. Series rsil omitted (OSDI model, sim/README.md).
Vdd vdd 0 1.2
Vp padp 0 dc 0
XDh vdd padp 0 diodevdd_2kv m=1
XDl vdd padp 0 diodevss_2kv m=1
