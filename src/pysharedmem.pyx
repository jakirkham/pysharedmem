# cython: boundscheck = False
# cython: initializedcheck = False
# cython: nonecheck = False
# cython: wraparound = False


cimport cpython
cimport cpython.object
cimport cpython.tuple

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

    def __dealloc__(self):
        cdef char* ptr
        if self.buf is not None:
            ptr = &self.buf[0]
            self.buf = None
            PyMem_RawFree(<void*>ptr)


cdef class membuffer:
    cdef object buf

    def __init__(self, obj):
        self.buf = PyMemoryView_FromObject(obj)

    def __getbuffer__(self, Py_buffer *buffer, int flags):
        Py_buffer* self_buffer = PyMemoryView_GET_BUFFER(self.buf)

        buffer.buf = self_buffer
        buffer.obj = self
        buffer.len = self_buffer.len
        buffer.readonly = self_buffer.readonly
        buffer.itemsize = self_buffer.itemsize
        buffer.format = self_buffer.format
        buffer.ndim = self_buffer.ndim
        buffer.shape = self_buffer.shape
        buffer.strides = self_buffer.strides
        buffer.suboffsets = self_buffer.suboffsets
        buffer.internal = self_buffer.internal

    def __releasebuffer__(self, Py_buffer *buffer):
        pass

    def __reduce__(self):
        cdef bytes buf_bytes = self.buf.tobytes()

        cdef tuple result = PyTuple_Pack(1, <PyObject*>s)
        result = PyTuple_Pack(2, <PyObject*>frombuffer, <PyObject*>result)

        return result


def frombuffer(src):
    return membuffer(src)
