import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock

@cocotb.test()
async def sha256_core_test(dut):
    """Simple test for SHA256 core with correct signal names"""
    
    print("Starting SHA256 Core Test")
    print("=" * 50)
    
    # Start clock (10ns period = 100MHz)
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset sequence (reset_n is active low)
    print("Applying reset...")
    dut.reset_n.value = 0  # Assert reset
    await Timer(50, "ns")  # Hold reset for 50ns
    dut.reset_n.value = 1  # Deassert reset
    await Timer(20, "ns")  # Wait after reset
    print("Reset complete")
    
    # Initialize all inputs to safe values
    dut.init.value = 0
    dut.next.value = 0
    dut.mode.value = 0
    dut.block.value = 0
    
    await RisingEdge(dut.clk)
    
    # Check initial state
    print(f"Initial ready: {dut.ready.value}")
    print(f"Initial digest_valid: {dut.digest_valid.value}")
    
    # Test 1: Simple initialization
    print("\n--- Test 1: Initialize SHA256 ---")
    
    # Set up a simple test block (all zeros for now)
    test_block = 0
    dut.block.value = test_block
    dut.mode.value = 0  # Assuming 0 = SHA-256 mode
    
    # Apply init pulse
    await RisingEdge(dut.clk)
    dut.init.value = 1
    await RisingEdge(dut.clk)
    dut.init.value = 0
    
    print("Init pulse applied")
    
    # Wait for processing and monitor signals
    max_wait_cycles = 100
    cycle_count = 0
    
    while cycle_count < max_wait_cycles:
        await RisingEdge(dut.clk)
        cycle_count += 1
        
        ready = int(dut.ready.value)
        digest_valid = int(dut.digest_valid.value)
        
        if cycle_count % 10 == 0 or digest_valid:
            print(f"Cycle {cycle_count}: ready={ready}, digest_valid={digest_valid}")
        
        if digest_valid:
            digest_value = int(dut.digest.value)
            print(f"Got digest: 0x{digest_value:064x}")
            break
    
    if cycle_count >= max_wait_cycles:
        print("WARNING: Timeout waiting for digest_valid")
    
    # Test 2: Test with known test vector
    print("\n--- Test 2: Known Test Vector ---")
    
    # Wait for ready
    while not dut.ready.value:
        await RisingEdge(dut.clk)
    
    # Use a simple known test case: empty message (just padding)
    # For SHA256, empty string should hash to:
    # e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    
    # SHA256 padding for empty message (512 bits):
    # 0x8000...000 followed by length (0) in last 64 bits
    empty_message_block = 0x8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
    
    dut.block.value = empty_message_block
    dut.mode.value = 0
    
    # Apply init pulse
    await RisingEdge(dut.clk)
    dut.init.value = 1
    await RisingEdge(dut.clk)
    dut.init.value = 0
    
    print("Applied empty message test vector")
    
    # Wait for result
    cycle_count = 0
    while cycle_count < max_wait_cycles:
        await RisingEdge(dut.clk)
        cycle_count += 1
        
        if dut.digest_valid.value:
            digest_value = int(dut.digest.value)
            expected = 0xe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
            
            print(f"Digest:   0x{digest_value:064x}")
            print(f"Expected: 0x{expected:064x}")
            
            if digest_value == expected:
                print("✓ PASS: Digest matches expected value!")
            else:
                print("✗ FAIL: Digest does not match expected value")
            break
    
    # Test 3: Multi-block operation
    print("\n--- Test 3: Next Block Operation ---")
    
    # Wait for ready
    timeout = 0
    while not dut.ready.value and timeout < 20:
        await RisingEdge(dut.clk)
        timeout += 1
    
    if dut.ready.value:
        # Try next operation
        dut.block.value = 0x123456789abcdef0fedcba9876543210  # Different block
        
        await RisingEdge(dut.clk)
        dut.next.value = 1
        await RisingEdge(dut.clk)
        dut.next.value = 0
        
        print("Applied next block operation")
        
        # Monitor for a few cycles
        for i in range(10):
            await RisingEdge(dut.clk)
            if dut.digest_valid.value:
                digest_value = int(dut.digest.value)
                print(f"Next block digest: 0x{digest_value:064x}")
                break
    
    print("\n" + "=" * 50)
    print("SHA256 Core Test Complete")

@cocotb.test()
async def quick_signal_test(dut):
    """Quick test to verify all signals are accessible"""
    
    print("Quick Signal Accessibility Test")
    print("-" * 40)
    
    # Test all expected signals
    signals_to_test = {
        'clk': 'input',
        'reset_n': 'input', 
        'init': 'input',
        'next': 'input',
        'mode': 'input',
        'block': 'input',
        'ready': 'output',
        'digest': 'output',
        'digest_valid': 'output'
    }
    
    for signal_name, signal_type in signals_to_test.items():
        try:
            signal = getattr(dut, signal_name)
            # Try to read the signal
            value = signal.value
            print(f"✓ {signal_name:12} ({signal_type:6}): accessible, value = {value}")
            
            # If it's an input, try to write to it
            if signal_type == 'input':
                original_value = value
                signal.value = 1
                new_value = signal.value
                signal.value = original_value  # Restore
                print(f"    └─ Write test: {original_value} -> {new_value} -> {original_value}")
                
        except AttributeError:
            print(f"✗ {signal_name:12} ({signal_type:6}): NOT FOUND")
        except Exception as e:
            print(f"✗ {signal_name:12} ({signal_type:6}): ERROR - {e}")
    
    print("-" * 40)
    print("Signal test complete")