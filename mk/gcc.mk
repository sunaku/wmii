DEBUGCFLAGS = \
	-g \
	-O1 \
	-fno-builtin \
	-fno-inline \
	-fno-omit-frame-pointer \
	-fno-optimize-sibling-calls \
	-fno-unroll-loops
CFLAGS += \
	-std=c99 \
	-pedantic \
	-pipe \
	-fno-strict-aliasing \
	-Wall \
	-Wimplicit \
	-Wmissing-prototypes \
	-Wno-comment \
	-Wno-missing-braces \
	-Wno-parentheses \
	-Wno-sign-compare \
	-Wno-switch \
	-Wno-unused-result \
	-Wpointer-arith \
	-Wreturn-type \
	-Wstrict-prototypes \
	-Wtrigraphs
MKDEP = cpp -M
SOCFLAGS += -fPIC

