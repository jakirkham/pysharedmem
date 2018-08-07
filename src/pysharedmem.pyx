cimport cpython
cimport cpython.mem
from cpython.mem cimport PyMem_Malloc, PyMem_Free

cimport pysharedmem

include "version.pxi"


cdef class cbuffer:
    cdef char[:] buf

    def __cinit__(self, Py_ssize_t length):
        self.buf = None

        if length <= 0:
            raise ValueError("length must be positive definite")

        cdef void* ptr = PyMem_Malloc(length * sizeof(char))
        if not ptr:
            raise MemoryError("unable to allocate buffer")

        self.buf = <char[:length]>ptr

    def __getbuffer__(self, Py_buffer *buffer, int flags):
        buffer.buf = &self.buf[0]
        buffer.obj = self
        buffer.len = len(self.buf)
        buffer.readonly = 0
        buffer.itemsize = self.buf.ndim
        buffer.format = "c"
        buffer.ndim = self.buf.ndim
        buffer.shape = self.buf.shape
        buffer.strides = self.buf.strides
        buffer.suboffsets = NULL
        buffer.internal = NULL

    def __releasebuffer__(self, Py_buffer *buffer):
        pass

    def __dealloc__(self):
        PyMem_Free(&self.buf[0])
        self.buf = None
