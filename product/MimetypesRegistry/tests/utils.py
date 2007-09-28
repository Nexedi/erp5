import re
import glob
from unittest import TestSuite
from sys import modules
from os.path import join, abspath, dirname, basename

def normalize_html(s):
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"(?s)\s+<", "<", s)
    s = re.sub(r"(?s)>\s+", ">", s)
    s = re.sub(r"\r", "", s)
    return s

PREFIX = abspath(dirname(__file__))

def input_file_path(file):
    return join(PREFIX, 'input', file)

def output_file_path(file):
    return join(PREFIX, 'output', file)

def matching_inputs(pattern):
    return [basename(path) for path in glob.glob(join(PREFIX, "input", pattern))]

def load(dotted_name, globals=None):
    """ load a python module from it's name """
    mod = __import__(dotted_name, globals)
    components = dotted_name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
