INSTALL ?= install -p
PYTHON ?= python
PYTHON_UNITTEST_MODULE ?= unittest

UNITDIR=$(shell pkg-config systemd --variable systemdsystemunitdir)
PYTHON_LIBDIR=$(shell $(PYTHON) -c \
    "from distutils import sysconfig; print(sysconfig.get_python_lib())")
PLUGINDIR=$(PYTHON_LIBDIR)/dnf-plugins

install:
	$(INSTALL) -d $(DESTDIR)$(UNITDIR)
	$(INSTALL) -m644 fedup-system-upgrade.service $(DESTDIR)$(UNITDIR)
	$(INSTALL) -d $(DESTDIR)$(PLUGINDIR)
	$(INSTALL) -m644 fedup.py $(DESTDIR)$(PLUGINDIR)
	systemctl --no-reload --root=$(DESTDIR) enable fedup-system-upgrade.service

clean:
	rm -rf *.pyc __pycache__

check:
	$(PYTHON) -m $(PYTHON_UNITTEST_MODULE) test_fedup

.PHONY: install clean check
