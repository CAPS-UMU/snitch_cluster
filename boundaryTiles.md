# Extending Matmul with Boundary Tiles
## Daily Commands

Make sure you are *outside* the `snitch_cluster` directory!

```
docker run -it --entrypoint /bin/bash -v $PWD/snitch_cluster:/repo -w /repo ghcr.io/pulp-platform/snitch_cluster-hw:main
```

Make sure to check your env vars are set before running any scripts!

For boundary tiles:

```
export gemmDir="/repo/sw/kernels/blas/gemm_boundary"
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

## gemm (unmodified)

```
# m, n, and k must all divide evenly into corresponding M,N,K input sizes
# n must be a multiple of 8 due to fixed unroll and jam factor of 8
# m, n, and k must each be able to fit into 8 TCDM banks (optimized scratchpad layout constraint)
```
where `l1MemoryBytes = 112 * 1024`, `bank_size=1024`, `dualBuff=True`

Make sure to check your env vars are set before running any scripts!

```
export gemmDir="/repo/sw/kernels/blas/gemm"
```

### example of compiling and running a kernel

```
cd 16x16x16
bash compile.sh
bash run.sh
bash extract.sh
```

^the folder `16x16x16` and its contents were created by running inside the myrtle repo `python topTenFromMNK.py "inputSize16x16x16.txt" 16x16x16` and the removing all tiling schemes except the 8-8-8 one from the search space file.



