# General Notes (Emily's gemm experiments branch)

Important Links:

- Basic Snitch Cluster Tutorial: https://pulp-platform.github.io/snitch_cluster/ug/tutorial.html#building-the-hardware

- Hardware Configuration JSON: [recent_snitch/snitch_cluster/cfg/default.json](recent_snitch/snitch_cluster/cfg/default.json)
- Verilator Makefile: [make/verilator.mk](make/verilator.mk)
- Luca's gemm experiment scripts: [experiments/frep/README.md](experiments/frep/README.md)
- Gemm experiment source code: [sw/kernels/blas/gemm/src/main.c](sw/kernels/blas/gemm/src/main.c)

How to inspect and remove docker images:

```
docker image ls
docker rmi <id of docker image you want to remove>
```

For example:

```
ghcr.io/pulp-platform/snitch_cluster-sw   main      3faf69063839   2 hours ago     4.28GB
ghcr.io/pulp-platform/snitch_cluster-hw   main      ca86047174bb   6 days ago      4.62GB
ghcr.io/opencompl/snitch-toolchain        4.0.0     774ff0eddbf9   2 weeks ago     3.2GB
hello-world                               latest    74cc54e27dc4   8 months ago    10.1kB
ghcr.io/opencompl/quidditch/toolchain     main      7e434df5cfea   13 months ago   880MB
ghcr.io/opencompl/snitch-toolchain        latest    ca514c5d7628   13 months ago   2.84GB
```

then to remove `sw` docker I did:

```
[hoppip@inf-155-54-205-141 recent_snitch]$ docker rmi -f 3faf69063839
Untagged: ghcr.io/pulp-platform/snitch_cluster-sw:main
Deleted: sha256:3faf6906383993fb4ddf24a34a35f635ee75facd8651ab10f09cc2018dc24cec
```

## Repo Setup

*Based on: https://pulp-platform.github.io/snitch_cluster/ug/getting_started.html*

```
git clone git@github.com:CAPS-UMU/snitch_cluster.git
cd snitch_cluster
git submodule update --init --recursive
```

Start docker:

```
docker run -it --entrypoint /bin/bash -v $PWD/snitch_cluster:/repo -w /repo ghcr.io/pulp-platform/snitch_cluster-sw:main
```

#### Build Hardware

```
make verilator
```

Do these "real path" errors matter?

```
root@3b3b7f278bde:/repo# make verilator
realpath: missing operand
Try 'realpath --help' for more information.
realpath: missing operand
Try 'realpath --help' for more information.
realpath: missing operand
Try 'realpath --help' for more information.
mkdir -p /repo/target/sim/build/work-vlt
...
```

#### Build Software

```
make DEBUG=ON sw -j
```

#### Run Example

```
cd test
snitch_cluster.vlt ../sw/kernels/misc/tutorial/build/tutorial.elf
```

## Daily Commands

Make sure you are *outside* the `snitch_cluster` directory!

```
docker run -it --entrypoint /bin/bash -v $PWD/snitch_cluster:/repo -w /repo ghcr.io/pulp-platform/snitch_cluster-sw:main
```



## Adding snitch application 

*Based on https://pulp-platform.github.io/snitch_cluster/ug/tutorial.html#developing-your-first-snitch-application*

- ```
  mkdir sw/kernels/misc/tutorial
  ```

- ```
  mkdir sw/kernels/misc/tutorial/src
  ```

  - add `tutorial.c` file
  
- ```
  mkdir sw/kernels/misc/tutorial/data
  ```

  - add `data.h` file
  
- Inside the tutorial folder, create `app.mk`with the following:
  
  ```
  APP              := tutorial
  $(APP)_BUILD_DIR := $(SN_ROOT)/sw/kernels/misc/$(APP)/build
  SRCS             := $(SN_ROOT)/sw/kernels/misc/$(APP)/src/$(APP).c
  $(APP)_INCDIRS   := $(SN_ROOT)/sw/kernels/misc/$(APP)/data
  
  include $(SN_ROOT)/sw/kernels/common.mk
  ```
  
- Inside `/snitch_cluster/make/sw.mk`:
  Add `SN_APPS += $(SN_ROOT)/sw/kernels/misc/tutorial`

- Now spin up docker and run `snitch_cluster.vlt sw/kernels/misc/tutorial/build/tutorial.elf`

## Running gemm examples

### My Own Verilator instructions

`/home/hoppip/recent_snitch/snitch_cluster/sw/kernels/blas/gemm/data/params.json`:

change double-buffer setting in params.json and then rebuild everything and see if the data.h inside of build folder is different?

ask luca how to run tests with verilator

try to run the gemm elf file with verilator

Run gemm example:

```
cd test
snitch_cluster.vlt ../sw/kernels/blas/gemm/build/gemm.elf
```

```
../sw/kernels/blas/gemm/scripts/verify.py snitch_cluster.vlt ../sw/kernels/blas/gemm/build/gemm.elf
```

```
echo $?
```

### automating the instructions

```
clear;bash many_gemms.sh 8x672x672wm-n-k_searchSpaceTop3.csv compile no no
```

```
clear;bash many_gemms.sh 56x56x56wm-n-k_searchSpaceTop3.csv compile no no
```

```
clear;time bash many_gemms.sh 56x56x56wm-n-k_searchSpaceTop3.csv compile run no > 56x56x56-output.txt
```



56x56x56wm-n-k_searchSpaceTop3.csv

`/home/hoppip/recent_snitch/snitch_cluster/sw/kernels/blas/gemm/build-yodel/gemm.elf`

`/home/hoppip/recent_snitch/snitch_cluster/8x672x672wm-n-k_searchSpaceTop3.csv`

```
../sw/kernels/blas/gemm/scripts/verify.py snitch_cluster.vlt ../sw/kernels/blas/gemm/build/gemm.elf
cd sw/kernels/blas/gemm/build-yodel
../scripts/verify.py snitch_cluster.vlt gemm.elf > verify-output.txt
echo $?
cd ../../../../../
clear;bash many_gemms.sh examplewm-n-k_searchSpace.csv no no extract
```



example gen_trace.py call:

```
/repo/util/trace/gen_trace.py /repo/test/logs/trace_hart_00000.dasm --mc-exec /tools/riscv-llvm/bin/llvm-mc --mc-flags "-disassemble -mcpu=snitch" --dma-trace /repo/test/dma_trace_00000_00000.log --dump-hart-perf /repo/test/logs/hart_00000_perf.json --dump-dma-perf /repo/test/logs/dma_00000_perf.json -o /repo/test/logs/trace_hart_00000.txt

```

```
python extractKernelTimeFromJsons.py "32x16x16w32-16-16" "sw/kernels/blas/gemm/32x16x16w32-16-16/logs"
python extractKernelTimeFromJsons.py "exp" "sw/kernels/blas/gemm/build-yodel/logs"
clear;bash many_gemms.sh examplewm-n-k_searchSpace.csv
python prepareParams.py "sw/kernels/blas/gemm/data/params.json" 32 16 16 4 2 2
python extractKernelTimeFromJsons.py "32x16x16w32-16-16" "sw/kernels/blas/gemm/32x16x16w32-16-16/logs"
python extractKernelTimeFromJsons.py "32x16x16w8-8-8" "sw/kernels/blas/gemm/32x16x16w8-8-8/logs"
python extractKernelTimeFromJsons.py "32x16x16w16-8-8" "sw/kernels/blas/gemm/32x16x16w16-8-8/logs"
```

/home/hoppip/recent_snitch/snitch_cluster/sw/kernels/blas/gemm/32x16x16w32-16-16

### QuestaSim instructions

```
make clean-vsim
make vsim DEBUG=ON -j
...
```

see [experiments/frep/README.md](experiments/frep/README.md) for details.

```
../../../../../../../../../sw/blas/gemm/scripts/verify.py 
../../../../../hw/zonl48dobu/bin/snitch_cluster.vsim 
../../../../../build/zonl48dobu/24/32/8/gemm.elf
```



## old notes below



docker run --rm -ti --volume $PWD/snitch_cluster:/repo ghcr.io/pulp-platform/snitch_cluster-sw:main

#### will these help as reference?

```
$ git clone --recursive https://github.com/opencompl/riscv-paper-experiments.git
$ docker run --rm -ti --volume $PWD/riscv-paper-experiments:/src ghcr.io/opencompl/snitch-toolchain:latest bash
$ cd /src
$ make
```

or in one shot with

```
$ git clone --recursive https://github.com/opencompl/riscv-paper-experiments.git
$ docker run -ti --volume ${PWD}/riscv-paper-experiments:/src ghcr.io/opencompl/snitch-toolchain:latest bash -c "make -C /src"
```



## Repo Setup

*Based on: https://pulp-platform.github.io/snitch_cluster/ug/getting_started.html*

- `git clone git@github.com:CAPS-UMU/snitch_cluster.git`
- `cd snitch_cluster`

- `git submodule update --init --recursive`
- `docker build -t ghcr.io/pulp-platform/snitch_cluster-sw:main -f util/container/Dockerfile .`

These failed:

- `cd ..; docker run -it --entrypoint /bin/bash -v snitch_cluster:/repo -w /repo ghcr.io/pulp-platform/snitch_cluster-sw:main`
- `make verilator` (caused errors)
- `make DEBUG=ON sw -j` (caused errors)
- 

Trying again with this command (selecting `hw` docker instead of `sw` docker):

- `cd ..; docker run -it --entrypoint /bin/bash -v snitch_cluster:/repo -w /repo ghcr.io/pulp-platform/snitch_cluster-hw:main`
- `make verilator`
- `make DEBUG=ON sw -j` (said there was nothing to make)

Both docker looks commands seem to work okay now. In general, I enter the `sw` docker from now on...

## Daily Commands

- `cd snitch_cluster`
- `cd ..; docker run -it --entrypoint /bin/bash -v snitch_cluster:/repo -w /repo ghcr.io/pulp-platform/snitch_cluster-sw:main`
- `make DEBUG=ON sw -j`

## Running Examples

- `ls sw/kernels/blas/gemm/build/`
- `sw/kernels/blas/gemm/build/gemm.elf`
- Let's try `snitch_cluster.vlt sw/kernels/blas/gemm/build/gemm.elf`

This seemed to work okay:

```
cd test
snitch_cluster.vlt ../sw/kernels/blas/gemm/build/gemm.elf
```



we tried:

```
snitch_cluster.vlt sw/kernels/blas/axpy/build/axpy.elf
```

and it seemed to work okay.

## Adding snitch application 

*Based on https://pulp-platform.github.io/snitch_cluster/ug/tutorial.html#developing-your-first-snitch-application*

- ```
  mkdir sw/kernels/misc/tutorial
  ```

- ```
  mkdir sw/kernels/misc/tutorial/src
  ```

- Inside `/snitch_cluster/make/sw.mk`:
  Add `SN_APPS += $(SN_ROOT)/sw/kernels/misc/tutorial`

- Now spin up docker and run `snitch_cluster.vlt sw/kernels/misc/tutorial/build/tutorial.elf`

## Trouble Shooting

1. ```
   cd ..; docker run -it --entrypoint /bin/bash -v snitch_cluster:/repo -w /repo ghcr.io/pulp-platform/snitch_cluster-sw:main
   make verilator
   ```

   Error:
   ```
   make verilator
   realpath: missing operand
   Try 'realpath --help' for more information.
   realpath: missing operand
   Try 'realpath --help' for more information.
   realpath: missing operand
   Try 'realpath --help' for more information.
   mkdir -p /repo/target/sim/build/work-vlt
   bender script verilator -t rtl -t snitch_cluster -t snitch_cluster_wrapper -t verilator -DASSERTS_OFF > /repo/target/sim/build/work-vlt/testharness.f
       Checkout common_verification (https://github.com/pulp-platform/common_verification.git)
        Cloning common_verification (https://github.com/pulp-platform/common_verification.git)
       Checkout tech_cells_generic (https://github.com/pulp-platform/tech_cells_generic)
        Cloning tech_cells_generic (https://github.com/pulp-platform/tech_cells_generic)
       Checkout common_cells (https://github.com/pulp-platform/common_cells.git)
        Cloning common_cells (https://github.com/pulp-platform/common_cells.git)
       Checkout apb (https://github.com/pulp-platform/apb.git)
        Cloning apb (https://github.com/pulp-platform/apb.git)
       Checkout axi (https://github.com/colluca/axi.git)
        Cloning axi (https://github.com/colluca/axi.git)
       Checkout axi_stream (https://github.com/pulp-platform/axi_stream.git)
        Cloning axi_stream (https://github.com/pulp-platform/axi_stream.git)
       Checkout fpu_div_sqrt_mvp (https://github.com/pulp-platform/fpu_div_sqrt_mvp.git)
        Cloning fpu_div_sqrt_mvp (https://github.com/pulp-platform/fpu_div_sqrt_mvp.git)
       Checkout obi (https://github.com/pulp-platform/obi.git)
        Cloning obi (https://github.com/pulp-platform/obi.git)
       Checkout register_interface (https://github.com/pulp-platform/register_interface.git)
        Cloning register_interface (https://github.com/pulp-platform/register_interface.git)
       Checkout scm (https://github.com/pulp-platform/scm.git)
        Cloning scm (https://github.com/pulp-platform/scm.git)
       Checkout axi_riscv_atomics (https://github.com/pulp-platform/axi_riscv_atomics)
        Cloning axi_riscv_atomics (https://github.com/pulp-platform/axi_riscv_atomics)
       Checkout cluster_icache (https://github.com/pulp-platform/cluster_icache.git)
        Cloning cluster_icache (https://github.com/pulp-platform/cluster_icache.git)
       Checkout fpnew (https://github.com/pulp-platform/cvfpu.git)
        Cloning fpnew (https://github.com/pulp-platform/cvfpu.git)
       Checkout idma (https://github.com/pulp-platform/iDMA.git)
        Cloning idma (https://github.com/pulp-platform/iDMA.git)
       Checkout riscv-dbg (https://github.com/pulp-platform/riscv-dbg)
        Cloning riscv-dbg (https://github.com/pulp-platform/riscv-dbg)
   Using default config file: /repo/cfg/default.json
   mkdir -p /repo/hw/generated
   [CLUSTERGEN] Generate /repo/hw/generated/snitch_cluster_wrapper.sv
   /repo/util/clustergen/clustergen.py -c /repo/cfg/lru.json -o /repo/hw/generated/snitch_cluster_wrapper.sv --template /repo/hw/snitch_cluster/src/snitch_cluster_wrapper.sv.tpl
   [CLUSTERGEN] Generate /repo/hw/generated/snitch_cluster_pkg.sv
   /repo/util/clustergen/clustergen.py -c /repo/cfg/lru.json -o /repo/hw/generated/snitch_cluster_pkg.sv --template /repo/hw/snitch_cluster/src/snitch_cluster_pkg.sv.tpl
   [CLUSTERGEN] Generate /repo/hw/generated/snitch_cluster.rdl
   /repo/util/clustergen/clustergen.py -c /repo/cfg/lru.json -o /repo/hw/generated/snitch_cluster.rdl --template /repo/hw/snitch_cluster/src/snitch_cluster.rdl.tpl
   [peakrdl] Generating /repo/hw/generated/snitch_cluster_addrmap.svh
   peakrdl raw-header /repo/hw/generated/snitch_cluster.rdl -o /repo/hw/generated/snitch_cluster_addrmap.svh --format svh -I /repo/hw/snitch_cluster/src/snitch_cluster_peripheral
   /tools/riscv-llvm/bin/clang -mabi=ilp32d -march=rv32imafd -static -nostartfiles -fuse-ld=/tools/riscv-llvm/bin/ld.lld -L/repo/sw/runtime -T/repo/hw/bootrom/bootrom.ld /repo/hw/bootrom/bootrom.S -o /repo/hw/bootrom/bootrom.elf
   /tools/riscv-llvm/bin/llvm-objdump -d /repo/hw/bootrom/bootrom.elf > /repo/hw/bootrom/bootrom.dump
   /tools/riscv-llvm/bin/llvm-objcopy -j .text -O binary /repo/hw/bootrom/bootrom.elf /repo/hw/bootrom/bootrom.bin
   /repo/util/clustergen/gen_bootrom.py --sv-module snitch_bootrom /repo/hw/bootrom/bootrom.bin > /repo/hw/bootrom/snitch_bootrom.sv
   verilator -f /repo/target/sim/build/work-vlt/testharness.f --Mdir /repo/target/sim/build/work-vlt --MMD -E --top-module testharness > /dev/null
   /bin/sh: 1: verilator: not found
   [CLUSTERGEN] Generate /repo/hw/generated/bootdata.cc
   /repo/util/clustergen/clustergen.py -c /repo/cfg/lru.json -o /repo/hw/generated/bootdata.cc --template /repo/hw/snitch_cluster/test/bootdata.cc.tpl
   mkdir -p /repo/target/sim/build/work-vlt/riscv-isa-sim/
   wget -O /repo/target/sim/build/work-vlt/riscv-isa-sim//35d50bc40e59ea1d5566fbd3d9226023821b1bb6 https://github.com/riscv/riscv-isa-sim/tarball/35d50bc40e59ea1d5566fbd3d9226023821b1bb6
   --2025-09-29 12:50:39--  https://github.com/riscv/riscv-isa-sim/tarball/35d50bc40e59ea1d5566fbd3d9226023821b1bb6
   Resolving github.com (github.com)... 140.82.121.3
   Connecting to github.com (github.com)|140.82.121.3|:443... connected.
   HTTP request sent, awaiting response... 301 Moved Permanently
   Location: https://github.com/riscv-software-src/riscv-isa-sim/tarball/35d50bc40e59ea1d5566fbd3d9226023821b1bb6 [following]
   --2025-09-29 12:50:39--  https://github.com/riscv-software-src/riscv-isa-sim/tarball/35d50bc40e59ea1d5566fbd3d9226023821b1bb6
   Reusing existing connection to github.com:443.
   HTTP request sent, awaiting response... 302 Found
   Location: https://codeload.github.com/riscv-software-src/riscv-isa-sim/legacy.tar.gz/35d50bc40e59ea1d5566fbd3d9226023821b1bb6 [following]
   --2025-09-29 12:50:40--  https://codeload.github.com/riscv-software-src/riscv-isa-sim/legacy.tar.gz/35d50bc40e59ea1d5566fbd3d9226023821b1bb6
   Resolving codeload.github.com (codeload.github.com)... 140.82.121.10
   Connecting to codeload.github.com (codeload.github.com)|140.82.121.10|:443... connected.
   HTTP request sent, awaiting response... 200 OK
   Length: unspecified [application/x-gzip]
   Saving to: '/repo/target/sim/build/work-vlt/riscv-isa-sim//35d50bc40e59ea1d5566fbd3d9226023821b1bb6'
   
   /repo/target/sim/build/work-     [  <=>                                          ] 381.45K  1.49MB/s    in 0.3s    
   
   2025-09-29 12:50:40 (1.49 MB/s) - '/repo/target/sim/build/work-vlt/riscv-isa-sim//35d50bc40e59ea1d5566fbd3d9226023821b1bb6' saved [390604]
   
   tar xfm /repo/target/sim/build/work-vlt/riscv-isa-sim/35d50bc40e59ea1d5566fbd3d9226023821b1bb6 --strip-components=1 -C /repo/target/sim/build/work-vlt/riscv-isa-sim/
   patch /repo/target/sim/build/work-vlt/riscv-isa-sim/fesvr/context.h < /repo/target/sim/patches/context.h.diff
   patching file /repo/target/sim/build/work-vlt/riscv-isa-sim/fesvr/context.h
   touch /repo/target/sim/build/work-vlt/riscv-isa-sim/35d50bc40e59ea1d5566fbd3d9226023821b1bb6_unzip
   cd /repo/target/sim/build/work-vlt/riscv-isa-sim// && ./configure --prefix `pwd` \
           CC=cc CXX=g++ CFLAGS="" CXXFLAGS="" LDFLAGS=""
   checking build system type... x86_64-pc-linux-gnu
   checking host system type... x86_64-pc-linux-gnu
   checking for gcc... cc
   checking whether the C compiler works... yes
   checking for C compiler default output file name... a.out
   checking for suffix of executables... 
   checking whether we are cross compiling... no
   checking for suffix of object files... o
   checking whether we are using the GNU C compiler... yes
   checking whether cc accepts -g... yes
   checking for cc option to accept ISO C89... none needed
   checking whether we are using the GNU C++ compiler... yes
   checking whether g++ accepts -g... yes
   checking for ar... ar
   checking for ranlib... ranlib
   checking for dtc... no
   configure: error: device-tree-compiler not found
   make: *** [/repo/make/verilator.mk:62: /repo/target/sim/build/work-vlt/lib/libfesvr.a] Error 1
   root@54a13b4e7111:/repo# 
   
   
   ```

   

2. ```
   root@54a13b4e7111:/repo# make DEBUG=ON sw -j
   realpath: missing operand
   Try 'realpath --help' for more information.
   realpath: missing operand
   Try 'realpath --help' for more information.
   realpath: missing operand
   Try 'realpath --help' for more information.
   make: Nothing to be done for 'sw'.
   
   ```

3. 