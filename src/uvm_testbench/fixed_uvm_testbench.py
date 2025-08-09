import cocotb
from cocotb.triggers import Timer
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
    
    # Start the clock first (this was missing!)
    clock = Clock(dut.clk, 10, units="ns")  # 10ns period = 100MHz
    cocotb.start_soon(clock.start())
    
    # Apply reset sequence
    dut.reset_n.value = 0  # Assert reset
    await Timer(50, "ns")
    dut.reset_n.value = 1  # Deassert reset
    await Timer(20, "ns")
    
    # Initialize inputs
    dut.init.value = 0
    dut.next.value = 0
    dut.mode.value = 0
    dut.block.value = 0
    
    # Also set it in ConfigDB as backup
    try:
        ConfigDB().set(None, "*", "DUT", dut)
        ConfigDB().set(None, "uvm_test_top.*", "DUT", dut)
    except:
        pass  # ConfigDB might not work, but we have global fallback
    
    # Run the UVM test
    await uvm_root().run_test("SHA256Test")