# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge
import math
import random

# ==========================================    this is line 10
# HARDWARE DICTIONARIES
# ==========================================

# Maps the physical 7-segment LED wires (without the Decimal Point) back to an integer
SEG_TO_INT = {
    0b0111111: 0, 
    0b0000110: 1, 
    0b1011011: 2, 
    0b1001111: 3, 
    0b1100110: 4, 
    0b1101101: 5, 
    0b1111101: 6, 
    0b0000111: 7, 
    0b1111111: 8, 
    0b1101111: 9
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

async def apply_hardware_reset(dut):
    """
    TASK 1: Boot up the chip and engage the DFT Fast-Forward Pin.
    """
    dut._log.info("Initiating strict hardware reset...")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0x80 #(This turns on Pin 7: Fast-Forward Mode!)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 20)
    assert dut.uo_out.value == 0, f"Failed! Expected output to be zero during reset, got {bin(dut.uo_out.value)}"
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 20)
    
    pass

async def chitter_press_enter(dut, debounce_limit=100):
    """
    TASK 2: Simulate a violent mechanical switch bouncing on ui_in[7].
    """
    # 1. The Press Bounce (Metal making contact)

    for i in range (5):
        dut.ui_in.value = int(dut.ui_in.value) | 0x80
        await ClockCycles(dut.clk, random.randint(2, 15))
        dut.ui_in.value = int(dut.ui_in.value) & 0x7F
        await ClockCycles(dut.clk, random.randint(2, 15))

    # 2. The Solid Hold (Human finger fully down)

    dut.ui_in.value = int(dut.ui_in.value) | 0x80
    await ClockCycles(dut.clk, debounce_limit + 50)

    # 3. The Release Bounce (Metal springing back)
    
    for i in range (5):
        dut.ui_in.value = int(dut.ui_in.value) | 0x80
        await ClockCycles(dut.clk, random.randint(2, 15))
        dut.ui_in.value = int(dut.ui_in.value) & 0x7F
        await ClockCycles(dut.clk, random.randint(2, 15))

    # 4. The Solid Release (Finger removed)

    dut.ui_in.value = int(dut.ui_in.value) & 0x7F
    await ClockCycles(dut.clk, debounce_limit + 50)

    pass

async def execute_app_lifecycle(dut, opcode, a, b, debounce_limit):
    """
    TASK 3: Navigate the OS, input the math, and visually read the 7-segment display!
    """
    # 1. LOAD THE DATA

    dut.ui_in.value = opcode
    await ClockCycles(dut.clk, 1)
    await chitter_press_enter(dut, debounce_limit)
    assert dut.uo_out.value == 0b01110111, f"Failed! Expected LOAD_A state, got {bin(dut.uo_out.value)}"

    dut.ui_in.value = a
    await ClockCycles(dut.clk, 1)
    await chitter_press_enter(dut, debounce_limit)
    assert dut.uo_out.value == 0b01111111, f"Failed! Expected LOAD_B state, got {bin(dut.uo_out.value)}"

    dut.ui_in.value = b
    await ClockCycles(dut.clk, 1)
    await chitter_press_enter(dut, debounce_limit)

    # 2. WAIT FOR THE DECIMAL POINT (Hundreds Digit)

    while (int(dut.uo_out.value) & 0x80) == 0:
        await RisingEdge(dut.clk)
    
    # 3. READ HUNDREDS
    
    segments = int(dut.uo_out.value) & 0x7F #mask out DP
    hundreds = SEG_TO_INT[int(segments)]

    # 4. READ TENS

    await ClockCycles(dut.clk, 105)
    assert (int(dut.uo_out.value) & 0x80) == 0, f"Failed! Expected DP led to stop after hundreds, got {bin(dut.uo_out.value)}"
    segments = int(dut.uo_out.value) & 0x7F
    tens = SEG_TO_INT[int(segments)]

    # 5. READ UNITS

    await ClockCycles(dut.clk, 105)
    assert (int(dut.uo_out.value) & 0x80) == 0, f"Failed! Expected DP led to stop after hundreds, got {bin(dut.uo_out.value)}"
    segments = int(dut.uo_out.value) & 0x7F
    units = SEG_TO_INT[int(segments)]

    # 6. RECONSTRUCT THE ANSWER
    
    hardware_answer = (hundreds * 100) + (tens * 10) + units

    # 7. EXIT THE MENU
    
    await chitter_press_enter(dut, debounce_limit)
    assert dut.uo_out.value == 0b01101101, f"Failed! Expected MENU_LED after a complete cycle, got {bin(dut.uo_out.value)}"
    
    # 8. Return the hardware_answer
    
    return hardware_answer


# ==========================================
# MAIN EXECUTION THREAD
# ==========================================

@cocotb.test()
async def strict_verification_suite(dut):
    dut._log.info("Starting ETH-Standard Automated Verification Suite...")

    # Boot the 50MHz Clock
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Run the Reset Sequence
    await apply_hardware_reset(dut)

    assert dut.uo_out.value == 0b01101101, f"Failed! Expected MENU_LED after reset, got {bin(dut.uo_out.value)}"

    #Test chitter resistance
    for i in range (5):
        dut.ui_in.value = int(dut.ui_in.value) | 0x80
        await ClockCycles(dut.clk, random.randint(2, 15))
        dut.ui_in.value = int(dut.ui_in.value) & 0x7F
        await ClockCycles(dut.clk, random.randint(2, 15))

    assert dut.uo_out.value == 0b01101101, f"Failed! Expected MENU_LED after chitter, got {bin(dut.uo_out.value)}"

    # Test Vectors
    gcd_vectors   = [(12, 8), (25, 10), (7, 3), (100, 0), (0, 17), (31, 97), (102, 81), (0, 0)]
    isqrt_vectors = [(16, 9), (50, 50), (4, 0), (100, 21), (0, 5), (100, 1), (11, 110), (0, 0)]
    lfsr_vectors  = [(1, 5), (0, 3), (15, 10), (0, 0), (4, 0), (103, 0), (0, 21), (73, 4)] 

    dut._log.info("=========================================")
    dut._log.info("BEGINNING APP 0: EUCLIDEAN GCD ENGINE")
    dut._log.info("=========================================")
    for a, b in gcd_vectors:
        dut._log.info(f"Testing GCD: A={a}, B={b}")
        
        # Call execute_app_lifecycle and get the hardware_answer

        hardware_answer = await execute_app_lifecycle(dut, 0b0000000, a, b, 100)
        expected = math.gcd(a, b)
        assert hardware_answer == expected, f"GCD Failed! Got {hardware_answer}, Expected {expected}"
        
        pass

    dut._log.info("=========================================")
    dut._log.info("BEGINNING APP 1: HARDWARE ISQRT ENGINE")
    dut._log.info("=========================================")
    for a, b in isqrt_vectors:
        dut._log.info(f"Testing ISQRT: A={a}, B={b}")
        
        # TASK 5: Call execute_app_lifecycle and get the hardware_answer

        hardware_answer = await execute_app_lifecycle(dut, 1, a, b, 100)
        expected = math.isqrt(a + b)
        assert hardware_answer == expected, f"ISQRT Failed! Got {hardware_answer}, Expected {expected}"
        
        pass

    dut._log.info("=========================================")
    dut._log.info("BEGINNING APP 2: CRYPTOGRAPHIC LFSR")
    dut._log.info("=========================================")
    for a, b in lfsr_vectors:
        dut._log.info(f"Testing LFSR: Seed={a}, Steps={b}")
        
        # TASK 6: Call execute_app_lifecycle and get the hardware_answer
        # Just print it out using dut._log.info() since we don't have a built-in math.lfsr function.
        
        hardware_answer = await execute_app_lifecycle(dut, 2, a, b, 100)
        dut._log.info(hardware_answer)
        
        pass

    dut._log.info("ALL VECTORS PASSED FSM NAVIGATION, CHITTER RESISTANCE, AND DISPLAY DECODING.")

    dut._log.info("=========================================")
    dut._log.info("EDGE CASE: ASYNCHRONOUS RESET DURING CALCULATION")
    dut._log.info("=========================================")
    
    # Start a GCD calculation
    dut.ui_in.value = 0 # Opcode 0
    await chitter_press_enter(dut, 100)
    dut.ui_in.value = 100 # Large A
    await chitter_press_enter(dut, 100)
    dut.ui_in.value = 3   # Prime B
    await chitter_press_enter(dut, 100)
    
    # Wait just 2 clock cycles, so the GCD engine is in the middle of dividing!
    await ClockCycles(dut.clk, 2)
    
    dut._log.info("USER HIT RESET MID-CALCULATION!")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    
    # Verify the OS immediately aborted and returned to the Menu
    assert dut.uo_out.value == 0b01101101, f"Failed! Chip did not recover to Menu after reset. Got {bin(dut.uo_out.value)}"

    # ==========================================
    # MANUAL EDGE CASE TESTING (PHYSICAL VULNERABILITIES)
    # ==========================================
    dut._log.info("=========================================")
    dut._log.info("COMMENCING PHYSICAL EDGE CASE DESTRUCTION TESTS")
    dut._log.info("=========================================")

    # -----------------------------------------------------------------
    # EDGE CASE 1: THE "FAT FINGER" (Asynchronous Data Change)
    # -----------------------------------------------------------------
    
    await apply_hardware_reset(dut)
    
    for test_num, wait_cycles in enumerate([99, 100, 101], 1):
        dut._log.info(f"Fat Finger Test {test_num}: Changing data at debounce cycle {wait_cycles}")
        
        # Go to MENU and select Opcode 0
        dut.ui_in.value = 0
        await ClockCycles(dut.clk, 1) # THE FIX: Let data propagate
        await chitter_press_enter(dut, 100)
        
        # We are in LOAD_A. Set data to 12.
        dut.ui_in.value = 12
        await ClockCycles(dut.clk, 1) # THE FIX: Let data propagate
        
        # Manually start the Enter press WITHOUT our helper function so we can interrupt it
        dut.ui_in.value = int(dut.ui_in.value) | 0x80 
        
        # Wait until the EXACT moment the debouncer is about to trigger
        await ClockCycles(dut.clk, wait_cycles)
        
        # FAT FINGER: Suddenly change the data to 25 while Enter is still HIGH!
        dut.ui_in.value = (25 | 0x80) 
        
        # Let the debouncer finish and the FSM transition
        await ClockCycles(dut.clk, 10)
        
        # Release Enter cleanly
        dut.ui_in.value = int(dut.ui_in.value) & 0x7F
        await ClockCycles(dut.clk, 150)
        
        # We are now in LOAD_B. Finish the math (B = 10)
        dut.ui_in.value = 10
        await ClockCycles(dut.clk, 1) # THE FIX: Let data propagate
        await chitter_press_enter(dut, 100)
        
        # Wait for calculation to finish and DP to light up
        while (int(dut.uo_out.value) & 0x80) == 0:
            await RisingEdge(dut.clk)
            
        # Read the Hundreds digit to see what latched!
        segments = int(dut.uo_out.value) & 0x7F
        latched_ans = SEG_TO_INT[int(segments)]
        
        dut._log.info(f"Resulting Hundreds Digit: {latched_ans}")
        
        # Exit DONE state
        await chitter_press_enter(dut, 100)

    # -----------------------------------------------------------------
    # EDGE CASE 2: THE "IMPATIENT HOLD"
    # -----------------------------------------------------------------
    dut._log.info("--- EDGE CASE 2: IMPATIENT HOLD ---")
    await apply_hardware_reset(dut)
    
    # Load Opcode 0, A=12, B=8 normally
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)
    await chitter_press_enter(dut, 100)
    
    dut.ui_in.value = 12
    await ClockCycles(dut.clk, 1)
    await chitter_press_enter(dut, 100)
    
    dut.ui_in.value = 8
    await ClockCycles(dut.clk, 1)
    
    # Press Enter for B, but NEVER RELEASE IT
    dut.ui_in.value = int(dut.ui_in.value) | 0x80
    await ClockCycles(dut.clk, 150) # Hold past debounce limit
    
    # Wait for the math to finish while STILL holding Enter
    await ClockCycles(dut.clk, 50)
    
    # Did the FSM safely stop at STATE_DONE, or did it skip straight back to Menu?
    assert (int(dut.uo_out.value) & 0x80) != 0, "FAILED! Impatient hold caused FSM to skip STATE_DONE."
    dut._log.info("Impatient Hold resisted! Chip safely stopped at STATE_DONE.")
    
    # Finally, release the switch and press it again to exit
    dut.ui_in.value = int(dut.ui_in.value) & 0x7F
    await ClockCycles(dut.clk, 150)
    await chitter_press_enter(dut, 100)

    # -----------------------------------------------------------------
    # EDGE CASE 3: THE "PREMATURE EXIT"
    # -----------------------------------------------------------------
    dut._log.info("--- EDGE CASE 3: PREMATURE EXIT ---")
    
    # Start a quick GCD
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)
    await chitter_press_enter(dut, 100)
    dut.ui_in.value = 25
    await ClockCycles(dut.clk, 1)
    await chitter_press_enter(dut, 100)
    dut.ui_in.value = 10
    await ClockCycles(dut.clk, 1)
    await chitter_press_enter(dut, 100)
    
    # Wait for the Hundreds digit (DP is high)
    while (int(dut.uo_out.value) & 0x80) == 0:
        await RisingEdge(dut.clk)
        
    dut._log.info("Hundreds digit showing. Interrupting timer NOW!")
    
    # IMMEDIATELY hit enter before the Tens or Units digit can show
    await chitter_press_enter(dut, 100)
    
    # Check if we correctly aborted back to Menu
    assert dut.uo_out.value == 0b01101101, f"FAILED! Did not cleanly return to Menu. Got {bin(dut.uo_out.value)}"
    
    # Critical Check: If we do a new math problem, does the display start correctly at Hundreds?
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 1)
    await chitter_press_enter(dut, 100)
    dut.ui_in.value = 12
    await ClockCycles(dut.clk, 1)
    await chitter_press_enter(dut, 100)
    dut.ui_in.value = 8
    await ClockCycles(dut.clk, 1)
    await chitter_press_enter(dut, 100)
    
    # If the multiplexer resets properly, the very first digit to show should have the DP on!
    await ClockCycles(dut.clk, 20)
    while (int(dut.uo_out.value) & 0x80) == 0:
        await RisingEdge(dut.clk)
        
    dut._log.info("Premature Exit safely handled! Multiplexer cleanly reset to Hundreds digit.")