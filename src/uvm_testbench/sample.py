from sha256 import SHA256

def sha256_naked(block:bytes) -> str:
    #Convert to list type (int)
    TC_block = [0] * 16
    for i in range(len(TC_block)):
        chunk = block[4*i: 4*i+4]
        TC_block[i] = int.from_bytes(chunk, byteorder='big')  # or 'little' depending on endianness
        
    my_sha256 = SHA256(verbose=0)
    my_sha256.init()
    my_sha256.next(TC_block)
    my_digest = my_sha256.get_digest()
    
    
    #Return back to byte
    reconstructed_bytes = b''.join(x.to_bytes(4, byteorder='big') for x in my_digest)
    return reconstructed_bytes.hex()
    
print(sha256_naked(b'\x61\x62\x63\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18'))