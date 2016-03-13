.PHONY: doc

doc:
	epydoc --config pydoc.cfg

clean:
	find . | grep ".pyc" | xargs rm -f
	find . | grep "~" | xargs rm -f