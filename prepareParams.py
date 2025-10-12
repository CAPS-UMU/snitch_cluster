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
    "gemm_fp": "gemm_fp64_opt"
}

def main():
    if len(sys.argv) != 8:
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
        m_tiles=int(M/m)
        n_tiles=int(N/n)
        k_tiles=int(K/k)
        print("\t",end='')
        print(f'prepareParams.py: we are working with {fp} {M}x{N}x{K} with num tiles {m_tiles} {n_tiles} {k_tiles}')
        #    searchSpaceDF=pd.read_csv(sys.argv[1])
        # for i in range(0, searchSpaceDF.shape[0]):
        # theName = searchSpaceDF["JSON Name"][i]
        # rowDim = searchSpaceDF["Row Dim"][i]
        # redDim = searchSpaceDF["Reduction Dim"][i]
        # jsonPath = f"{sys.argv[3]}/{theName}.json"
        # print(f'writing to {jsonPath}')
        #jsonPath = f"{testerFolder}/{theName}.json"
        # with open(fp) as json_file:
        #         data = json.load(json_file)
        data=defaultSettings
        data["m"]=M 
        data["n"]=N 
        data["k"]=K
        data["m_tiles"]=m_tiles
        data["n_tiles"]=n_tiles
        data["k_tiles"]=k_tiles
        f = open(fp, "w")   # 'r' for reading and 'w' for writing 
    #   #  data[f'{sys.argv[2]}']["tile-sizes"]=[[0], [int(rowDim)], [int(redDim)]]
        f.write(f"{json.dumps(data)}")
        f.close()  
        # expName=sys.argv[1]
        # logs=sys.argv[2]
        # if not os.path.exists(logs):
        #     print("\t",end='')
        #     print(f'generateTileSizeJSONFiles.py: Error: directory {logs} does not exist.')
        #     return 1
        # computeCores=[
        #     f"{logs}/hart-trace_hart_00000-perf.json",
        #     f"{logs}/hart-trace_hart_00001-perf.json",
        #     f"{logs}/hart-trace_hart_00002-perf.json",
        #     f"{logs}/hart-trace_hart_00003-perf.json",
        #     f"{logs}/hart-trace_hart_00004-perf.json",
        #     f"{logs}/hart-trace_hart_00005-perf.json",
        #     f"{logs}/hart-trace_hart_00006-perf.json",
        #     f"{logs}/hart-trace_hart_00007-perf.json",
        # ]
        # row=[]
        # minStart=-1
        # maxEnd=0
        # for c in computeCores:
        #     with open(c) as json_file:
        #         data = json.load(json_file)
        #         start=data[1]["start"]
        #         end=data[1]["end"]
        #         end_fpss=data[1]["end_fpss"]
        #         cycles=data[1]["cycles"]
        #         row.append(int(cycles))
        #         if minStart == -1:
        #             minStart=start
        #         if start <= minStart:
        #             minStart = start
        #         if end > maxEnd:
        #             maxEnd = end
        #         print(f"{c}: start: {start} end:{end} end_fpss:{end_fpss}")
        # with open(f"{logs}/hart-trace_hart_00008-perf.json") as json_file:
        #     data = json.load(json_file)
        #     dma_cycles=data[0]["cycles"]
        #     row.append(dma_cycles)
        # row.append(maxEnd-minStart + 1)
        # timeData=np.array(row, dtype='int').reshape(1,10)
        # cols=('core0','core1','core2','core3','core4','core5','core6','core7','dma','Kernel Time')
        # df = pd.DataFrame(data=timeData, columns=cols)
        # df['FakeNN JSON Name']=expName
        # df.to_csv(f"{logs}/{expName}.csv")

if __name__ == "__main__":
    main()

    # # for each input size and tiling scheme
    # # save a json tiling scheme given m, n, k
    # # save a json tiling scheme with m=0, n=0, k=0 (golden)
    # searchSpaceDF=pd.read_csv(sys.argv[1])
    # for i in range(0, searchSpaceDF.shape[0]):
    #     theName = searchSpaceDF["FakeNN JSON Name"][i]
    #     m = searchSpaceDF["m"][i]
    #     n = searchSpaceDF["n"][i]
    #     k=searchSpaceDF["k"][i]
    #     mC = searchSpaceDF["M"][i]
    #     nC = searchSpaceDF["N"][i]
    #     kC=searchSpaceDF["K"][i]
    #     # create json representation of tiling scheme
    #     data = {}
    #     node = {}
    #     node["tile-sizes"] = [[0], [40], [100]]
    #     node["loop-order"] = [[2,0], [0,0], [1,0]]
    #     node["dual-buffer"] = True
    #     dispatchName = f'main$async_dispatch_0_matmul_transpose_b_{mC}x{nC}x{kC}_f64'
    #     data[dispatchName]=node
    #     # if ts dne, generate it
    #     jsonPath = f"{sys.argv[2]}/{theName}.json"
    #     if not os.path.exists(jsonPath):
    #         print("\t",end='')
    #         print(f'generateTileSizeJSONFiles.py: writing to {jsonPath}')
    #         f = open(jsonPath, "w")   # 'r' for reading and 'w' for writing 
    #         data[f'{dispatchName}']["tile-sizes"]=[[int(m)], [int(n)], [int(k)]]
    #         f.write(f"{json.dumps(data)}")
    #         f.close()
    #     else:
    #         print("\t",end='')
    #         print(f'generateTileSizeJSONFiles.py: using cached {jsonPath}')
    #     # if golden ts dne, generate it
    #     theName=f'{mC}x{nC}x{kC}w{0}-{0}-{0}'
    #     jsonPath = f"{sys.argv[3]}/{theName}.json"
    #     if not os.path.exists(jsonPath):
    #         print("\t",end='')
    #         print(f'generateTileSizeJSONFiles.py: writing to {jsonPath}')
    #         f = open(jsonPath, "r")   # 'r' for reading and 'w' for writing 
    #         data[f'{dispatchName}']["tile-sizes"]=[[int(0)], [int(0)], [int(0)]]
    #         f.write(f"{json.dumps(data)}")
    #         f.close()
    #     else:
    #         print("\t",end='')
    #         print(f'generateTileSizeJSONFiles.py: using cached {jsonPath}')
   
    