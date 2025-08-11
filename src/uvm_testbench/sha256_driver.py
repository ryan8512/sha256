# sha256_driver.py - Fixed version with proper sequencing
from pyuvm import *
import cocotb 
from cocotb.triggers import RisingEdge, FallingEdge, Timer

# Import the global DUT handle
try:
    import uvmtest_fixed as testbench
except ImportError:
        testbench = None

class SHA256Driver(uvm_driver):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dut = None
        self.input_ap = uvm_analysis_port("input_ap", self)  # analysis port for inputs

    def build_phase(self):
        super().build_phase()
        # Get DUT from global variable (most reliable)
        if testbench.dut_handle is not None:
            self.dut = testbench.dut_handle
            self.logger.info("DUT retrieved from global handle")
            
            # Debug: Print all available signals
            self.logger.info(f"DUT type: {type(self.dut)}")
            available_signals = [attr for attr in dir(self.dut) if not attr.startswith('_')]
            self.logger.info(f"Available DUT signals: {available_signals}")
            
            # Check for expected signals
            expected_signals = ['clk', 'reset_n', 'init', 'next', 'mode', 'block', 'ready', 'digest', 'digest_valid']
            for sig in expected_signals:
                if hasattr(self.dut, sig):
                    self.logger.info(f"✓ Signal '{sig}' found")
                else:
                    self.logger.warning(f"✗ Signal '{sig}' NOT found")
            
        else:
            self.logger.fatal("Failed to get DUT - no DUT available")
    
    async def run_phase(self):
        self.raise_objection()
        
        # Wait a bit before starting
        await Timer(10, "ns")
        
        # Initialize all inputs to safe values
        self.dut.init.value = 0
        self.dut.next.value = 0
        self.dut.mode.value = 0
        self.dut.block.value = 0
        
        await RisingEdge(self.dut.clk)
        
        while True:
            txn = await self.seq_item_port.get_next_item()
            
            self.logger.info(f"Driving transaction: {txn}")

            # Forward input transaction to scoreboard via analysis port
            self.input_ap.write(txn)

            await self.drive_transaction(txn)
            
            self.seq_item_port.item_done()
        self.drop_objection()
        
    async def drive_transaction(self, txn):
        try:
            self.logger.info("Starting drive_transaction")
            
            # Wait for DUT to be ready before starting
            timeout_count = 0
            max_timeout = 100
            
            while int(self.dut.ready.value) == 0 and timeout_count < max_timeout:
                await RisingEdge(self.dut.clk)
                timeout_count += 1
            
            if timeout_count >= max_timeout:
                self.logger.error("Timeout waiting for DUT ready before transaction")
                return
            
            self.logger.info(f"DUT ready, proceeding with transaction after {timeout_count} cycles")
            
            # Wait for a clean clock edge
            await RisingEdge(self.dut.clk)
            
            # Apply inputs
            self.dut.mode.value = txn.mode
            self.dut.block.value = txn.block
            self.logger.info(f"Set mode={txn.mode}, block=0x{txn.block:0128x}")
            
            # Apply control signals
            if txn.init:
                self.dut.init.value = 1
                self.logger.info("Applied init pulse")
            elif txn.next:
                self.dut.next.value = 1
                self.logger.info("Applied next pulse")
            
            # Wait one clock cycle for inputs to be registered
            await RisingEdge(self.dut.clk)
            
            # Deassert control signals (should be pulses)
            self.dut.init.value = 0
            self.dut.next.value = 0
            self.logger.info("Deasserted control signals")
            
            # Now wait for the operation to complete
            # The operation is complete when digest_valid goes high
            timeout_count = 0
            max_timeout = 1000
            
            self.logger.info("Waiting for digest_valid to go high...")
            
            while int(self.dut.digest_valid.value) == 0 and timeout_count < max_timeout:
                await RisingEdge(self.dut.clk)
                timeout_count += 1
                
                # Log progress periodically
                if timeout_count % 100 == 0:
                    ready_val = int(self.dut.ready.value)
                    self.logger.info(f"Waiting for digest_valid... cycle {timeout_count}, ready={ready_val}")
            
            if timeout_count >= max_timeout:
                self.logger.error(f"Timeout waiting for digest_valid (waited {timeout_count} cycles)")
            else:
                digest_val = int(self.dut.digest.value)
                ready_val = int(self.dut.ready.value)
                self.logger.info(f"Operation completed after {timeout_count} cycles")
                self.logger.info(f"Final state: ready={ready_val}, digest=0x{digest_val:064x}")
                
                # Wait one more cycle to let the monitor capture the result
                await RisingEdge(self.dut.clk)
                
                # Wait for digest_valid to go low (end of operation)
                timeout_count = 0
                while int(self.dut.digest_valid.value) == 1 and timeout_count < 100:
                    await RisingEdge(self.dut.clk)
                    timeout_count += 1
                
                self.logger.info(f"digest_valid deasserted after {timeout_count} additional cycles")
                
        except Exception as e:
            self.logger.error(f"Error in drive_transaction: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise