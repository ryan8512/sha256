from pyuvm import *

class SHA256Scoreboard(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        
        # Export receives transactions from monitor
        self.analysis_export = uvm_analysis_imp(self.write_transaction, "analysis_export", self)
        
        # Dictionary to map block -> expected digest
        self.expected_outputs = {}
        
    
    def write_transaction(self, txn):
        self.logger.info(f"Scoreboard received digest: 0x{txn.digest:064x}")
        
        #Find Expected digest based on something
        expected_digest = self.expected_outputs.get(txn.block, None)
        
        if expected_digest is None:
            self.logger.warning("No expected digest found for this block")
        else:
            if txn.digest != expected_digest:
                self.logger.error(f"Digest mismatch!\nExpected: 0x{expected_digest: 064x}\nActual: 0x{txn.digest: 064x}")
            else:
                self.logger.info("Digest matches expected")