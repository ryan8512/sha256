import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock

@cocotb.test()
async def simple_rtl_test(dut):
    """Simple test to check RTL interface"""
    
    # Start clock
    clock = Clock(dut.clk, 10, units="ns")  # 10ns period = 100MHz
    cocotb.start_soon(clock.start())
    
    # Reset DUT (using correct signal name: reset_n, active low)
    dut.reset_n.value = 0  # Assert reset (active low)
    await Timer(20, "ns")
    dut.reset_n.value = 1  # Deassert reset (active low)
    await Timer(20, "ns")
    
    # Print available signals
    print(f"DUT type: {type(dut)}")
    print(f"Available signals: {[attr for attr in dir(dut) if not attr.startswith('_')]}")
    
    # Try to access basic signals with correct names
    try:
        print(f"clk exists: {hasattr(dut, 'clk')}")
        print(f"reset_n exists: {hasattr(dut, 'reset_n')}")  # Changed from rst
        print(f"init exists: {hasattr(dut, 'init')}")
        print(f"next exists: {hasattr(dut, 'next')}")
        print(f"ready exists: {hasattr(dut, 'ready')}")
        print(f"block exists: {hasattr(dut, 'block')}")
        print(f"digest exists: {hasattr(dut, 'digest')}")
        print(f"digest_valid exists: {hasattr(dut, 'digest_valid')}")  # Added this
        print(f"mode exists: {hasattr(dut, 'mode')}")  # Added this
        
    except Exception as e:
        print(f"Error checking signals: {e}")
    
    # Simple stimulus
    await RisingEdge(dut.clk)
    
    # Try setting some signals
    try:
        dut.init.value = 1
        dut.next.value = 0
        dut.mode.value = 1
        dut.block.value = 0x61626380000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018  # 512-bit value
        print("Successfully set input signals")
        
        await RisingEdge(dut.clk)
        
        dut.init.value = 0
        dut.next.value = 0
        print("Successfully cleared control signals")
        
    except Exception as e:
        print(f"Error setting signals: {e}")
        raise
    
    # Wait a few cycles and monitor outputs
    for i in range(70):
        await RisingEdge(dut.clk)
        try:
            ready_val = dut.ready.value
            digest_valid_val = dut.digest_valid.value
            print(f"Cycle {i}: ready = {ready_val}, digest_valid = {digest_valid_val}")
            
            if digest_valid_val:
                digest_val = dut.digest.value
                print(f"  Digest: 0x{int(digest_val):064x}")
        except Exception as e:
            print(f"Cycle {i}: could not read output signals - {e}")
    
    print("Simple RTL test completed successfully!")