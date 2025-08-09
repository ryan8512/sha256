# sha256_driver.py - Corrected version with proper signal names
from pyuvm import *
import cocotb 
from cocotb.triggers import RisingEdge, FallingEdge, Timer

# Import the global DUT handle
try:
    import fixed_testbench as testbench
except ImportError:
    try:
        import testbench
    except ImportError:
        testbench = None

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
            await self.drive_transaction(txn)
            
            self.seq_item_port.item_done()
        self.drop_objection()
        
    async def drive_transaction(self, txn):
        try:
            self.logger.info("Starting drive_transaction")
            
            # Wait for a clean clock edge
            await RisingEdge(self.dut.clk)
            self.logger.info("Got rising edge of clock")
            
            # Apply inputs carefully with error checking
            self.dut.init.value = txn.init
            self.logger.info(f"Set init = {txn.init}")
            
            self.dut.next.value = txn.next
            self.logger.info(f"Set next = {txn.next}")
            
            self.dut.mode.value = txn.mode
            self.logger.info(f"Set mode = {txn.mode}")
            
            # Handle 512-bit block value properly
            if hasattr(txn, 'block') and txn.block is not None:
                self.dut.block.value = txn.block
                self.logger.info(f"Set block = 0x{txn.block:0128x}")
            
            # Wait one clock cycle for inputs to be registered
            await RisingEdge(self.dut.clk)
            self.logger.info("Got second rising edge of clock")
            
            # Deassert control signals (init/next should be pulses)
            self.dut.init.value = 0
            self.dut.next.value = 0
            self.logger.info("Deasserted init and next signals")
            
            # Wait until DUT is ready or timeout
            timeout_count = 0
            max_timeout = 1000  # Increased timeout for SHA256 processing
            
            # Wait for operation to start (ready might go low first)
            await RisingEdge(self.dut.clk)
            
            while self.dut.ready.value == 0 and timeout_count < max_timeout:
                await RisingEdge(self.dut.clk)
                timeout_count += 1
                
                # Log progress every 50 cycles
                if timeout_count % 50 == 0:
                    self.logger.info(f"Waiting for ready... cycle {timeout_count}")
                
            if timeout_count >= max_timeout:
                self.logger.error(f"Timeout waiting for ready signal (waited {timeout_count} cycles)")
            else:
                self.logger.info(f"DUT became ready after {timeout_count} cycles")
                
        except Exception as e:
            self.logger.error(f"Error in drive_transaction: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise