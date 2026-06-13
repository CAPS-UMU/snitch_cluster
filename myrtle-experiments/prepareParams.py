import sys
import pandas as pd
import numpy as np
import json
import os.path
print("\n\tprepareParams.py: ATTN: only many_gemms.sh should call this script.")

defaultSettings={
    "setup_ssr": 1,
    "parallelize_m": 1,
    "parallelize_k": 0,
    "m_tiles": 1, 
    "n_tiles": 1, 
    "k_tiles": 1, 
    "load_a": 1,
    "load_b": 1,
    "load_c": 1,
    "double_buffer": 1,
    "partition_banks": 0,
    "transa": False,
    "transb": False, 
    "m": 32,
    "n": 16,
    "k": 16,
    "alpha": 1,
    "beta": 0,
    "gemm_fp": "gemm_fp64_opt_myrtle"
}

def main():
    if len(sys.argv) != 9:
        print("\t",end='')
        print(f"prepareParams.py: USAGE: One params.json file path followed by 6 integer arguments: M N K m n k.\nYou passed in {len(sys.argv)} args")
    else:
        fp=sys.argv[1]
        M=int(sys.argv[2])
        N=int(sys.argv[3])
        K=int(sys.argv[4])
        m=int(sys.argv[5])
        n=int(sys.argv[6])
        k=int(sys.argv[7])
        padding = sys.argv[8]
       # print(f"my vals are {M} {N} {K} {m} {n} {k} ")
        paddedM = m * (M // m) + m if (M % m) != 0 else M
        paddedN = n * (N // n) + n if (N % n) != 0 else N
        paddedK = k * (K // k) + k if (K % k) != 0 else K
        if (M % m != 0.0) or (N % n != 0.0) or (K % k != 0.0):
            if "padded" not in f'{padding}':
                raise Exception(f'prepareParams.py: Error: one of the tile sizes {m}, {n}, or {k} does not divide evenly into input size {M}x{N}x{K}')
            else:
                print("\t",end='')
                print(f"prepareParams.py: gemmDir env var {padding} contains the word padded, so we are setting params for boundary tiles.")
        beta = os.getenv('beta', "-42")
        if(beta=="-42"):
            print("\t",end='')
            print("prepareParams.py: Warning: beta env not set. defaulting beta to 0.")
            beta = 0
        else:
            beta = int(beta)
            print("\t",end='')
            print(f"prepareParams.py: beta is {beta}")
        m_tiles=int(paddedM/m)
        n_tiles=int(paddedN/n)
        k_tiles=int(paddedK/k)
        print("\t",end='')
        print(f'prepareParams.py: we are working with {fp} {M}x{N}x{K} with num tiles {m_tiles} {n_tiles} {k_tiles}')
        data=defaultSettings
        data["m"]=paddedM 
        data["n"]=paddedN 
        data["k"]=paddedK
        data["m_tiles"]=m_tiles
        data["n_tiles"]=n_tiles
        data["k_tiles"]=k_tiles
        data["m_unpadded"]=M 
        data["n_unpadded"]=N 
        data["k_unpadded"]=K
        data["beta"]=beta
        f = open(fp, "w")   # 'r' for reading and 'w' for writing 
        f.write(f"{json.dumps(data)}")
        f.close()  
        return 0


if __name__ == "__main__":
    main()

   