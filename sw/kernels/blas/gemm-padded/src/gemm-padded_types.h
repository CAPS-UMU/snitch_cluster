// Copyright 2025 ETH Zurich and University of Bologna.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0
//
//         Adapted gemm_types.h for padding.
//
// Author: Luca Colagrande <colluca@iis.ee.ethz.ch>
//         Emily Sillars <emily.sillars@um.es>

#include <stdint.h>

/**
 * 
 * @struct gemm_padded_args_t
 * @brief Structure to hold arguments for a padded GEMM operation on Snitch-based
 *        multiple-cluster architectures.
 *
 * This structure extends the gemm_padded_args_t structure to support
 * padding in the m, n, and k dimensions.
 *
 * @note Refer to `gemm_args_t` for a description of all other parameters.
 */
typedef struct {
    uint32_t m_tiles;
    uint32_t n_tiles;
    uint32_t k_tiles;
    uint32_t parallelize_m;
    uint32_t parallelize_k;
    uint32_t load_a;
    uint32_t load_b;
    uint32_t load_c;
    uint32_t double_buffer;
    gemm_fp_t gemm_fp;
    uint32_t prec;
    uint32_t setup_ssr;
    uint32_t partition_banks;
    // BLAS args
    uint32_t transa;
    uint32_t transb;
    uint32_t m;
    uint32_t n;
    uint32_t k;
    double alpha;
    void* a;
    uint32_t lda;
    void* b;
    uint32_t ldb;
    uint32_t beta;
    void* c;
    uint32_t ldc;
    uint32_t m_unpad;
    uint32_t n_unpad;
    uint32_t k_unpad;
} gemm_padded_args_t;