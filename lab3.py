import copy

class Language(object):
    
    class Rule(object):
        def __init__(self, string=None):
            if string is not None:
                self.__init_from_string(string)

        def __init_from_string(self, string):
            parts = string.split(' ')
            self._from = parts[0]
            self._to = []
            for i in parts[1:]:
                self._to.append(i)


        def is_lamda_rule(self):
            return len(self._to) == 0

        def get_left_side(self):
            return self._from[:]


        def get_right_side(self):
            return self._to[:]


        def get_all_symbols(self):
            return set(self._from).union(set(self._to))

        
        def get_splitted_copy(self, terminals_to_replace):
            new_rule = copy.deepcopy(self)
            for i in range(0, len(new_rule._to)):
                if new_rule._to[i] in terminals_to_replace:
                    new_rule._to[i] = new_rule._to[i] + '\''
            return new_rule


        def _get_right_part_str(self):
            if self.is_lamda_rule():
                return chr(955)
            else:
                return ' '.join(self._to)
        
        
        def __str__(self):
            return '%s -> %s' % (self._from, self._get_right_part_str())

        
        def __repr__(self):
            return '%s -> %s' % (self._from, self._get_right_part_str())


    def __init_from_file(self, filename):
        with open(filename, 'r') as f:
            nonterminals_num = int(f.readline())
            self._nonterminals = []
            for _ in range(0, nonterminals_num):
                self._nonterminals.append(f.readline().strip(' \n\t'))
            
            terminals_num = int(f.readline().strip(' \n\t'))
            self._terminals = []
            for _ in range(0, terminals_num):
                self._terminals.append(f.readline().strip(' \n\t'))

            rules_num = int(f.readline())
            self._rules = []
            for _ in range(0, rules_num):
                rule = Language.Rule(string=f.readline().strip(' \n\t'))
                self._rules.append(rule)
            
            self._start_symbol = f.readline().strip(' \n\t')
    
    def __init_from_data(self, terminals, non_terminals, rules, start):
        self._nonterminals = non_terminals[:]
        self._terminals = terminals[:]
        self._start_symbol = start
        self._rules = copy.deepcopy(rules)

    
    def __init__(self, filename=None, terminals=None, non_terminals=None, rules=None, start=None):
        if filename is not None:
            self.__init_from_file(filename)
        elif terminals is not None:
            self.__init_from_data(terminals, non_terminals, rules, start)

    def split_grammer(self, nonterminals_to_replace):
        new_grammers = []
        new_rules = []
        for rule in self._rules:
            new_rules.append(rule.get_splitted_copy(nonterminals_to_replace))

        for nonterminal_to_replace in nonterminals_to_replace:
            new_nonterminals = list((set(self._nonterminals)-set(nonterminals_to_replace)).union(set([nonterminal_to_replace])))
            new_terminals = list(set(self._terminals).union(set([i + '\'' for i in nonterminals_to_replace])))
            new_grammers.append(Language(terminals=new_terminals, non_terminals=new_nonterminals, rules=new_rules, start=nonterminal_to_replace))
        
        return new_grammers

    def get_Ne(self):
        previous_set = set([])
        while 1:
            current_set = set([])
            for rule in self._rules:
                if set(rule.get_right_side()).issubset(previous_set.union(set(self._terminals))):
                    current_set.add(rule.get_left_side())
            if current_set == previous_set:
                break
            previous_set = current_set
        return list(previous_set)


    def remove_unnecessary_nonterminals(self):
        ne = self.get_Ne()
        new_nonterminals = list(filter(lambda x: x in ne, self._nonterminals))
        new_rules = list(filter(lambda x: x.get_all_symbols().issubset(set(self._terminals).union(set(ne))), self._rules))
        self._nonterminals = new_nonterminals
        self._rules = new_rules

    def remove_unreachable_symbols(self):
        previous_set = set([self._start_symbol])
        while 1:
            current_set = copy.deepcopy(previous_set)
            for rule in self._rules:
                if rule.get_left_side() in previous_set:
                    for i in rule.get_right_side():
                        current_set.add(i)
            if current_set == previous_set:
                break
            previous_set = current_set
        self._nonterminals = list(set(self._nonterminals).intersection(previous_set))
        self._terminals = list(set(self._terminals).intersection(previous_set))
        self._rules = list(filter(lambda x: x.get_all_symbols().issubset(previous_set), self._rules))


    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "Non-terminals: %s\nTerminals: %s\nRules: %s\nStart symbol: %s" % (self._nonterminals, self._terminals, self._rules, self._start_symbol)

    def build_parse_table(self, terminal_chain):
        parse_table = [[set() for _ in range(0, len(terminal_chain) - i)] for i in range(0, len(terminal_chain))]
        for i in range(0, len(terminal_chain)):
            for rule in self._rules:
                if terminal_chain[i] in rule.get_right_side():
                    parse_table[i][0].add(rule.get_left_side())

        for j in range(2, len(terminal_chain) + 1):
            for i in range(1, len(terminal_chain) - j + 2):
                print(i, j)
                for k in range(1, j):
                    for rule in self._rules:
                        if len(rule.get_right_side()) != 2:
                            continue
                        B = rule.get_right_side()[0]
                        C = rule.get_right_side()[1]
                        if (B in parse_table[i - 1][k - 1]) and (C in parse_table[i + k - 1][j - k - 1]):
                            parse_table[i - 1][j - 1].add(rule.get_left_side())

        return parse_table


language = Language(filename='grammer728.txt')
print('Original grammer:')
print(language)
print('')
print('')
parse_table = language.build_parse_table('abaab')
print(parse_table)
