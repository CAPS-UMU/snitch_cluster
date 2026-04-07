import sys
import pandas as pd
import numpy as np
import json
import os.path
import math
print("\n\t\textractKernelTimeFromJsons.py: ATTN: only many_gemms.sh should call this script.")

def main():
    if len(sys.argv) != 9:
        print("\t",end='')
        print(f"USAGE: Requires two string arguments, experiment name and the full path to the experiment's logs folder, followed by M N K m n k.\nYou passed in {len(sys.argv)} args")
    else:
        expName=sys.argv[1]
        logs=sys.argv[2]
        if not os.path.exists(logs):
            print("\t\t",end='')
            print(f'extractKernelTimeFromJsons.py: Error: directory {logs} does not exist.')
            return 1
        M=int(sys.argv[3])
        N=int(sys.argv[4])
        K=int(sys.argv[5])
        m = int(sys.argv[6])
        n = int(sys.argv[7])
        k = int(sys.argv[8])
        m_tiles=math.ceil(M/m)
        n_tiles=math.ceil(N/n)
        k_tiles=math.ceil(K/k)
        cluster_tiles=m_tiles*n_tiles*k_tiles
        regionCount=2*cluster_tiles+1
        computeCores=[
            f"{logs}/hart-trace_hart_00000-perf.json",
            f"{logs}/hart-trace_hart_00001-perf.json",
            f"{logs}/hart-trace_hart_00002-perf.json",
            f"{logs}/hart-trace_hart_00003-perf.json",
            f"{logs}/hart-trace_hart_00004-perf.json",
            f"{logs}/hart-trace_hart_00005-perf.json",
            f"{logs}/hart-trace_hart_00006-perf.json",
            f"{logs}/hart-trace_hart_00007-perf.json",
        ]
        # reality check
        for c in computeCores:
            with open(c) as json_file:
                data = json.load(json_file)
                if regionCount != len(data):
                    if m % 8 == 0:
                        raise Exception(f"ATTENTION! DIFFERENT ERROR! JSON {c} contains an an unexpected number of regions: Expected:{regionCount} Actual:{len(data)}")
                    else:
                        raise Exception(f"KNOWN ERROR: JSON {c} contains an an unexpected number of regions, WHICH MAKES A LITTLE SENSE: Expected:{regionCount} Actual:{len(data)}")
        # end of reality check
        row=[]
        minStart=-1
        maxEnd=0
        for c in computeCores:
            with open(c) as json_file:
                data = json.load(json_file)
                start=data[1]["start"] # second region from beginning
                end=data[regionCount-2]["end"] # second to last region
                end_fpss=data[regionCount-2]["end_fpss"]
                cycles=max(end,end_fpss) - start
                row.append(int(cycles))
                if minStart == -1:
                    minStart=start
                if start <= minStart:
                    minStart = start
                if end > maxEnd:
                    maxEnd = end
                print(f"{c}: start: {start} end:{end} end_fpss:{end_fpss}")
        dma = f"{logs}/hart-trace_hart_00008-perf.json"
        with open(dma) as json_file:
            data = json.load(json_file)
            dma_cycles=data[0]["cycles"]
            row.append(dma_cycles)
        print(f"{dma} (dma): cycles: {dma_cycles}")
        row.append(maxEnd-minStart + 1)
        timeData=np.array(row, dtype='int').reshape(1,10)
        cols=('core0','core1','core2','core3','core4','core5','core6','core7','dma','Kernel Time')
        df = pd.DataFrame(data=timeData, columns=cols)
        df['FakeNN JSON Name']=expName
        df.to_csv(f"{logs}/{expName}.csv", index=False)
        return 0

if __name__ == "__main__":
    if main() != 0:
        raise Exception("")

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
   
    