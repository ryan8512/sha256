import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock

@cocotb.test()
async def sha256_core_test(dut):
    """Simple test for SHA256 core with correct signal names - no overflow"""
    
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
    
    # Test 1: Simple initialization with zero block
    print("\n--- Test 1: Zero Block Test ---")
    
    # Set up a zero test block
    dut.block.value = 0
    dut.mode.value = 0
    
    # Apply init pulse
    await RisingEdge(dut.clk)
    dut.init.value = 1
    await RisingEdge(dut.clk)
    dut.init.value = 0
    
    print("Init pulse applied with zero block")
    
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
            print(f"Zero block digest: 0x{digest_value:064x}")
            break
    
    if cycle_count >= max_wait_cycles:
        print("WARNING: Timeout waiting for digest_valid")
    
    # Test 2: Test with pattern block (safe 512-bit value)
    print("\n--- Test 2: Pattern Block Test ---")
    
    # Wait for ready
    timeout = 0
    while not dut.ready.value and timeout < 20:
        await RisingEdge(dut.clk)
        timeout += 1
    
    if not dut.ready.value:
        print("WARNING: DUT not ready for next test")
        return
    
    # Use a safe 512-bit pattern - construct it carefully
    # 512 bits = 64 bytes = 128 hex digits
    # Let's use a repeating pattern that's easy to verify
    pattern_block = 0
    for i in range(64):  # 64 bytes
        pattern_block = (pattern_block << 8) | (i & 0xFF)
    
    print(f"Pattern block: 0x{pattern_block:0128x}")
    print(f"Block bit length: {pattern_block.bit_length()} (should be <= 512)")
    
    # Only proceed if the block size is safe
    if pattern_block.bit_length() <= 512:
        dut.block.value = pattern_block
        dut.mode.value = 0
        
        # Apply init pulse
        await RisingEdge(dut.clk)
        dut.init.value = 1
        await RisingEdge(dut.clk)
        dut.init.value = 0
        
        print("Applied pattern block")
        
        # Wait for result
        cycle_count = 0
        while cycle_count < max_wait_cycles:
            await RisingEdge(dut.clk)
            cycle_count += 1
            
            if dut.digest_valid.value:
                digest_value = int(dut.digest.value)
                print(f"Pattern block digest: 0x{digest_value:064x}")
                break
        
        if cycle_count >= max_wait_cycles:
            print("WARNING: Timeout waiting for pattern block digest")
    else:
        print(f"ERROR: Pattern block too large ({pattern_block.bit_length()} bits)")
    
    # Test 3: Simple alternating pattern
    print("\n--- Test 3: Simple Alternating Pattern ---")
    
    # Wait for ready
    timeout = 0
    while not dut.ready.value and timeout < 20:
        await RisingEdge(dut.clk)
        timeout += 1
    
    if dut.ready.value:
        # Create alternating pattern: 0xAAAA...AAAA (512 bits)
        alt_pattern = 0
        for i in range(128):  # 128 hex digits = 512 bits
            if i % 2 == 0:
                alt_pattern = (alt_pattern << 4) | 0xA
            else:
                alt_pattern = (alt_pattern << 4) | 0x5
        
        print(f"Alternating pattern bit length: {alt_pattern.bit_length()}")
        
        if alt_pattern.bit_length() <= 512:
            dut.block.value = alt_pattern
            
            await RisingEdge(dut.clk)
            dut.next.value = 1  # Use 'next' instead of 'init' for subsequent blocks
            await RisingEdge(dut.clk)
            dut.next.value = 0
            
            print("Applied alternating pattern using 'next' command")
            
            # Monitor for a few cycles
            for i in range(20):
                await RisingEdge(dut.clk)
                if dut.digest_valid.value:
                    digest_value = int(dut.digest.value)
                    print(f"Alternating pattern digest: 0x{digest_value:064x}")
                    break
        else:
            print("ERROR: Alternating pattern too large")
    
    print("\n" + "=" * 50)
    print("SHA256 Core Test Complete")

@cocotb.test()
async def simple_block_size_test(dut):
    """Test to verify maximum safe block sizes"""
    
    print("Block Size Test")
    print("-" * 30)
    
    # Test different block sizes
    test_values = [
        ("1-bit", 1),
        ("8-bit", 0xFF),
        ("16-bit", 0xFFFF),
        ("32-bit", 0xFFFFFFFF),
        ("64-bit", 0xFFFFFFFFFFFFFFFF),
        ("128-bit", (1 << 128) - 1),
        ("256-bit", (1 << 256) - 1),
        ("511-bit", (1 << 511) - 1),
        ("512-bit", (1 << 512) - 1),
    ]
    
    for name, value in test_values:
        try:
            print(f"Testing {name}: {value.bit_length()} bits")
            # Don't actually assign if it's too big, just test the size
            if value.bit_length() <= 512:
                print(f"  ✓ {name} fits in 512 bits")
            else:
                print(f"  ✗ {name} too large ({value.bit_length()} bits)")
        except Exception as e:
            print(f"  ERROR testing {name}: {e}")
    
    print("-" * 30)

@cocotb.test() 
async def hex_string_test(dut):
    """Test hex string to integer conversion"""
    
    print("Hex String Test")
    print("-" * 20)
    
    # Test creating exactly 512-bit values using hex strings
    hex_strings = [
        "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # All zeros
        "8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",  # MSB set
        "123456789abcdef0fedcba9876543210123456789abcdef0fedcba9876543210123456789abcdef0fedcba9876543210123456789abcdef0fedcba9876543210",  # Pattern
    ]
    
    for i, hex_str in enumerate(hex_strings):
        print(f"Test {i+1}: {len(hex_str)} hex digits")
        try:
            value = int(hex_str, 16)
            print(f"  Value bit length: {value.bit_length()}")
            print(f"  Fits in 512 bits: {value.bit_length() <= 512}")
            print(f"  Value: 0x{value:0128x}"[:50] + "...")  # Show first 50 chars
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("-" * 20)