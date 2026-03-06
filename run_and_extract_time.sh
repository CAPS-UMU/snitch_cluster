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
k=${10}
here=${11}
elf=$(basename $gemmDir)

genTrace(){
    gen_trace="$here/util/trace/gen_trace.py"
    llvm_mc="/tools/riscv-llvm/bin/llvm-mc"
    logsDir="$1" # absolute path of the logs directory
    logWOFE="$2" # log file without the .dasm file extension
    dma="$3"
    echo "logsDir is $logsDir and log file is $logWOFE and dma is $dma"
    if [[ "$dma" != "dma" ]]; 
    then
        $gen_trace "$logsDir/$logWOFE.dasm" --mc-exec $llvm_mc --mc-flags "-disassemble -mcpu=snitch" --dma-trace "$logsDir/$logWOFE.log" --dump-hart-perf "$logsDir/hart-$logWOFE-perf.json" --dump-dma-perf "$logsDir/dma-$logWOFE-perf.json" -o "$logsDir/$logWOFE.txt"
    else
        $gen_trace "$logsDir/$logWOFE.dasm" --mc-exec $llvm_mc --mc-flags "-disassemble -mcpu=snitch" --dump-hart-perf "$logsDir/hart-$logWOFE-perf.json" -o "$logsDir/$logWOFE.txt"
    fi
    return 0
}

echo -e "\trun_and_extract_time.sh: Arguments passed in are $buildDir $extractKernelTime $expName $logs $M $N $K $m $n $k"

cd $buildDir
correct=$(../scripts/verify.py snitch_cluster.vlt $elf.elf > verify-output.txt; echo $?)
if [[ "$correct" != "0" ]]; 
then
    echo -e "\trun_and_extract_time.sh: Error: tiled $elf did not produce expected result! Errno $correct"
    return 1
else
    echo -e "\trun_and_extract_time.sh: Ran $elf correctly."
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
correct=$(echo $?)
if [[ "$correct" == "0" ]]; 
then
    echo -e "\trun_and_extract_time.sh: Successfully exported timing information. Deleting logs..."
    # delete huge log files
    cd $logs
    rm -rf *.dasm
else
    echo -e "\trun_and_extract_time.sh: Error exporting timing info!"
fi


