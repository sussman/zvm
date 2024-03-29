# Unix Makefile for CheapGlk library

# This generates a shared library, libcheapglk.so.
#
# The file cgunigen.c was generated by the casemap.py script, but
# that step isn't in the Makefile -- you don't have to re-generate it.
# It's based on Unicode character data, which is not platform-dependent.

# Pick a C compiler.
# CC = cc
CC = gcc -ansi

GLKLIB_SHARED = libcheapglk.so
OSFLAG :=
DEL := rm -f
ifeq ($(OS),Windows_NT)
OSFLAG := -D WIN32
GLKLIB_SHARED = libcheapglk.dll
DEL := del /F
endif

OPTIONS = -g -Wall -fPIC
CFLAGS = $(OPTIONS) $(INCLUDEDIRS) $(OSFLAG)

CHEAPGLK_OBJS =  \
  cgfref.o cggestal.o cgmisc.o cgstream.o cgstyle.o cgwindow.o cgschan.o \
  cgdate.o cgunicod.o main.o gi_dispa.o gi_blorb.o gi_debug.o cgblorb.o \
  glkstart.o

CHEAPGLK_HEADERS = cheapglk.h gi_dispa.h gi_debug.h

all: $(GLKLIB_SHARED)

cgunicod.o: cgunigen.c

$(GLKLIB_SHARED): $(CHEAPGLK_OBJS)
	gcc -shared -o $(GLKLIB_SHARED) $(CHEAPGLK_OBJS)

$(CHEAPGLK_OBJS): glk.h $(CHEAPGLK_HEADERS)

clean:
	$(DEL) *~ *.o $(GLKLIB_SHARED)