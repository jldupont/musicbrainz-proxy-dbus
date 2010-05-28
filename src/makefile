#
# @author Jean-Lou Dupont
# http://www.systemical.com/
#
PRJ=musicbrainz_proxy_dbus

PYTHON=`which python`
BASE=/usr/lib/musicbrainz-proxy-dbus

all:
	@echo "make install"
	@echo "make clean"
	@echo "make buildsrc"

clean:
	@rm -rf $(DESTDIR)$(BASE)/*.pyc
		
install:
	@install -d $(DESTDIR)$(BASE)

	
	
buildsrc:
	debuild -S