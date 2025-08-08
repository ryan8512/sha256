# sha256_monitor.py - Updated to use global DUT
from pyuvm import *
import cocotb
from cocotb.triggers import RisingEdge
from sha256_transaction import SHA256Transaction

# Import the global DUT handle
import testbench

class SHA256Monitor(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dut = None
        self.analysis_port = uvm_analysis_port("analysis_port", self)

    def build_phase(self):
        super().build_phase()
        # Get DUT from global variable (most reliable)
        if testbench.dut_handle is not None:
            self.dut = testbench.dut_handle
            self.logger.info("DUT retrieved from global handle")
        else:
            # Fallback: try ConfigDB
            try:
                self.dut = ConfigDB().get(None, "*", "DUT")
                self.logger.info("DUT retrieved from config_db")
            except:
                # Last resort: direct cocotb access
                self.dut = cocotb.top
                self.logger.info("DUT set from cocotb.top directly")
        
        if self.dut is None:
            self.logger.fatal("Failed to get DUT - no DUT available")
    
    async def run_phase(self):
        self.raise_objection()
        while True:
            await RisingEdge(self.dut.clk)
            
            if self.dut.digest_valid.value:
                txn = SHA256Transaction()
                txn.digest = int(self.dut.digest.value)
                txn.digest_valid = int(self.dut.digest_valid.value)
                txn.ready = int(self.dut.ready.value)
                
                self.logger.info(f"Observed digest: 0x{txn.digest:064x}")
                self.analysis_port.write(txn)
        self.drop_objection()