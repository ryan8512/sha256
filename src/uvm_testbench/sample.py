from sha256 import SHA256

def sha256_naked(block) -> str:
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
    
print(sha256_naked("aaaaaaaaaaaaaaaa5555555555555555aaaaaaaaaaaaaaaa5555555555555555aaaaaaaaaaaaaaaa5555555555555555aaaaaaaaaaaaaaaa5555555555555555"))

#0xaaaaaaaaaaaaaaaa5555555555555555aaaaaaaaaaaaaaaa5555555555555555aaaaaaaaaaaaaaaa5555555555555555aaaaaaaaaaaaaaaa5555555555555555