make:
	[ -d "exitmap" ] || git clone git@github.com:NullHypothesis/exitmap.git
	[ -d "exitmap" ] && python2 -m pip install -r exitmap/requirements.txt
	[ -d "exitmap" ] && [ -f "exitmap/src/modules/timeddns.py" ] || ln src/timeddns.py exitmap/src/modules/timeddns.py
	[ -d "exitmap" ] && [ -f "exitmap/src/modules/theoracle.conf" ] || ln theoracle.conf exitmap/src/modules/theoracle.conf
	[ -d "logs" ] || mkdir logs
	[ -d "results" ] || mkdir results
	[ -d "tor_cache" ] || mkdir tor_cache
	python3 -m pip install stem pysocks seaborn
	python2 -m pip install stem
	
clean:
	@echo "THIS WILL REMOVE ALL RESULTS, LOGS AND CACHE IN 5 SECONDS! Press Ctrl + C to cancel."
	sleep 5
	rm -rf exitmap_scans/*
	rm -rf tor_cache/*
	rm -f logs/*
	rm -rf results/*