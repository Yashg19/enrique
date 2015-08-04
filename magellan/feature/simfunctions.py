import jpype
import pandas as pd
import numpy as np

from magellan.utils.helperfunctions import remove_non_ascii

# list of sim functions supported : UPDATE LATER
sim_fn_names = ['jaccard', 'lev', 'exact_match', 'rel_diff']

# abbreviations of sim functions
abb = ['jac', 'lev', 'exm', 'rdf']

# global function names
_m_global_sim_fns = pd.DataFrame({'function_name':sim_fn_names, 'short_name':abb})

# get similarity functions
def get_sim_funs():
    fns = [jaccard, lev, exact_match, rel_diff]
    return dict(zip(sim_fn_names, fns))

# similarity measures

# set based
def jaccard(arr1, arr2):
    if arr1 is None or arr2 is None:
        return np.NaN
    if any(pd.isnull(arr1)) or any(pd.isnull(arr2)):
        return np.NaN
    sim = jpype.JClass('build.SimilarityFunction')()
    return sim.jaccard(arr1, arr2)

# string based
def lev(s1, s2):
    if s1 is None or s2 is None:
        return np.NaN
    if pd.isnull(s1) or pd.isnull(s2):
        return np.NaN
    if isinstance(s1, basestring):
        s1 = remove_non_ascii(s1)
    if isinstance(s2, basestring):
        s2 = remove_non_ascii(s2)
    sim = jpype.JClass('build.SimilarityFunction')()
    return sim.levenshtein(str(s1), str(s2))

# boolean/string/numeric similarity measure
def exact_match(d1, d2):
    if d1 is None or d2 is None:
        return np.NaN
    if pd.isnull(d1) or pd.isnull(d2):
        return np.NaN
    if d1 == d2:
        return 1
    else:
        return 0

# numeric similarity measure
def rel_diff(d1, d2):
    if d1 is None or d2 is None:
        return np.NaN
    if pd.isnull(d1) or pd.isnull(d2):
        return np.NaN
    return abs(d1-d2)/(d1+d2)