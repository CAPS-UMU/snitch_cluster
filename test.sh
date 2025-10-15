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

echo "$buildDir $extractKernelTime $expName $logs $M $N $K $m $n $k"

