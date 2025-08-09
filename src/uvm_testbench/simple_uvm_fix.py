import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock
from pyuvm import *
from sha256_test import SHA256Test

# Global DUT reference - simple and reliable
dut_handle = None

@cocotb.test()
async def sha256_uvm_test(dut):
    """Main cocotb test function with proper clock and reset"""
    
    # Store DUT globally so components can access it
    global dut_handle
    dut_handle = dut
    
    print("Starting UVM test with clock and reset...")
    
    # Start the clock first - this was the main missing piece!
    clock = Clock(dut.clk, 10, units="ns")  # 10ns period = 100MHz
    cocotb.start_soon(clock.start())
    
    # Apply reset sequence
    print("Applying reset...")
    dut.reset_n.value = 0  # Assert reset
    await Timer(100, "ns")  # Hold reset 
    dut.reset_n.value = 1  # Deassert reset
    await Timer(50, "ns")   # Wait after reset
    
    # Initialize inputs to known state
    dut.init.value = 0
    dut.next.value = 0
    dut.mode.value = 0
    dut.block.value = 0
    
    # Wait for a few clock cycles to let system stabilize
    for i in range(10):
        await RisingEdge(dut.clk)
    
    print(f"System ready: ready={dut.ready.value}")
    
    # Set in ConfigDB 
    try:
        ConfigDB().set(None, "*", "DUT", dut)
        ConfigDB().set(None, "uvm_test_top.*", "DUT", dut)
    except:
        pass
    
    print("Starting UVM framework...")
    
    # Run the UVM test
    await uvm_root().run_test("SHA256Test")