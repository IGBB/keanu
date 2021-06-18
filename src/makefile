##
# ddrad viz
#
# @file
# @version 0.1

CXX = g++
CXXFLAGS = -Wall -O3 -std=c++11 -fopenmp
PROG=keanu-bubble keanu-graph

.PHONY: all clean

all: $(PROG)

clean:
	$(MAKE) $(MFLAGS) -C kraken2 clean
	rm -f *.o $(PROG)

kraken2/%:
	$(MAKE) $(MFLAGS) -C kraken2 $*

main.graph.o: main.graph.cc


bubble.html.h : bubble.html
bubble.style.h : bubble.css
bubble.script.h : bubble.js

bubble.html.h bubble.style.h bubble.script.h :
	xxd -i $< | sed 's/};/, 0x00};/' > $@

main.bubble.o: main.bubble.cc bubble.html.h bubble.style.h bubble.script.h

keanu-%: main.%.o kraken2/taxonomy.o kraken2/mmap_file.o
	$(CXX) $(CXXFLAGS) -o $@ $^
# end
