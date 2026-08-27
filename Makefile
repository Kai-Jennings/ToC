COMPILER = g++
FLAGS = -std=c++23

default:
	$(COMPILER) $(FLAGS) main.cpp -o app.bin > makelog 2>&1