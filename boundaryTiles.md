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

## Example of Compiling and Running a Kernel

### Manually

Compile:

```
make DEBUG=ON sw -j
```

Run without script:

```
cd sw/kernels/blas/gemm_boundary/build
../scripts/verify.py snitch_cluster.vlt gemm_boundary.elf > verify-output.txt;
```

### Using Scripts from the Myrtle Repo

Checkout Myrtle repo branch [here](https://github.com/CAPS-UMU/myrtle/tree/expand-cost-model-for-matmul)

1. make a folder and input.txt containing the input matmul dimensions, in this case 16x16x16
2. generate scripts to compile and run this matmul on the snitch cluster using the `createExperiment.py` script

```
cd scripts
mkdir ../16x16x16
echo "beta=0" > ../16x16x16/input.txt; echo "16x16x16" >> ../16x16x16/input.txt
python createExperiment.py "../16x16x16/input.txt" "../16x16x16" "_ss_c_rem_div_ana_pruned"
```

Instead of "_ss_c_rem_div_ana_pruned", you can use "full" to query myrtle for the full search space instead of a pruned one.

3. Copy the folder and all of its contents to the top level of the snitch repo directory

4. Modify the search space file (remove rows as desired) to make sure you only compile and run the tiling schemes you want

5. Compile and run from inside the `16x16x16` experiment folder*

   ```
   bash compile.sh
   bash run.sh
   bash extract.sh
   ```

   * make sure to set this environment variable before running the scripts!
     ```
     export gemmDir="/repo/sw/kernels/blas/gemm_boundary"
     ```

     
