#!/usr/bin/env python3
# Copyright 2023 ETH Zurich and University of Bologna.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0
#
# Luca Colagrande <colluca@iis.ee.ethz.ch>

import numpy as np
import sys
from datagen import GemmDataGen

import importlib.util
import sys
# we want to use a customized argument parser for the Verifier, so we aren't importing from venv.

import pathlib
spec = importlib.util.spec_from_file_location("SnitchSim.verif_utils", f"{pathlib.Path(__file__).parent.resolve()}/../../../../../util/sim/verif_utils.py")
verif_utils = importlib.util.module_from_spec(spec)
sys.modules["SnitchSim.verif_utils"] = verif_utils
spec.loader.exec_module(verif_utils)
#verif_utils.MyClass()
#/home/hoppip/recent_snitch/snitch_cluster/sw/kernels/blas/matmul_padded/scripts/verify.py
#../../../../../../util/sim/verif_utils.py
# spec = importlib.util.spec_from_file_location("SnitchSim.verif_utils", "/path/to/file.py")
# customVerifier = importlib.util.module_from_spec(spec)
# sys.modules["SnitchSim.verif_utils"] = foo
# spec.loader.exec_module(foo)
# foo.MyClass()

# from SnitchSim.verif_utils import Verifier
from snitch.util.sim.data_utils import ctype_from_precision_t


class GemmVerifier(verif_utils.Verifier):

    OUTPUT_UIDS = ['c']
    ERR_THRESHOLD = {
        1: 1e-4,
        2: 5e-1,
        4: 1e-3,
        8: 1e-3
    }

    def __init__(self):
        super().__init__()
        self.prec = self.get_input_from_symbol('prec', 'uint32_t')[0]

    def get_actual_results_unpadded(self):
        M = self.get_input_from_symbol('m_unpadded', 'uint32_t')[0]
        N = self.get_input_from_symbol('n_unpadded', 'uint32_t')[0]
        c = self.get_output_from_symbol(self.OUTPUT_UIDS[0], ctype_from_precision_t(self.prec)).flatten()[0:int(M*N)]
        return c

    def get_expected_results_unpadded(self):
        M = self.get_input_from_symbol('m_unpadded', 'uint32_t')[0]
        N = self.get_input_from_symbol('n_unpadded', 'uint32_t')[0]
        K = self.get_input_from_symbol('k_unpadded', 'uint32_t')[0]
        a = self.get_input_from_symbol('a', ctype_from_precision_t(self.prec)).flatten()[0:M*K]
        b = self.get_input_from_symbol('b', ctype_from_precision_t(self.prec)).flatten()[0:K*N]
        c = self.get_input_from_symbol('c', ctype_from_precision_t(self.prec)).flatten()[0:M*N]
        m = M
        n = N
        k = K
        beta = self.get_input_from_symbol('beta', 'uint32_t')[0]
        transb = self.get_input_from_symbol('transb', 'uint32_t')[0]

        a = np.reshape(a, (m, k))
        if transb:
            b = np.reshape(b, (n, k))
            b = b.transpose()
        else:
            b = np.reshape(b, (k, n))
        c = np.reshape(c, (m, n))

        return GemmDataGen().exact_golden_model(1, a, b, beta, c).flatten(), a, b

    def check_results(self, *args):
        actual=self.get_actual_results_unpadded()
        expected, a, b=self.get_expected_results_unpadded()
        np.reshape(actual,(8,32))
        np.reshape(a,(8,32))
        np.reshape(b,(8,32))
        print(a)
        print(b)
        print(actual)
        print(expected)
        return super().check_results(actual,expected, rtol=self.ERR_THRESHOLD[self.prec])


if __name__ == "__main__":
    sys.exit(GemmVerifier().main())
