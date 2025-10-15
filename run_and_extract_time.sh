# run a gemm executable and extract timing information from its verilator logs
# this script takes as arguments
# buildDir
# extractKernelTime // path to python script
# expName
# logs
# M
# N
# K
# m
# n
# k

buildDir=$1
extractKernelTime=$2
expName=$3
logs=$4
M=$5
N=$6
K=$7
m=$8
n=$9
k=$10

echo -e "\trun_and_extract_time.sh: Arguments passed in are $buildDir $extractKernelTime $expName $logs $M $N $K $m $n $k"

cd $buildDir
correct=$(../scripts/verify.py snitch_cluster.vlt gemm.elf > verify-output.txt; echo $?)
if [[ "$correct" != "0" ]]; 
then
    echo -e "\trun_and_extract_time.sh: Error: tiled gemm did not produce expected result! Errno $correct"
else
    echo -e "\trun_and_extract_time.sh: Ran gemm and no errors."
fi

# extract timing info
genTrace logs "trace_hart_00000"
genTrace logs "trace_hart_00001"
genTrace logs "trace_hart_00002"
genTrace logs "trace_hart_00003"
genTrace logs "trace_hart_00004"
genTrace logs "trace_hart_00005"
genTrace logs "trace_hart_00006"
genTrace logs "trace_hart_00007"
genTrace logs "trace_hart_00008" dma
python $extractKernelTime $expName $logs $M $N $K $m $n $k

# delete huge log files
cd $logs
rm -rf *.dasm

