from pyuvm import *
from sha256 import SHA256

class SHA256ScoreboardExport(uvm_analysis_export):
    """Custom analysis export that forwards to scoreboard"""
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.scoreboard = parent
    
    def write(self, txn):
        # Forward to scoreboard's write method
        self.scoreboard.write_transaction(txn)

class SHA256Scoreboard(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        
        # Create custom analysis export
        self.analysis_export = SHA256ScoreboardExport("analysis_export", self)
        
        # Counter for received transactions
        self.transaction_count = 0
        
        # Dictionary to store expected results for known test patterns
        self.setup_expected_results()
    
    def setup_expected_results(self):
        """Setup expected results for known test patterns"""
        self.expected_results = {}
        
        # For zero block (all zeros - 512 bits)
        zero_block = "61626380000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018"
        zero_hash = self.sha256_naked(zero_block)
        self.expected_results[0] = int(zero_hash, 16)
        self.logger.info(f"Expected result for zero block: 0x{zero_hash}")
        
        # Note: For more complex patterns, you would need to implement
        # the exact SHA256 padding and processing that your RTL uses
    
    def write_transaction(self, txn):
        """This method will be called by the analysis export"""
        self.transaction_count += 1
        
        self.logger.info(f"=== Scoreboard Transaction #{self.transaction_count} ===")
        self.logger.info(f"Received digest: 0x{txn.digest:064x}")
        self.logger.info(f"Ready: {txn.ready}, Valid: {txn.digest_valid}")
        
        # Basic validation - digest should not be zero (unless it's the zero block result)
        if txn.digest == 0:
            self.logger.error("Received zero digest - this might indicate an error")
        else:
            self.logger.info("✓ Non-zero digest received")
        
        # Check digest_valid should be 1
        if txn.digest_valid != 1:
            self.logger.error(f"Expected digest_valid=1, got {txn.digest_valid}")
        else:
            self.logger.info("✓ digest_valid is correctly asserted")
        
        # For the zero block case, we can check against expected result
        if hasattr(txn, 'block') and txn.block == 0:
            expected = self.expected_results.get(0)
            if expected and txn.digest == expected:
                self.logger.info("✓ Zero block digest matches expected result")
            elif expected:
                self.logger.error(f"✗ Zero block digest mismatch!")
                self.logger.error(f"  Expected: 0x{expected:064x}")
                self.logger.error(f"  Actual:   0x{txn.digest:064x}")
        
        # Log statistics
        self.logger.info(f"Total transactions processed: {self.transaction_count}")
        self.logger.info("=" * 50)
    
    def sha256_naked(self, block:str) -> str:
        #Convert to list type (int)
        TC_block = [0] * 16
        for i in range(len(TC_block)):
            chunk = block[8*i: 8*i+8]
            TC_block[i] = int(chunk,16)
            
        my_sha256 = SHA256(verbose=0)
        my_sha256.init()
        my_sha256.next(TC_block)
        my_digest = my_sha256.get_digest()
        
        
        #Return back to byte
        reconstructed_bytes = b''.join(x.to_bytes(4, byteorder='big') for x in my_digest)
        return reconstructed_bytes.hex()