#
# SConstruct file.
#
# For help on its use, run "scons -H", or just run "scons" to build
# all targets.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os
import re


# ----------------------------------------------------------------------------
# Command-Line Options
# ----------------------------------------------------------------------------

opts = Options()
opts.AddOptions(
    BoolOption( "DEBUG", "Set to 1 to build for debug.", 0 ),
    )


# ----------------------------------------------------------------------------
# Our Custom Environment Class
# ----------------------------------------------------------------------------

class OurCustomEnvironment( Environment ):
    """
    A standard SCons Environment with some additional helper
    functions/methods.
    """

    COMPILER_OPTIONS = "CCFLAGS"
    LINKER_OPTIONS = "LINKFLAGS"

    MSVC = "cl"
    GCC = "gcc"

    def addToListVariable( self,
                           varName,
                           cCompiler,
                           base = [],
                           debug = [],
                           noDebug = [] ):
        """
        Appends to a list environment variable if the given C compiler
        is being used.  The list in 'base' is always added, the list
        in 'debug' is added only if debugging is enabled, and the list
        in 'noDebug' is added only if debugging is not enabled.
        """

        if self["CC"] == cCompiler:
            finalList = []
            finalList.extend( base )
            if self["DEBUG"]:
                finalList.extend( debug )
            else:
                finalList.extend( noDebug )
            kwargs = { varName : finalList }
            self.Append( **kwargs )


# ----------------------------------------------------------------------------
# Base Environment Definition
# ----------------------------------------------------------------------------

env = OurCustomEnvironment( options = opts )

# This makes it so that we can just execute "scons -h" to see nicely
# formatted help for this SConstruct file.
Help( opts.GenerateHelpText(env) )


# ----------------------------------------------------------------------------
# C/C++ Compiler Options
# ----------------------------------------------------------------------------

# Documentation on Visual C++ Compiler Options can be found here:
# http://msdn2.microsoft.com/en-us/library/9s7c9wdw(VS.80).aspx

env.addToListVariable(
    env.COMPILER_OPTIONS,
    env.MSVC,
    [ "/W3",      # Set warning level (max is 4, min is 0)
      #"/WX",      # Treat all warnings as errors
      "/nologo",  # Suppress display of sign-on banner
      "/Zi",      # Produce a program database (PDB) for debugging
      ]
    )

# Documentation on GCC compiler options can be found here:
# http://gcc.gnu.org/onlinedocs/gcc/Option-Summary.html

env.addToListVariable(
    env.COMPILER_OPTIONS,
    env.GCC,
    [ "-Wall",    # Enable all warnings
      #"-Werror",  # Treat all warnings as errors
      ]
    )


# ----------------------------------------------------------------------------
# C/C++ Linker Options
# ----------------------------------------------------------------------------

# Documentation on Visual C++ Linker Options can be found here:
# http://msdn2.microsoft.com/en-us/library/y0zzbyt4(VS.80).aspx

env.addToListVariable(
    env.LINKER_OPTIONS,
    env.MSVC,
    [ "/nologo",  # Suppress display of sign-on banner
      "/DEBUG",   # Create .pdb file containing debugging information
      ]
    )


# ----------------------------------------------------------------------------
# Build Actions
# ----------------------------------------------------------------------------

SConscript( "cheapglk/SConscript", exports="env" )
