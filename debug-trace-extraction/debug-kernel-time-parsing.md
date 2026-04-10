# How many regions should a timed, tiled matmul have?

### When the matmul uses exclusively divisor tiles, the answer is

```
2 * (m_tiles * n_tiles * k_tiles) + 1
```

- The first region is the time from the start of program execution until the first `mcycle()` call.

- After the `mcycle()` call, the compute core processes one compute core tile (right?!)

- At the end of the computation, `mcycle()` gets called again to mark the end of the region of interest.

Now we have three regions:

```
---- start of program execution ----|
-                                   |  REGION 0
-                                   |
----     first mcycle call      ----| 
-                                   |  REGION 1
-  compute core tile computation    |
-                                   |
----    second mcycle call      ----|
-                                   |  REGION 2
-                                   |
--- (program ends or next mcycle) --|
-              ...                  |
```

- The final region is the time of the last computation's closing `mcycle()` until the end of the program.
- Regardless of what that region represents, we will have `2 * compute_core_tiles_per_core + 1` regions,
  where `compute_core_tiles_per_core = m_tiles * n_tiles * k_tiles * 8 / 8`

### When the matmul uses remainder tiles, the answer is

I'm not sure yet, but we do know that the lower indexed cores process extra elements when `m_hat` gets processed instead of an `m'` sized tile. But this doesn't change the number of compute cores, right? So is it a coincidence that the only failing extractions are when the m dimension is not divisible by 8? Maybe there are more, but using ceiling function when calculating number of tiles is not correct either, so it is creating false positives.

Let's find a minimal example. Does `16x24x8w8-16-8` have this region count mismatch problem?

```
python topTenFromMNK.py "../16x24x8/input.txt" "../16x24x8" "_ss_c_rem_ana"
```

No issues, 9 regions in each.

Let's try `16x24x8w9-16-8`:

**Yes, there is an issue. We expected 9 regions for each core, but we got 5 for the last compute core:**

```
In the current json, there are 9 regions.
In the current json, there are 9 regions.
In the current json, there are 9 regions.
In the current json, there are 9 regions.
In the current json, there are 9 regions.
In the current json, there are 9 regions.
In the current json, there are 9 regions.
In the current json, there are 5 regions.
```

Our naive (and apparently incorrect) impression that the number of compute core tiles for ONE compute core WITH remainder tiles was

`ceil(M/m) * ceil(N/n) * ceil(K/k) = ceil(16/9) * ceil(24/16) * ceil(8/8) = ceil(1.77)*ceil(1.5)*ceil(1.0)=2*2*1= 4`

Then region count became `2*4 + 1 = 9`...

But the final compute core has 5 compute core tiles. WHY?

```
for i in 2 # M
	for j in 2 # N
		for h in 1# K
			WORK sent to 8 COMPUTE CORES
```

| Iters               | m_size  | n_size | k_size | 0       | 1       | 2       | 3       | 4       | 5       | 6       | 7    |
| ------------------- | ------- | ------ | ------ | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ---- |
| i = 0, j = 0, h = 0 | 9       | 16     | 8      | 2       | 1       | 1       | 1       | 1       | 1       | 1       | 1    |
| i = 0, j = 1, h = 0 | 9       | 8      | 8      | 2       | 1       | 1       | 1       | 1       | 1       | 1       | 1    |
| i = 1, j = 0, h = 0 | ***7*** | 16     | 8      | 1       | 1       | 1       | 1       | 1       | 1       | 1       |      |
| i = 1, j = 1, h = 0 | ***7*** | 8      | 8      | ***1*** | ***1*** | ***1*** | ***1*** | ***1*** | ***1*** | ***1*** |      |

From gemm.h:

```
  // Compute fraction of C rows every core computes
     uint32_t frac_m = args->m / core_num; // 7 / 8 = 0
     uint32_t rem_m = args->m % core_num;  // 7 % 8 = 7
     if (snrt_cluster_core_idx() < rem_m)  // cores 0-6  get a frac_m of 1, while core 7 keeps a frac_m of 0 (NOT EXECUTING)
     	frac_m++;

  // Invoke kernel for each core
     if (frac_m > 0) {
            kernel(args->setup_ssr, args->partition_banks, args->transa,
                   args->transb, frac_m, args->n, args->k, a, lda, args->b,
                   args->ldb, args->beta, c, ldc);
            snrt_fpu_fence();
     }
```



So I think the **number of compute cores running per cluster tile** is simple when `m_size is > 8`. Then each of the 8 cores gets a chunk of m_size, and remainder is spread among the 8 cores, not changing whether they execute or not.

The challenging situation is when `m_size < 8`. In this case, only `m_size` cores actually run for that cluster tile. So what we need to keep track of is how many cluster tiles use a `m_rem as the m_size`, vs. how many use `actual m as the m_size`.

- `(M / m) * ceil(N/n) * ceil(K/k)` times, the cluster tile uses `all 8` cores.
- `1 * ceil(N/n) * ceil(K/k)` times, the cluster tile uses `m_rem` cores. 

So in the case of `16x24x8w9-16-8`, 

- `(M / m) * ceil(N/n) * ceil(K/k) = (16/9) * ceil(24/16) * ceil(8/8) = 1 * 2 * 1 = 2` cluster tiles use all 8 cores.
- `1 * ceil(N/n) * ceil(K/k) = 1 * 2 * 1 = 2 ` cluster tiles use `m_rem = 7 cores`.
- AND we know that the cores that are skipped during the `m_rem` iterations are cores with an index ABOVE OR EQUAL TO `m_rem`.

| Cluster Tile Kind                                  | 0    | 1    | 2    | 3    | 4    | 5    | 6    | 7    |
| -------------------------------------------------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| `m = 9`                                            | 2    | 2    | 2    | 2    | 2    | 2    | 2    | 2    |
| `m_rem = 7`                                        | 2    | 2    | 2    | 2    | 2    | 2    | 2    | 0    |
| Total compute core <br />tiles processed           | 4    | 4    | 4    | 4    | 4    | 4    | 4    | 2    |
| Regions timed <br />= `2 * CC_tiles_processed + 1` | 9    | 9    | 9    | 9    | 9    | 9    | 9    | 5    |

Not ALL of the remainder tile points need to use this formula, because the asymmetry only arises when a remainder tile (at L1 level) **is less than 8**.

#### Region count given M, N, K, m, n, k, and compute core with index idx:

```
m_iters = (M / m) * ceil(N/n) * ceil(K/k)
m_rem_iters = 1 * ceil(N/n) * ceil(K/k)
rem_m = M % m
RegionsTimed(idx) = idx < rem_m ? 2*(m_iters + m_rem_iters) + 1 : 2 * m_iters + 1
```

# Why is the difference between e2e compute core time and the sum of all traced regions so LARGE for 8-8-32??

```
extractDataFromJsons.py: ATTN: only many_gemms.sh should call this script.
max e2e dma vs cc diff time is 18: 
[np.int64(18), np.int64(11), np.int64(10), np.int64(9), np.int64(6), np.int64(5), np.int64(4), np.int64(3)]

max sum region vs cc diff time is 2048: [np.int64(2048), np.int64(2048), np.int64(2048), np.int64(2048), np.int64(2048), np.int64(2048), np.int64(2048), np.int64(2048)] 

128 128 128 8 8 32 with build directory /repo/128x128x128-no-redundant-stores/128x128x128w8-8-32/build

```

It's off by 2048 because for each region it sums, it adds 1 cycle to account for zero-indexing. You should only account for zero-indexing once, but because we are summing up regions' "cycles" count, we accidentally account for zero-offset number of regions times or 1024 compute core tiles * 2 regions for each -> 2048 "error".
