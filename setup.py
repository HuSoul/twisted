#! /usr/bin/env python

# Twisted, the Framework of Your Internet
# Copyright (C) 2001 Matthew W. Lefkowitz
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of version 2.1 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""
Package installer for Twisted

Copyright (C) 2001 Matthew W. Lefkowitz
All rights reserved, see LICENSE for details.

$Id: setup.py,v 1.36 2002/04/26 05:08:41 carmstro Exp $
"""

import distutils, os, sys, string
from glob import glob

from distutils.core import setup, Extension
from distutils.command.build_scripts import build_scripts
from distutils.command.install_data import install_data

from twisted import copyright


#############################################################################
### Helpers and distutil tweaks
#############################################################################

script_preamble = """
### Twisted Preamble
# This makes sure that users don't have to set up their environment
# specially in order to run these programs from bin/.
import sys, os, string
pos = string.find(os.path.abspath(sys.argv[0]), os.sep+'Twisted')
if pos != -1:
    sys.path.insert(0, os.path.abspath(sys.argv[0])[:pos+8])
sys.path.insert(0, os.curdir)
### end of preamble
"""

class build_scripts_create(build_scripts):
    """ Overload the build_scripts command and create the scripts
        from scratch, depending on the target platform.

        You have to define the name of your package in an inherited
        class (due to the delayed instantiation of command classes
        in distutils, this cannot be passed to __init__).

        The scripts are created in an uniform scheme: they start the
        run() function in the module

            <packagename>.scripts.<mangled_scriptname>

        The mangling of script names replaces '-' and '/' characters
        with '-' and '.', so that they are valid module paths. 
    """
    package_name = None

    def copy_scripts(self):
        """ Create each script listed in 'self.scripts'
        """
        if not self.package_name:
            raise Exception("You have to inherit build_scripts_create and"
                " provide a package name")
        
        to_module = string.maketrans('-/', '_.')

        self.mkpath(self.build_dir)
        for script in self.scripts:
            outfile = os.path.join(self.build_dir, os.path.basename(script))

            #if not self.force and not newer(script, outfile):
            #    self.announce("not copying %s (up-to-date)" % script)
            #    continue

            if self.dry_run:
                self.announce("would create %s" % outfile)
                continue

            module = os.path.splitext(os.path.basename(script))[0]
            module = string.translate(module, to_module)
            script_vars = {
                'python': os.path.normpath(sys.executable),
                'package': self.package_name,
                'module': module,
                'preamble': script_preamble,
            }

            self.announce("creating %s" % outfile)
            file = open(outfile, 'w')

            try:
                if sys.platform == "win32":
                    file.write('@echo off\n'
                        'if NOT "%%_4ver%%" == "" %(python)s -c "from %(package)s.scripts.%(module)s import run; run()" %%$\n'
                        'if     "%%_4ver%%" == "" %(python)s -c "from %(package)s.scripts.%(module)s import run; run()" %%*\n'
                        % script_vars)
                else:
                    file.write('#! %(python)s\n'
                        '%(preamble)s\n'
                        'from %(package)s.scripts.%(module)s import run\n'
                        'run()\n'
                        % script_vars)
            finally:
                file.close()
                os.chmod(outfile, 0755)


class build_scripts_twisted(build_scripts_create):
    package_name = 'twisted'


def scriptname(path):
    """ Helper for building a list of script names from a list of
        module files.
    """
    script = os.path.splitext(os.path.basename(path))[0]
    script = string.replace(script, '_', '-')
    if sys.platform == "win32":
        script = script + ".bat"
    return script


# build list of scripts from their implementation modules
twisted_scripts = map(scriptname, glob('twisted/scripts/[!_]*.py'))


# make sure data files are installed in twisted package
# this is evil.
class install_data_twisted(install_data):
    def finalize_options (self):
        self.set_undefined_options('install',
            ('install_lib', 'install_dir'),
            ('root', 'root'),
            ('force', 'force'),
        )


#############################################################################
### Call setup()
#############################################################################

ver = string.replace(copyright.version, '-', '_') #RM doesn't like '-'
setup_args = {
    'name': "Twisted",
    'version': ver
    'description': "Twisted %s is a framework to build frameworks" % ver,
    'author': "Twisted Matrix Laboratories",
    'author_email': "twisted-python@twistedmatrix.com",
    'maintainer': "Glyph Lefkowitz",
    'maintainer_email': "glyph@twistedmatrix.com",
    'url': "http://twistedmatrix.com/",
    'licence': "GNU LGPL",
    'long_description': """
Twisted is a framework to build frameworks. It is expected that one day
the project has expanded to the point that the Twisted Reality framework
(a very small part of the codebase, even now) can seamlessly integrate
with mail, web, DNS, netnews, IRC, RDBMSs, desktop environments, and
your toaster. 
""",
    'packages': [
        "twisted",
        "twisted.coil",
        "twisted.coil.plugins",
        "twisted.cred",
        "twisted.enterprise",
        # "twisted.forum",
        "twisted.im",
        "twisted.internet",
        "twisted.lumberjack",
        "twisted.mail",
        "twisted.manhole",
        "twisted.manhole.ui",
        # "twisted.metrics",
        "twisted.names",
        "twisted.persisted",
        "twisted.protocols",
        "twisted.protocols.ldap",
        "twisted.python",
        "twisted.scripts",
        "twisted.spread",
        "twisted.spread.ui",
        "twisted.tap",
        "twisted.test",
        "twisted.web",
        "twisted.words",
        "twisted.words.ui",
        "twisted.words.ui.gateways",
    ],

    'cmdclass': {
        ## NOT YET for all platforms, see below for win32 test code!
        ##'build_scripts': build_scripts_twisted,
        'install_data': install_data_twisted,
    },
}

if hasattr(distutils.dist.DistributionMetadata, 'get_keywords'):
    setup_args['keywords'] = "internet www tcp framework games"

if hasattr(distutils.dist.DistributionMetadata, 'get_platforms'):
    setup_args['platforms'] = "win32 posix"

if os.name == 'posix':
    setup_args['scripts'] = [
        'bin/manhole', 'bin/mktap', 'bin/twistd',
        'bin/im', 'bin/t-im', 'bin/tap2deb',
        'bin/coil',
    ]
else:
    # new script schema only for win32, for now
    setup_args['scripts'] = twisted_scripts
    setup_args['cmdclass']['build_scripts'] = build_scripts_twisted
    

imPath = os.path.join('twisted', 'im')
setup_args['data_files'] = [(imPath, [os.path.join(imPath, 'instancemessenger.glade')]),
                            ('twisted', [os.path.join('twisted', 'plugins.tml')])]


# for building C banana...

if os.name == 'nt':
    define_macros = [("WIN32", "1")]
else:
    define_macros = []
setup_args['ext_modules'] = [
    Extension("twisted.spread.cBanana", ["twisted/spread/cBanana.c"],
              define_macros=define_macros),
    ]

apply(setup, (), setup_args)

