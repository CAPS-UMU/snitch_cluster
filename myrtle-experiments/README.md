# Extending Tiled Matmul with Remainder Tiles
## APPTAINER
### Do this once
From *inside* the `snitch_cluster` directory:
```
docker build --target snitch_cluster-hw -t ghcr.io/pulp-platform/snitch_cluster-hw:main -f util/container/Dockerfile .

apptainer build util/container/snitch_cluster-hw.sif docker-daemon://ghcr.io/pulp-platform/snitch_cluster-hw:main

apptainer build --sandbox util/container/snitch_cluster-hw-sandbox util/container/snitch_cluster-hw.sif

apptainer shell --bind .:/repo util/container/snitch_cluster-hw-sandbox

cd /repo

bender update
```
### Daily Commands
```
export PATH=$PATH:/home/esillars/apptainer-build/bin

cd snitch_cluster

apptainer shell --bind .:/repo util/container/snitch_cluster-hw-sandbox

cd /repo

export gemmDir="/repo/sw/kernels/blas/matmul_padded"
```
## DOCKER
from inside snitch_cluster directory,
```
sudo docker build --target snitch_cluster-hw -t ghcr.io/pulp-platform/snitch_cluster-hw:main -f util/container/Dockerfile .
```

### Daily Commands

Make sure you are *outside* the `snitch_cluster` directory!

```
docker run -it --entrypoint /bin/bash -v $PWD/snitch_cluster:/repo -w /repo ghcr.io/pulp-platform/snitch_cluster-hw:main
```

Make sure to check your env vars are set before running any scripts!

For remainder and divisor tiles:

```
export gemmDir="/repo/sw/kernels/blas/matmul_padded"
```

Compile without script:

```
make DEBUG=ON sw -j
```

Run without script:

```
cd build-directory
../scripts/verify.py snitch_cluster.vlt gemm.elf > verify-output.txt;
```

## gemm (unmodified) contraints

```
# m, n, and k must all divide evenly into corresponding M,N,K input sizes
# n must be a multiple of 8 due to fixed unroll and jam factor of 8
# m, n, and k must each be able to fit into 8 TCDM banks (optimized scratchpad layout constraint)
```
where `l1MemoryBytes = 112 * 1024`, `bank_size=1024`, `dualBuff=True`

### example of compiling and running a kernel

```
cd 16x16x16
bash compile.sh
bash run.sh
bash extract.sh
```

^the folder `16x16x16` and its contents were created by running inside the myrtle repo `python topTenFromMNK.py "inputSize16x16x16.txt" 16x16x16` and the removing all tiling schemes except the 8-8-8 one from the search space file.

## gemm-padded (relaxed constraints for remainder tiles)

```
# n must be a multiple of 8 due to fixed unroll and jam factor of 8
# m, n, and k must each be able to fit into 8 TCDM banks (optimized scratchpad layout constraint)
# k must be >= 3 due to hard-coded assembly's hardware loop's epilogue and prologue
```
where `l1MemoryBytes = 112 * 1024`, `bank_size=1024`, `dualBuff=True`

### Example of padding in M dimension: 24x24x24w16-8-8

todo

### Example of padding in N dimension: 24x24x24w8-16-8

This is the dimension we care about padding the most, so we will start with this case.



### Example of padding in K dimension: 24x24x24w8-8-16

todo

### Example of padding in all three dimensions: 24x24x24w5-16-7

todo



