import cocotb
from cocotb.triggers import Timer
from pyuvm import *
from sha256_test import SHA256Test

# Global DUT reference - simple and reliable
dut_handle = None

@cocotb.test()
async def sha256_uvm_test(dut):
    """Main cocotb test function"""
    
    # Store DUT globally so components can access it
    global dut_handle
    dut_handle = dut
    
    # Also set it in ConfigDB as backup
    try:
        ConfigDB().set(None, "*", "DUT", dut)
        ConfigDB().set(None, "uvm_test_top.*", "DUT", dut)
    except:
        pass  # ConfigDB might not work, but we have global fallback
    
    # Run the UVM test
    await uvm_root().run_test("SHA256Test")