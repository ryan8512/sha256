import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock
from pyuvm import uvm_root
from sha256_configdb import configdb
from sha256_test import SHA256Test

@cocotb.test()
async def sha256_uvm_test(dut):
    """Main cocotb test function with proper clock and reset"""
    
    print("=" * 60)
    print("Starting SHA256 UVM Test")
    print("=" * 60)
    
    # Start the clock first
    clock = Clock(dut.clk, 10, units="ns")  # 10ns period = 100MHz
    cocotb.start_soon(clock.start())
    
    # Apply reset sequence
    print("Applying reset...")
    dut.reset_n.value = 0  # Assert reset
    await Timer(200, "ns")  # Hold reset longer
    dut.reset_n.value = 1  # Deassert reset
    await Timer(100, "ns")   # Wait after reset
    
    # Initialize inputs to known safe values
    dut.init.value = 0
    dut.next.value = 0
    dut.mode.value = 0
    dut.block.value = 0
    
    # Wait for a few clock cycles to stabilize
    for i in range(10):
        await RisingEdge(dut.clk)
    
    # Check initial state
    print(f"Initial state after reset:")
    print(f"  ready = {dut.ready.value}")
    print(f"  digest_valid = {dut.digest_valid.value}")
    print(f"  digest = 0x{int(dut.digest.value):064x}")
    
    print("System initialized, starting UVM...")
    
    # Set in ConfigDB as backup
    try:
        configdb.set(None, "*", "DUT", dut)
        print("DUT saved to ConfigDB")
    except:
        print("It didn't save correctly to ConfigDB")
    
    # Run the UVM test
    await uvm_root().run_test("SHA256Test")
    
    print("=" * 60)
    print("SHA256 UVM Test Completed")
    print("=" * 60)