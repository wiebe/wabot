clean: docclean
	find . -name "*.py[co]" -exec rm -f {} \;

doc: docclean
	mkdir -p ./doc/
	epydoc -n LuckyBot -vo ./doc/ --html luckybot

docclean:
	rm -rf ./doc/*
