# cython: boundscheck = False
# cython: initializedcheck = False
# cython: nonecheck = False
# cython: wraparound = False


cimport cpython
cimport cpython.buffer
cimport cpython.bytes
cimport cpython.object
cimport cpython.tuple

from cpython.buffer cimport PyBuffer_ToContiguous
from cpython.bytes cimport PyBytes_FromStringAndSize
from cpython.object cimport PyObject
from cpython.tuple cimport PyTuple_Pack

cimport pysharedmem

include "version.pxi"


cdef extern from "Python.h":
    IF PY_VERSION_HEX >= 0x03040000:
        void* PyMem_RawMalloc(size_t n) nogil
        void PyMem_RawFree(void *p) nogil
    ELSE:
        void* PyMem_RawMalloc "PyMem_Malloc" (size_t n) nogil
        void PyMem_RawFree "PyMem_Free" (void *p) nogil

cdef extern from "Python.h":
    object PyMemoryView_FromObject(object)
    Py_buffer* PyMemoryView_GET_BUFFER(object)


cdef class cbuffer:
    cdef char[::1] buf

    def __cinit__(self, Py_ssize_t length):
        self.buf = None

        if length <= 0:
            raise ValueError("length must be positive definite")

        cdef char* ptr = <char*>PyMem_RawMalloc(length * sizeof(char))
        if not ptr:
            raise MemoryError("unable to allocate buffer")

        self.buf = <char[:length]>ptr

    def __getbuffer__(self, Py_buffer *buffer, int flags):
        buffer.buf = &self.buf[0]
        buffer.obj = self
        buffer.len = len(self.buf)
        buffer.readonly = 0
        buffer.itemsize = self.buf.itemsize
        buffer.format = "c"
        buffer.ndim = self.buf.ndim
        buffer.shape = self.buf.shape
        buffer.strides = self.buf.strides
        buffer.suboffsets = NULL
        buffer.internal = NULL

    def __releasebuffer__(self, Py_buffer *buffer):
        pass

    def __reduce__(self):
        cdef bytes buf_bytes = PyBytes_FromStringAndSize(
            &self.buf[0], len(self.buf)
        )

        cdef tuple result = PyTuple_Pack(1, <PyObject*>buf_bytes)
        result = PyTuple_Pack(2, <PyObject*>frombuffer, <PyObject*>result)

        return result

    def __dealloc__(self):
        cdef char* ptr
        if self.buf is not None:
            ptr = &self.buf[0]
            self.buf = None
            PyMem_RawFree(<void*>ptr)


def frombuffer(src):
    src = PyMemoryView_FromObject(src)
    cdef Py_buffer* src_buf = PyMemoryView_GET_BUFFER(src)

    cdef cbuffer dest = cbuffer(src_buf.len)
    cdef char* dest_ptr = &dest.buf[0]

    PyBuffer_ToContiguous(<void*>dest_ptr, src_buf, src_buf.len, 'C')

    return dest
