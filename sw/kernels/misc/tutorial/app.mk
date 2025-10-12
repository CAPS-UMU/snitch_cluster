APP              := tutorial
$(APP)_BUILD_DIR := $(SN_ROOT)/sw/kernels/misc/$(APP)/build
SRCS             := $(SN_ROOT)/sw/kernels/misc/$(APP)/src/$(APP).c
$(APP)_INCDIRS   := $(SN_ROOT)/sw/kernels/misc/$(APP)/data

include $(SN_ROOT)/sw/kernels/common.mk