VERSION=2012082301
CXXFLAGS=-DVERSION="\"gr-scan $(VERSION)\"" -std=c++11 -Wall \
-I/usr/local/include -largp -lgnuradio-pmt -lgnuradio-runtime -lgnuradio-blocks -lgnuradio-fft -lgnuradio-filter -lgnuradio-osmosdr -lboost_system -O2 -Wno-unused-function

gr-scan: *.cpp *.hpp
	clang++ $(CXXFLAGS) -o gr-scan main.cpp
	g++-4.9 $(CXXFLAGS) -o gr-scan main.cpp
	g++ $(CXXFLAGS) -o gr-scan main.cpp

clean:
	rm -f gr-scan gr-scan.tar.gz

dist:
	mkdir gr-scan-$(VERSION)
	cp *.cpp *.hpp Makefile COPYING gr-scan-$(VERSION)
	tar -cf - gr-scan-$(VERSION) | gzip -9 -c - > gr-scan-$(VERSION).tar.gz
	rm -r gr-scan-$(VERSION)