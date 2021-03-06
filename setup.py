#!/usr/bin/env python
import os
import re
import sys
import urllib
from glob import glob
from itertools import chain
from subprocess import run

from setuptools import setup, find_packages
from setuptools.command.install import install as _install

from semstr.__version__ import VERSION

try:
    this_file = __file__
except NameError:
    this_file = sys.argv[0]
os.chdir(os.path.dirname(os.path.abspath(this_file)))

extras_require = {}
install_requires = []
for requirements_file in glob("requirements.*txt"):
    suffix = re.match(r"[^.]*\.(.*)\.?txt", requirements_file).group(1).rstrip(".")
    with open(requirements_file) as f:
        (extras_require.setdefault(suffix, []) if suffix else install_requires).extend(f.read().splitlines())

try:
    # noinspection PyPackageRequirements
    import pypandoc
    try:
        pypandoc.convert_file("README.md", "rst", outputfile="README.rst")
    except (IOError, ImportError, RuntimeError):
        pass
    long_description = pypandoc.convert_file("README.md", "rst")
except (IOError, ImportError, RuntimeError):
    long_description = ""


class install(_install):
    # noinspection PyBroadException
    def run(self):
        # Get submodules
        self.announce("Getting git submodules...")
        run(["git", "submodule", "update", "--init", "--recursive"], check=True)

        # Install requirements
        self.announce("Installing dependencies...")
        run(["pip", "--no-cache-dir", "install"] + install_requires +
            list(chain.from_iterable(extras_require.values())), check=True)

        # Install AMR resource
        for filename in ("have-org-role-91-roles-v1.06.txt", "have-rel-role-91-roles-v1.06.txt",
                         "verbalization-list-v1.06.txt", "morph-verbalization-v1.01.txt"):
            out_file = os.path.join("semstr", "util", "resources", filename)
            if not os.path.exists(out_file):
                self.announce("Getting '%s'..." % filename)
                try:
                    urllib.request.urlretrieve("https://amr.isi.edu/download/lists/" + filename, out_file)
                except:
                    self.warn("Failed downloading https://amr.isi.edu/download/lists/" + filename + " to " + out_file)

        # Install actual package
        _install.run(self)


setup(name="SEMSTR",
      version=VERSION,
      description="Scheme Evaluation and Mapping for Structural Text Representation",
      long_description=long_description,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Topic :: Text Processing :: Linguistic",
      ],
      author="Daniel Hershcovich",
      author_email="danielh@cs.huji.ac.il",
      url="https://github.com/huji-nlp/semstr",
      setup_requires=["pypandoc"],
      install_requires=install_requires,
      extras_require=extras_require,
      packages=find_packages() + ["src"],
      package_dir={
          "src": os.path.join("semstr", "amr", "src"),
      },
      package_data={"src": ["amr.peg"], "semstr.util": ["resources/*.txt"]},
      cmdclass={"install": install},
      )
