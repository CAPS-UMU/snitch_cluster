import sys
import pandas as pd
import numpy as np
import json
import os.path
import math
print("\n\t\textractDataFromJsons.py: ATTN: only many_gemms.sh should call this script.")

def stallCycles(core_json,rgc,idx):
    d = {}
    prologue = core_json[0]
    epilogue = core_json[-1]
    overlapStallTime = 0
    rawComputeTime = 0
    # region 0 is the proglogue
    # region 1 is the first compute tile
    # region 2 is the time spent after the first compute tile and before the next one
    # we want every other region starting from region 2 until the epilogue
    for i in range(2,rgc,2):
        overlapStallTime = overlapStallTime + core_json[i]["cycles"]
    # region 0 is the proglogue
    # region 1 is the first compute tile
    # region 2 is the time spent after the first compute tile and before the next one
    # we want every other region starting from region 1 until the epilogue
    for i in range(1,rgc,2):
        rawComputeTime = rawComputeTime + core_json[i]["cycles"]
    d[f"Before Computation_cc_{idx}"] = prologue["cycles"]
    d[f"After Computation_cc_{idx}"] = epilogue["cycles"]
    d[f"Overlap Stall Time_cc_{idx}"] = overlapStallTime
    d[f"Raw Compute Time_cc_{idx}"] = rawComputeTime
    d[f"cc_tiles_cc_{idx}"] = (rgc-1) / 2
    return (list(d.values()),list(d.keys()))

def regionCount(M,N,K,m,n,k,idx):
    m_cluster_tiles = int(M / m) * math.ceil(N/n) * math.ceil(K/k)
    m_rem_cluster_tiles = 1 * math.ceil(N/n) * math.ceil(K/k)
    rem_m = M % m
    if idx < rem_m:
        rc = 2*(m_cluster_tiles + m_rem_cluster_tiles) + 1
    else:
        rc = 2 * m_cluster_tiles + 1
    return rc

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
        cCores = []
        # region count reality check
        for idx in range(0,len(computeCores)):
            c = computeCores[idx]
            rgc = regionCount(M,N,K,m,n,k,idx)
            with open(c) as json_file:
                data = json.load(json_file)
                #print(f"In the current json, there are {len(data)} regions.")
                if rgc != len(data):
                    raise Exception(f"PARSE ERROR! JSON {c} contains an an unexpected number of regions: Expected:{rgc} Actual:{len(data)}")
                else:
                    cCores.append((c,rgc,idx))

      # end of reality check
        row=[]
        minStart=-1
        maxEnd=0
        stallCycleRow = []
        stallCycleCols = []
        for (c,rgc,idx) in cCores:
            with open(c) as json_file:
                data = json.load(json_file)
                (stallVals, stallCols) = stallCycles(data,rgc,idx)
                stallCycleRow = stallCycleRow + stallVals
                stallCycleCols = stallCycleCols + stallCols
                start=data[1]["start"] # second region from beginning
                end=data[rgc-2]["end"] # second to last region
                end_fpss=data[rgc-2]["end_fpss"]
                cycles=max(end,end_fpss) - start
                row.append(int(cycles))
                if minStart == -1:
                    minStart=start
                if start <= minStart:
                    minStart = start
                if end > maxEnd:
                    maxEnd = end
               # print(f"{c}: start: {start} end:{end} end_fpss:{end_fpss}")
        dma = f"{logs}/hart-trace_hart_00008-perf.json"
        with open(dma) as json_file:
            data = json.load(json_file)
            dma_cycles=data[0]["cycles"]
            row.append(dma_cycles)
       # print(f"{dma} (dma): cycles: {dma_cycles}")
        row.append(maxEnd-minStart + 1)
        cols=['core0','core1','core2','core3','core4','core5','core6','core7','dma','Kernel Time']
        row = row + stallCycleRow
        cols = cols + stallCycleCols
        timeData=np.array(row, dtype='int').reshape(1,len(row))
        
        df = pd.DataFrame(data=timeData, columns=cols)
        df["Total CC Tiles"] = df["cc_tiles_cc_0"] + df["cc_tiles_cc_1"] + df["cc_tiles_cc_2"] + df["cc_tiles_cc_3"] + df["cc_tiles_cc_4"] + df["cc_tiles_cc_5"] + df["cc_tiles_cc_6"] + df["cc_tiles_cc_7"]
        df["Overlap Stall Time Total"] = df["Overlap Stall Time_cc_0"] + df["Overlap Stall Time_cc_1"] + df["Overlap Stall Time_cc_2"] + df["Overlap Stall Time_cc_3"] + df["Overlap Stall Time_cc_4"] + df["Overlap Stall Time_cc_5"] + df["Overlap Stall Time_cc_6"] + df["Overlap Stall Time_cc_7"]
        df["Raw Compute Time Total"] = df["Raw Compute Time_cc_0"] + df["Raw Compute Time_cc_1"] + df["Raw Compute Time_cc_2"] + df["Raw Compute Time_cc_3"] + df["Raw Compute Time_cc_4"] + df["Raw Compute Time_cc_5"] + df["Raw Compute Time_cc_6"] + df["Raw Compute Time_cc_7"]
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
   
    