all:
	@(cd cheapglk && make)

clean:
	@(cd cheapglk && make clean)

check:
	@python3 run_tests.py
