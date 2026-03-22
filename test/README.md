Multi-Tool SoC Verification Suite
This directory contains the automated, cycle-accurate Python testbench for the Multi-Tool SoC. It uses cocotb to drive the hardware FSM, inject simulated physical noise, and verify the mathematical outputs of the coprocessors.

Test Coverage
This is a comprehensive suite that verifies both the mathematical logic and the physical resilience of the silicon FSM:

Mechanical Chitter Resilience: Simulates violent, randomized switch bouncing on the Enter pin to prove the hardware debouncer and edge-detectors ignore electrical noise.

Mathematical Vectors: Automatically loops through edge-case math problems for the Euclidean GCD FSM, the Integer Square Root engine, and the Cryptographic LFSR.

UI Multiplexing: Cycle-accurately reads the 7-segment display multiplexer out of the "data eye" to reconstruct the answer.

Physical Vulnerabilities: Simulates chaotic human behavior, including "Fat Finger" asynchronous data latching, "Impatient Hold" switch locks, and mid-calculation "Rage Quit" asynchronous resets.

How to Run Locally
If you have the OSS CAD Suite or Icarus Verilog installed, you can run the RTL simulation locally:

Bash
make -B
To run the gate-level simulation (testing the actual synthesized physical gates), first ensure your project has been hardened by GitHub Actions, then run:

Bash
make -B GATES=yes
Cloud CI/CD (GitHub Actions)
This testbench is fully integrated into the Tiny Tapeout GitHub Actions pipeline. Every push to the main branch automatically triggers both the RTL and Gate-Level (gl_test) testbenches in the cloud.

Viewing the Waveforms
If a test fails or you want to inspect the exact clock-cycle timing of the FSM and multiplexer, a .fst waveform file is generated.

Using GTKWave:

Bash
gtkwave tb.fst tb.gtkw
Using Surfer:

Bash
surfer tb.fst