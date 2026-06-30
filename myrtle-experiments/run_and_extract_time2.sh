#!/bin/bash
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



# gemini helped me write the timeout functino for this script
timeout(){
    # 1. Start process A (verify.py) in the background
 #   python3 verify.py > output.txt 2>&1 &
    $gemmDir/scripts/verify.py snitch_cluster.vlt $elf.elf "--myrtleTimeout=$TIMEOUT" > verify-output.txt &
#    correct=$($gemmDir/scripts/verify.py snitch_cluster.vlt $elf.elf --myrtleTimeout=5 > verify-output.txt; echo $?)
    
    PID_A=$!

    echo "Started Process A (PID: $PID_A)"

    # 2. Periodically check for the timeout string or process completion
    while true; do
        # Check if the process is still running
        if ! kill -0 $PID_A 2>/dev/null; then
            # Process A finished on its own
            wait $PID_A
            EXIT_STATUS=$?
            break
        fi

        # Check if "myrtleTimeout" appears in output.txt
        if grep -q "Myrtle Experiment Timeout" output.txt; then
            echo "Timeout detected! Cleaning up process tree..."

            # Find Process B (Child of A)
            PID_B=$(pgrep -P $PID_A)
            
            if [ -n "$PID_B" ]; then
                # Find Process C (Child of B)
                PID_C=$(pgrep -P $PID_B)
                
                # Kill in reverse order (Grandchild -> Child -> Parent)
                [ -n "$PID_C" ] && kill -9 $PID_C 2>/dev/null
                kill -9 $PID_B 2>/dev/null
            fi

            kill -9 $PID_A 2>/dev/null
            EXIT_STATUS=1
            echo "simulation failed on timeout."> verify-output.txt
            ls -l -h logs/*.dasm
            rm -rf "logs"
            rm -rf "dma_trace_00008_00000.log"
            break
        fi

        sleep 1
    done

    # 3. Print success or error based on exit status
    if [ $EXIT_STATUS -eq 0 ]; then
        echo "ran simulation correctly"
    else
        echo "error or timeout while running simulation"
    fi
}

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

main(){

    echo -e "\trun_and_extract_time.sh: Arguments passed in are $buildDir $extractKernelTime $expName $logs $M $N $K $m $n $k"

    cd $buildDir
    #correct=$($gemmDir/scripts/verify.py snitch_cluster.vlt $elf.elf --myrtleTimeout=5 > verify-output.txt; echo $?)
    timeout
    correct=$(echo $?)
    if [[ "$correct" != "0" ]]; 
    then
        echo -e "\trun_and_extract_time.sh: Simulation failed, so skipping export step. $correct"
        rm -rf "dma_trace_00008_00000.log"
        # delete huge log files
        cd $logs
        ls -l -h *.dasm
        rm -rf *.dasm
        rm -rf *.txt
        return 1
    fi

    # extract timing info
    if [[ -n "$TRACE_DMA_ONLY" ]]; then
        genTrace logs "trace_hart_00008" dma
    else
        for hartNum in 00000 00001 00002 00003 00004 00005 00006 00007 00008; do
            genTrace logs "trace_hart_${hartNum}"
        done
    fi
    python $extractKernelTime $expName $logs $M $N $K $m $n $k
    correct=$(echo $?)
    if [[ "$correct" == "0" ]]; 
    then
        echo -e "\trun_and_extract_time.sh: Successfully exported timing information. Deleting logs..."
        # delete huge log files
        cd $logs
        ls -l -h *.dasm
        rm -rf *.dasm
        rm -rf *.txt
        cd ..
        rm -rf "dma_trace_00008_00000.log"
    else
        echo -e "\trun_and_extract_time.sh: Error exporting timing info!"
    fi
}

main

