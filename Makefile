img/architecture.png: architecture.gv
	mkdir -p img
	dot -T png -o $@ $<
