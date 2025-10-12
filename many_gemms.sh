echo -e "\tmany_gemms.sh: This script compiles, runs, and exports timing info for many gemm kernels run on the snitch cluster."
echo -e "\tmany_gemms.sh: Always run this script from the top level directory (/repo inside the docker image)"
echo -e "\tmany_gemms.sh: Invoke this script with 'bash many_gemms.sh <searchSpace.csv>'"
here="$(pwd)" # save current directory so we can return to it
gemmDir="$here/sw/kernels/blas/gemm"
params="$gemmDir/data/params.json"
extractKernelTime="$here/extractKernelTimeFromJsons.py"

genTrace(){
    gen_trace="$here/util/trace/gen_trace.py"
    llvm_mc="/tools/riscv-llvm/bin/llvm-mc"
    logsDir="$1" # absolute path of the logs directory
    logWOFE="$2" # log file without the .dasm file extension
    dma="$3"
    echo "logsDir is $logsDir and log file is $logWOFE and dma is $dma"
    if [[ "$exists" != "0" ]]; 
    then
        $gen_trace "$logsDir/$logWOFE.dasm" --mc-exec $llvm_mc --mc-flags "-disassemble -mcpu=snitch" --dma-trace "$logsDir/$logWOFE.log" --dump-hart-perf "$logsDir/hart-$logWOFE-perf.json" --dump-dma-perf "$logsDir/dma-$logWOFE-perf.json" -o "$logsDir/$logWOFE.txt"
    else
        $gen_trace "$logsDir/$logWOFE.dasm" --mc-exec $llvm_mc --mc-flags "-disassemble -mcpu=snitch" --dump-hart-perf "$logsDir/hart-$logWOFE-perf.json" -o "$logsDir/$logWOFE.txt"
    fi
    return 0
}

compile(){
    ss="$1"
    echo -e "\tmany_gemms.sh: COMPILE step"
    uniquePointRegex='^(([0-9]*)x([0-9]*)x([0-9]*))w([0-9]*)-([0-9]*)-([0-9]*)'
    for ts in $(grep -oE $uniquePointRegex $ss)
            do
            eatNum='^([0-9])([0-9])*'
            M=$(echo $ts | grep -oE $eatNum)
            tail=${ts#*x}
            N=$(echo $tail | grep -oE $eatNum)
            tail=${tail#*x}
            K=$(echo $tail | grep -oE $eatNum)
            tail=${tail#*w}
            m=$(echo $tail | grep -oE $eatNum)
            tail=${tail#*-}
            n=$(echo $tail | grep -oE $eatNum)
            tail=${tail#*-}
            k=$(echo $tail | grep -oE $eatNum)
            buildDir="$gemmDir/"$M"x"$N"x"$K"w"$m"-"$n"-"$k
            echo -e "\t\t$M $N $K $m $n $k with build directory $buildDir"
            rm -rf $buildDir 2>/dev/null
            python prepareParams.py $params $M $N $K $m $n $k
            make DEBUG=ON sw -j
            cp -r "$gemmDir/build" $buildDir
            done
}

runAndExtract(){
    ss="$1"
    echo -e "\tmany_gemms.sh: RUN + EXPORT step"
    uniquePointRegex='^(([0-9]*)x([0-9]*)x([0-9]*))w([0-9]*)-([0-9]*)-([0-9]*)'
    for ts in $(grep -oE $uniquePointRegex $ss)
            do
            eatNum='^([0-9])([0-9])*'
            M=$(echo $ts | grep -oE $eatNum)
            tail=${ts#*x}
            N=$(echo $tail | grep -oE $eatNum)
            tail=${tail#*x}
            K=$(echo $tail | grep -oE $eatNum)
            tail=${tail#*w}
            m=$(echo $tail | grep -oE $eatNum)
            tail=${tail#*-}
            n=$(echo $tail | grep -oE $eatNum)
            tail=${tail#*-}
            k=$(echo $tail | grep -oE $eatNum)
            expName=$M"x"$N"x"$K"w"$m"-"$n"-"$k
            buildDir="$gemmDir/"$expName
            echo -e "\t\t$M $N $K $m $n $k with build directory $buildDir"
            logs="$buildDir/logs"
            # run gemm
            cd $buildDir
            correct=$(../scripts/verify.py snitch_cluster.vlt gemm.elf > verify-output.txt; echo $?)
            if [[ "$correct" != "0" ]]; 
            then
                echo -e "\tmany_gemms.sh: Error: tiled gemm did not produce expected result! Errno $correct"
                return 1
            else
                echo -e "\tmany_gemms.sh: Ran gemm and no errors."
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

            # aggregate timing info into single json

            # delete huge log files
            cd $logs
            rm -rf *.dasm

            cd $here
            
            done
}

onlyExtract(){
    ss="$1"
    echo -e "\tmany_gemms.sh: ONLY EXPORT step"
    uniquePointRegex='^(([0-9]*)x([0-9]*)x([0-9]*))w([0-9]*)-([0-9]*)-([0-9]*)'
    for ts in $(grep -oE $uniquePointRegex $ss)
            do
            eatNum='^([0-9])([0-9])*'
            M=$(echo $ts | grep -oE $eatNum)
            tail=${ts#*x}
            N=$(echo $tail | grep -oE $eatNum)
            tail=${tail#*x}
            K=$(echo $tail | grep -oE $eatNum)
            tail=${tail#*w}
            m=$(echo $tail | grep -oE $eatNum)
            tail=${tail#*-}
            n=$(echo $tail | grep -oE $eatNum)
            tail=${tail#*-}
            k=$(echo $tail | grep -oE $eatNum)
            expName=$M"x"$N"x"$K"w"$m"-"$n"-"$k
           # expName=$M"x"$N"x"$K"w"$m"-"$n"-"$k"-ndb"
            buildDir="$gemmDir/"$expName
            echo -e "\t\t$M $N $K $m $n $k with build directory $buildDir"
            logs="$buildDir/logs"
            cd $buildDir
            python $extractKernelTime $expName $logs $M $N $K $m $n $k
            # aggregate timing info into single json
            cd $here            
            done
}

main(){
    ss=$1
    # check arguments
    exists=$(ls $ss &> /dev/null; echo $?)
    if [[ "$exists" != "0" ]]; 
    then
        echo -e "\tmany_gemms.sh: Error: $ss csv file does not exist. Errno $exists"
        return 1
    fi

    if [[ "$2" == "compile" ]]; 
    then
        compile $ss
    fi
    
    if [[ "$3" == "run" ]]; 
    then
        runAndExtract $ss
    fi

    if [[ "$4" == "extract" ]]; 
    then
        onlyExtract $ss
    fi

    echo -e "\tmany_gemms.sh: DONE"
    return 0
}

main $1 $2 $3 $4
