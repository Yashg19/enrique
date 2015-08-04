# imports

import jpype
import logging
import os

from magellan.utils import installpath

# get installation path
def get_install_path():
    plist = installpath.split(os.sep)
    return os.sep.join(plist[0:len(plist)-1])

# initialize JVM
def init_jvm(jvmpath=None):
    """
    Initialize JVM and set class paths to execute sim. functions and tokenizers

    Paramaters
    ----------
    jvmpath : string, defaults to None
        If jvmpath is not given, a default path (identified by jpype package) is used

    Returns
    -------
    status : boolean
        Whether the initialization was successful
    """
    # check if the JVM is already running
    if jpype.isJVMStarted():
        logging.getLogger(__name__).warning('JVM is already running')
        return True

    # prepare classpaths
    # taken from https://github.com/konlpy/konlpy/blob/master/konlpy/jvm.py
    folder_suffix = ['{0}{2}', '{0}{1}secondstring-20120620.jar{2}', \
                     '{0}{1}simfunction.jar{2}', \
                     '{0}{1}simmetrics_jar_v1_6_2_d07_02_07.jar{2}', \
                     '{0}{1}*'
                     ]
    # maps to contents in inst/java under magellan dir
    java_dir = '%s%sinst%sjava' %(get_install_path(), os.sep, os.sep)
    if os.name == 'nt':
        args = [java_dir, os.sep,';']
    else:
        args = [java_dir, os.sep,':']
    classpath = os.sep.join(f.format(*args) for f in folder_suffix)

    # if JVM path is given then use it, else use default JVM path from jpype
    jvmpath = jvmpath or jpype.getDefaultJVMPath()
    if jvmpath:
        jpype.startJVM(jvmpath, '-Djava.class.path=%s' % classpath)
        return True
    else:
        raise ValueError('Please specify JVM path')

# remove non-ascii characters from string
def remove_non_ascii(s):
    s = ''.join(i for i in s if ord(i) < 128)
    s = str(s)
    return str.strip(s)
