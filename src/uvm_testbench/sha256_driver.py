# sha256_driver.py - Updated to use global DUT
from pyuvm import *
import cocotb 
from cocotb.triggers import RisingEdge, FallingEdge, Timer

# Import the global DUT handle
import testbench

class SHA256Driver(uvm_driver):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dut = None

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
            txn = await self.seq_item_port.get_next_item()
            
            self.logger.info(f"Driving transaction: {txn}")
            await self.drive_transaction(txn)
            
            self.seq_item_port.item_done()
        self.drop_objection()
        
    async def drive_transaction(self, txn):
        await RisingEdge(self.dut.clk)
        
        # Apply Inputs
        self.dut.init.value = txn.init
        self.dut.next.value = txn.next
        self.dut.mode.value = txn.mode
        self.dut.block.value = txn.block
        
        await RisingEdge(self.dut.clk)
        
        # Deassert init/next
        self.dut.init.value = 0
        self.dut.next.value = 0
        
        # Wait until DUT is ready
        while self.dut.ready.value == 0:
            await RisingEdge(self.dut.clk)