* SMOKE (toolchain bring-up, issue #3): DC Gummel sweep of one SG13G2 HBT.
* The device (npn13G2, default geometry) and bias are PLACEHOLDERS to prove the
* HBT model loads at each HBT corner section. They are NOT design choices and
* carry no spec value.
* Circuit body only: klt sim supplies .lib / .control / .end.
Vc c 0 dc 1.0
Vb b 0 dc 0
XQ c b 0 0 npn13G2
