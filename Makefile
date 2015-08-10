VERSION = 0.0.1

LN ?= ln
INSTALL ?= install -p
PYTHON ?= python
PYTHON_UNITTEST_MODULE ?= unittest

PYTHON_VERSION=$(shell $(PYTHON) -c \
    "import sys; print(sys.version_info.major)")
PYTHON_LIBDIR=$(shell $(PYTHON) -c \
    "from distutils import sysconfig; print(sysconfig.get_python_lib())")
PLUGINDIR=$(PYTHON_LIBDIR)/dnf-plugins

UNITDIR=$(shell pkg-config systemd --variable systemdsystemunitdir)
TARGET_WANTSDIR=$(UNITDIR)/system-update.target.wants

LOCALEDIR ?= /usr/share/locale
TEXTDOMAIN = dnf-plugin-system-upgrade
LANGUAGES = $(patsubst po/%.po,%,$(wildcard po/*.po))
MSGFILES = $(patsubst %,po/%.mo,$(LANGUAGES))

SERVICE = dnf-system-upgrade.service
PLUGIN = system_upgrade.py

build: $(MSGFILES)

po/$(TEXTDOMAIN).pot: $(PLUGIN)
	xgettext -c -s -d $(TEXTDOMAIN) -o $@ $?

po/%.mo : po/%.po
	msgfmt $< -o $@

install: $(PLUGIN) $(SERVICE) $(MSGFILES)
	$(INSTALL) -d $(DESTDIR)$(PLUGINDIR)
	$(INSTALL) -m644 $(PLUGIN) $(DESTDIR)$(PLUGINDIR)
	$(PYTHON) -m py_compile $(DESTDIR)$(PLUGINDIR)/$(PLUGIN)
	$(PYTHON) -O -m py_compile $(DESTDIR)$(PLUGINDIR)/$(PLUGIN)
	$(INSTALL) -d $(DESTDIR)$(UNITDIR)
	$(INSTALL) -d $(DESTDIR)$(TARGET_WANTSDIR)
	$(INSTALL) -m644 $(SERVICE) $(DESTDIR)$(UNITDIR)
	$(LN) -sf ../$(SERVICE) $(DESTDIR)$(TARGET_WANTSDIR)/$(SERVICE)
	for lang in $(LANGUAGES); do \
	  langdir=$(DESTDIR)$(LOCALEDIR)/$${lang}/LC_MESSAGES; \
	  $(INSTALL) -d $$langdir; \
	  $(INSTALL) po/$${lang}.mo $${langdir}/$(TEXTDOMAIN).mo;\
	done

clean:
	rm -rf *.py[co] __pycache__ dnf-plugin-system-upgrade-*.tar.gz po/*.mo

check: po/en_GB.mo
	$(PYTHON) -m $(PYTHON_UNITTEST_MODULE) test_system_upgrade

archive: version-check
	git archive --prefix=dnf-plugin-system-upgrade-$(VERSION)/ \
		    --output=dnf-plugin-system-upgrade-$(VERSION).tar.gz \
		    $(VERSION)

version-check:
	git describe --tags $(VERSION)
	grep '^Version:\s*$(VERSION)' dnf-plugin-system-upgrade.spec

.PHONY: build install clean check archive version-check
