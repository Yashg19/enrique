from collections import OrderedDict
import logging
class MatchTrigger(object):
    """
    Class to patch output from Matchers.
    Note:
    This class is similar to BooleanRuleMatcher except that this class switches predictions.
    """
    def __init__(self):
        self.cond_status = False
        self.rules = OrderedDict()
        self.rule_source = OrderedDict()
        self.rule_conjunct_list = OrderedDict()
        self.rule_cnt = 0
        self.value_to_set = 0


    def add_cond_rule(self, conjunct_list, feature_table):
        """
        Add rule to match trigger

        Parameters
        ----------
        conjunct_list : List of strings.
         List of predicates as in ['title_title_lev > 0.8', 'name_name_mel' > 0.6]

        feature_table : Pandas dataframe.
          Feature table containing information about features.
          see also:  get_features_for_blocking, get_features_from_matching, get_features

        Returns
        -------
        status : boolean, return True if the command was executed successfully.


        """
        if not isinstance(conjunct_list, list):
            conjunct_list = [conjunct_list]

        fn, name, fn_str = self.create_rule(conjunct_list, feature_table)

        self.rules[name] = fn
        self.rule_source[name] = fn_str
        self.rule_conjunct_list[name] = conjunct_list

        return True



    def add_cond_status(self, status):
        """
        Add boolean status that the condition is expected to satisfy

        Parameters
        ----------
        status : boolean, status that the user wants the condition to satisfy

        Returns
        -------
        ret_status : boolean, returns True if the command was executed successfully.
        """
        if not isinstance(status, bool):
            raise AssertionError('status is expected to be a boolean i.e True/False')
        self.cond_status = status
        return True

    def add_action(self, value):
        """
        Add action if the condition evaluates to condition status (see add_cond_rule, add_cond_status)

        Parameters
        ----------
        value : int (0/1). Value to be set if the condition evaluates to condition status

        Returns
        -------
        status : boolean, returns True if the command was executed successfully.

        """
        if value is not 1 or 0:
            raise AssertionError('Currently magellan supports only values 0/1 as label value')
        self.value_to_set = value
        return True
    # --------------------- currently working on --------------------------
    def execute(self, input_table, label_column):
        ltable = input_table.get_property('ltable')
        rtable = input_table.get_property('rtable')
        assert ltable is not None, 'Left table is not set'
        assert rtable is not None, 'Right table is not set'
        table = input_table.copy()

        l_key = input_table.get_property('foreign_key_ltable')
        r_key = input_table.get_property('foreign_key_rtable')

        # set the index and store it in l_tbl/r_tbl
        l_tbl = ltable.set_index(ltable.get_key(), drop=False)
        r_tbl = rtable.set_index(rtable.get_key(), drop=False)

        # keep track of valid ids
        y = []
        # iterate candidate set and process each row
        for idx, row in input_table.iterrows():
            if row[label_column] != self.value_to_set:
                # get the value of block attribute from ltuple
                l_row = l_tbl.ix[row[l_key]]
                r_row = r_tbl.ix[row[r_key]]
                res = self.apply_rules(l_row, r_row)
                if res == self.cond_status:
                    # switch labels.
                    table[label_column] = self.value_to_set
        return table




    def create_rule(self, conjunct_list, feature_table, name=None):
        if feature_table is None:
            logging.getLogger(__name__).error('Feature table is not given')
            return False
        # set the name
        if name is None:
            name = '_rule_' + str(self.rule_cnt)
            self.rule_cnt += 1

        fn_str = self.get_function_str(name, conjunct_list)

        if feature_table is not None:
            feat_dict = dict(zip(feature_table['feature_name'], feature_table['function']))
        else:
            feat_dict = dict(zip(self.feature_table['feature_name'], self.feature_table['function']))

        exec fn_str in feat_dict
        return feat_dict[name], name, fn_str

    def del_rule(self, rule_name):
        if rule_name not in self.rules.keys():
            logging.getLogger(__name__).error('Rule name not present in current set of rules')
            return False

        del self.rules[rule_name]
        del self.rule_source[rule_name]
        del self.rule_conjunct_list[rule_name]

        return True

    def view_rule(self, rule_name):
        if rule_name not in self.rules.keys():
            logging.getLogger(__name__).error('Rule name not present in current set of rules')
        print(self.rule_source[rule_name])

    def get_rule_names(self):
        return self.rules.keys()

    def get_rule(self, rule_name):
        if rule_name not in self.rules.keys():
            logging.getLogger(__name__).error('Rule name not present in current set of rules')
        return self.rules[rule_name]

    def apply_rules(self, ltuple, rtuple):
        for fn in self.rules.values():
            res = fn(ltuple, rtuple)
            if res is True:
                return True
        return False

    def get_function_str(self, name, conjunct_list):
        # create function str
        fn_str = "def " + name + "(ltuple, rtuple):\n"
        # add 4 tabs
        fn_str += '    '
        fn_str += 'return ' + ' and '.join(conjunct_list)
        return fn_str
