LIB_DIR = lib

default: pyexamples

pyexamples: setup.py pyexamples.pyx $(LIB_DIR)/libexamples.a
	python setup.py build_ext --inplace && rm -f pyexamples.c && rm -Rf build
	cp pyexamples.cpython-38-arm-linux-gnueabihf.so ~/.local/lib/python3.8/site-packages/pyexamples
	#cp pyexamples.cpython-37m-arm-linux-gnueabihf.so ~/.local/lib/python3.8/site-packages/pyexamples

$(LIB_DIR)/libexamples.a:
	make -C $(LIB_DIR) libexamples.a

clean:
	rm *.so *.o *.a


