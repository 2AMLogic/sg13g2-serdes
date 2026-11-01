# sta-paths.tcl -- per-module worst setup path of the synthesized digital
# partition (OpenSTA via openroad, ideal clock, no wires). Driven by
# scripts/sta-paths.sh, which substitutes the @LIB@ ... @PERIOD@ tokens (the
# openroad wrapper scrubs the environment, so env vars cannot carry them).
read_liberty @LIB@
read_lef @LEF_TECH@
read_lef @LEF_CELL@
read_verilog @NETLIST@
link_design @TOP@
create_clock -name clk -period @PERIOD@ [get_ports clk]
puts "== global worst setup path =="
report_checks -path_delay max -group_path_count 1 -format full
foreach m {u_chk u_gen u_pd u_flt u_lb u_eye u_ctrl} {
  puts "== worst setup path ending in $m =="
  set pins [get_pins -quiet -hierarchical "$m/*/D"]
  if {[llength $pins] == 0} { puts "(no flops matched)"; continue }
  report_checks -path_delay max -to $pins -group_path_count 1 -format full
}
puts "== worst setup path to a top-level output =="
report_checks -path_delay max -to [all_outputs] -group_path_count 1 -format full
