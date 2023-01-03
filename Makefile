ifeq ($(PREFIX),)
	PREFIX := ~/.local
	# /usr/local
endif

install: audiodemod.sh db_search.py kiss_csv.py process_frames.py process_simple.py satnogs_fetch_audio.py
	install -d $(DESTDIR)$(PREFIX)/bin/
	install -m 755 audiodemod.sh $(DESTDIR)$(PREFIX)/bin/
	install -m 755 db_search.py $(DESTDIR)$(PREFIX)/bin/
	install -m 755 kiss_csv.py $(DESTDIR)$(PREFIX)/bin/
	install -m 755 process_frames.py $(DESTDIR)$(PREFIX)/bin/
	install -m 755 process_simple.py $(DESTDIR)$(PREFIX)/bin/
	install -m 755 satnogs_fetch_audio.py $(DESTDIR)$(PREFIX)/bin/

