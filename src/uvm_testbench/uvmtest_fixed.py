import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock
from pyuvm import *
from sha256_env import SHA256Env
from sha256_transaction import SHA256Transaction

# Global DUT reference - simple and reliable
dut_handle = None

class SHA256SimpleSequence(uvm_sequence):
    async def body(self):
        # Wait a bit before starting to let everything settle
        await Timer(100, "ns")
        
        for i in range(3):
            txn = SHA256Transaction()
            txn.init = 1 if i == 0 else 0
            txn.next = 0 if i == 0 else 1
            txn.mode = 0
            
            # Create safe 512-bit block values
            if i == 0:
                txn.block = 0  # First test with zero block
            elif i == 1:
                # Create a simple repeating pattern that's exactly 512 bits
                pattern = 0x123456789abcdef0
                txn.block = 0
                for j in range(8):  # 8 * 64 bits = 512 bits
                    txn.block = (txn.block << 64) | pattern
            else:
                # Create alternating pattern
                pattern1 = 0xaaaaaaaaaaaaaaaa
                pattern2 = 0x5555555555555555
                txn.block = 0
                for j in range(4):  # 4 * 128 bits = 512 bits
                    txn.block = (txn.block << 64) | pattern1
                    txn.block = (txn.block << 64) | pattern2
            
            # Double-check block size
            if txn.block.bit_length() > 512:
                self.logger.warning(f"Block too large ({txn.block.bit_length()} bits), truncating")
                txn.block = txn.block & ((1 << 512) - 1)
            
            #self.logger.info(f"Sending transaction {i}: init={txn.init}, next={txn.next}")
            #self.logger.info(f"  Block bits: {txn.block.bit_length()}")
            
            await self.start_item(txn)
            await self.finish_item(txn)
            
            # Wait between transactions to allow processing
            await Timer(3000, "ns")  # 3us between transactions

class SHA256Test(uvm_test):
    def __init__(self, name, parent):
        super().__init__(name, parent)
    
    def build_phase(self):
        self.env = SHA256Env("env", self)
    
    async def run_phase(self):
        self.raise_objection()
        
        # Wait for reset to complete and system to stabilize
        await Timer(200, "ns")
        
        self.logger.info("=== Starting SHA256 UVM Test ===")
        
        seq = SHA256SimpleSequence("simple_seq")
        await seq.start(self.env.agent.sequencer)
        
        # Wait a bit more to let final transactions complete
        await Timer(10000, "ns")  # 10us final wait
        
        self.logger.info("=== SHA256 UVM Test Complete ===")
        
        self.drop_objection()

@cocotb.test()
async def sha256_uvm_test(dut):
    """Main cocotb test function with proper clock and reset"""
    
    # Store DUT globally so components can access it
    global dut_handle
    dut_handle = dut
    
    print("Starting UVM test with clock and reset...")
    
    # Start the clock first
    clock = Clock(dut.clk, 10, units="ns")  # 10ns period = 100MHz
    cocotb.start_soon(clock.start())
    
    # Apply reset sequence
    print("Applying reset...")
    dut.reset_n.value = 0  # Assert reset
    await Timer(100, "ns")  # Hold reset longer
    dut.reset_n.value = 1  # Deassert reset
    await Timer(50, "ns")   # Wait after reset
    
    # Initialize inputs
    dut.init.value = 0
    dut.next.value = 0
    dut.mode.value = 0
    dut.block.value = 0
    
    # Wait for a few clock cycles
    for _ in range(5):
        await RisingEdge(dut.clk)
    
    print("System initialized, starting UVM...")
    
    # Set in ConfigDB as backup
    try:
        ConfigDB().set(None, "*", "DUT", dut)
        ConfigDB().set(None, "uvm_test_top.*", "DUT", dut)
    except:
        pass
    
    # Run the UVM test
    await uvm_root().run_test("SHA256Test")