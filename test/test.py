# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge
import math

SEGMENTS = {
    0: 0x3F, 1: 0x06, 2: 0x5B, 3: 0x4F, 4: 0x66, 5: 0x6D, 6: 0x7D, 7: 0x07,
    8: 0x7F, 9: 0x6F, 10: 0b01011111, 11: 0b01111100, 12: 0b00111001, 13: 0b01011110, 14: 0b01111001, 15: 0b01110001
}

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    

    dut._log.info("Test project behavior")

    test_cases = [
        (12, 8),
        (15, 5),
        (8, 9),
        (7, 12),
        (13, 13),
        (9, 6),
        (1, 4)
    ]

    for a in range (16):
        for b in range (16):
            test_cases.append((a, b))

    for a, b in test_cases:
        expected = math.gcd(a, b)
        cocotb.log.info(f"testing gcd {a}, {b}")

        dut.ui_in.value = (b << 4) | a
        
        dut.uio_in.value = 1
        await ClockCycles(dut.clk, 1)
        dut.uio_in.value = 0

        for i in range (100) :
            await RisingEdge(dut.clk)
            if dut.uo_out.value != 0x40:    #wait till dash goes away to read result
                break
        expected_segments = SEGMENTS.get(expected, 0x00)
        actual_segments = int(dut.uo_out.value)

        assert actual_segments == expected_segments, \
            f"Failed GCD: {a}, {b} expected = {hex(expected_segments)} got: {hex(dut.uo_out.value)}" #test result and log if failed
        
        await ClockCycles(dut.clk, 5)