"""Compile all .po files to .mo files
using polib (no system gettext required)."""
import os
import sys
import polib


# Add project to path
sys.path.insert(0, os.path.dirname(__file__))
BASE = os.path.dirname(__file__)
locale_dir = os.path.join(BASE, 'locale')

compiled = 0
errors = 0

for lang in os.listdir(locale_dir):
    lc_dir = os.path.join(locale_dir, lang, 'LC_MESSAGES')
    po_file = os.path.join(lc_dir, 'django.po')
    mo_file = os.path.join(lc_dir, 'django.mo')

    if os.path.exists(po_file):
        try:
            po = polib.pofile(po_file)
            po.save_as_mofile(mo_file)
            count = len([e for e in po if e.msgstr])
            print("  OK Compiled [{}]: {} translations".format(lang, count))
            compiled += 1
        except Exception as e:
            print("  FAIL Error [{}]: {}".format(lang, e))
            errors += 1

print(f"\nDone: {compiled} compiled, {errors} errors")
