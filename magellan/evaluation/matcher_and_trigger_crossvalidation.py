import magellan as mg
import numpy as np
import pandas as pd

from magellan.matcher.booleanrulematcher import BooleanRuleMatcher
from magellan.evaluation.evaluation import eval_matches
from magellan.debugmatcher.debug_gui_utils import get_name_for_predict_column
from sklearn.cross_validation import KFold
from sklearn import clone
from collections import OrderedDict
import pyprind

def cv_matcher_and_trigger(matcher, trigger, table, exclude_attrs,
                           target_attr, k=5, metric='precision', random_state=None):
    assert metric in ['precision', 'recall', 'f1'], "Metric should be one of precision, recall, f1"
    folds = KFold(len(table), k, shuffle=True, random_state=random_state)
    table = table.copy()
    if isinstance(trigger, list) == False:
        trigger = [trigger]
    eval_ls = []
    ltable=table.get_property('ltable')
    rtable=table.get_property('rtable')
    foreign_key_ltable=table.get_property('foreign_key_ltable')
    foreign_key_rtable=table.get_property('foreign_key_rtable')
    if mg._progbar:
        bar = pyprind.ProgBar(k)
    for train_ind, test_ind in folds:
        train = mg.create_mtable(table.iloc[train_ind], key=table.get_key(),
                                     ltable=ltable,rtable=rtable,
                                     foreign_key_ltable=foreign_key_ltable,
                                     foreign_key_rtable=foreign_key_rtable)
        test = mg.create_mtable(table.iloc[test_ind], key=table.get_key(),
                                     ltable=ltable,rtable=rtable,
                                     foreign_key_ltable=foreign_key_ltable,
                                     foreign_key_rtable=foreign_key_rtable)
        if isinstance(matcher, BooleanRuleMatcher) == True:
            pred_col = get_name_for_predict_column(table.columns)
            predicted = matcher.predict(table=test, append=True, target_attr=pred_col,
                                        inplace=False)
        else:
            matcher.clf = clone(matcher.clf)
            matcher.fit(table=train, exclude_attrs=exclude_attrs,target_attr=target_attr)
            pred_col = get_name_for_predict_column(table.columns)
            predicted = matcher.predict(table=test, exclude_attrs=exclude_attrs,
                                        append=True, target_attr=pred_col, inplace=False)

        for t in trigger:
            t.execute(predicted, pred_col, inplace=True)

        eval_summary = eval_matches(predicted, target_attr, pred_col)
        eval_ls.append(eval_summary)
        if mg._progbar:
            bar.update()

    header = ['Name', 'Matcher', 'Metric', 'Num folds']
    fold_header = ['Fold ' + str(i+1) for i in range(k)]
    header.extend(fold_header)
    header.append('Mean score')
    val_list = []
    val_list.append(matcher.name)
    val_list.append(matcher)
    val_list.append(metric)
    val_list.append(k)
    scores = []
    for e in eval_ls:
        scores.append(e[metric])
    val_list.extend(scores)
    val_list.append(np.mean(scores))
    d = OrderedDict(zip(header, val_list))
    stats = pd.DataFrame([d])
    stats = stats[header]
    res = OrderedDict()
    res['cv_stats'] = stats
    res['fold_stats'] = eval_ls
    return res

