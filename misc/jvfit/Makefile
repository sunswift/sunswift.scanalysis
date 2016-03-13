# Project: JVFit
# Makefile created by Dev-C++ 4.9.9.0

CPP  = g++
CC   = gcc
DEBUG = #-D__DEBUG__ -g3
OPTIM = -O2 -fexpensive-optimizations
WARN = -Wall

CPPFLAGS = $(WARN) $(OPTIM) $(DEBUG) 
#TODO: check these CFLAGS. You probably don't need them all
CFLAGS = $(WARN) $(OPTIM) $(DEBUG) -mrtd 

OBJS  = leastsquares.o twodiodemodel.o quadsmooth.o decompose.o jvfit.o jvcalc.o
BIN_OBJS = $(OBJS) main.o jvfitdll.o
BIN  = jvfit

.PHONY: all all-before all-after clean clean-custom

all: all-before $(BIN) all-after $(DLL_NAME)

bin: $(BIN)

clean: clean-custom
	rm -f $(OBJS) $(DLL_OBJS) $(BIN_OBJS) $(BIN) $(DLL_NAME) $(DLL_EXP_DEF) $(DLL_EXP_LIB)

$(BIN): $(BIN_OBJS) 
	$(CPP) $(BIN_OBJS) -o $(BIN) $(LIBS)

%.o: %.c
	$(CC) $(CFLAGS) $(DLL_CFLAGS) -c $< -o $@

%.o: %.cpp %.h
	$(CPP) $(CPPFLAGS) -c $< -o $@

