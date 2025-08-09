# sha256_monitor.py - Corrected with proper signal names
from pyuvm import *
import cocotb
from cocotb.triggers import RisingEdge
from sha256_transaction import SHA256Transaction

# Import the global DUT handle
try:
    import fixed_testbench as testbench
except ImportError:
    try:
        import testbench
    except ImportError:
        testbench = None

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
            
            # Verify we have the expected signals
            required_signals = ['clk', 'digest_valid', 'digest', 'ready']
            missing_signals = []
            
            for sig in required_signals:
                if not hasattr(self.dut, sig):
                    missing_signals.append(sig)
            
            if missing_signals:
                self.logger.error(f"Missing required signals: {missing_signals}")
            else:
                self.logger.info("All required signals found")
                
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
        
        try:
            while True:
                await RisingEdge(self.dut.clk)
                
                # Check for valid digest output
                if int(self.dut.digest_valid.value) == 1:
                    # Create transaction to capture the result
                    txn = SHA256Transaction()
                    txn.digest = int(self.dut.digest.value)
                    txn.digest_valid = int(self.dut.digest_valid.value)
                    txn.ready = int(self.dut.ready.value)
                    
                    self.logger.info(f"Observed digest_valid=1, digest=0x{txn.digest:064x}")
                    self.analysis_port.write(txn)
                
                # Also monitor ready signal transitions for debugging
                if hasattr(self, '_prev_ready'):
                    current_ready = int(self.dut.ready.value)
                    if current_ready != self._prev_ready:
                        self.logger.info(f"Ready signal changed: {self._prev_ready} -> {current_ready}")
                        self._prev_ready = current_ready
                else:
                    self._prev_ready = int(self.dut.ready.value)
                    self.logger.info(f"Initial ready state: {self._prev_ready}")
        
        except Exception as e:
            self.logger.error(f"Error in monitor run_phase: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
        finally:
            self.drop_objection()