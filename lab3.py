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
            return set([self._from]).union(set(self._to))

        
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


    def delete_long_rules(self):
        extra_nonterm_num = 0
        new_rules = []
        new_nonterminals = []
        for rule in self._rules:
            if len(rule.get_right_side()) <= 2:
                new_rules.append(rule)
                continue
            new_rules.append(Language.Rule("%s %s %s" % (rule.get_left_side(), rule.get_right_side()[0], "EXTRA_NONTERMINAL_%s" % extra_nonterm_num)))
            self._nonterminals.append("EXTRA_NONTERMINAL_%s" % extra_nonterm_num)
            extra_nonterm_num = extra_nonterm_num + 1
            for i in range(1, len(rule.get_right_side()) - 2):
                new_rules.append(Language.Rule("%s %s %s" % ("EXTRA_NONTERMINAL_%s" % extra_nonterm_num - 1, rule.get_right_side()[i], "EXTRA_NONTERMINAL_%s" % extra_nonterm_num)))
                self._nonterminals.append("EXTRA_NONTERMINAL_%s" % extra_nonterm_num)
                extra_nonterm_num = extra_nonterm_num + 1
            new_rules.append(Language.Rule("%s %s %s" % ("EXTRA_NONTERMINAL_%s" % (extra_nonterm_num - 1, ), rule.get_right_side()[len(rule.get_right_side()) - 2], rule.get_right_side()[len(rule.get_right_side()) - 1])))
        self._rules = new_rules


    def delete_chain_rules(self):
        chain_pairs = [(A, A) for A in self._nonterminals]
        found_new = True
        while found_new:
            found_new = False
            new_chain_pairs = []
            for chain_pair in chain_pairs:
                for rule in self._rules:
                    if (len(rule.get_right_side()) != 1) or (rule.get_right_side()[0] not in self._nonterminals):
                        continue
                    if (chain_pair[1] == rule.get_left_side()) and ((chain_pair[0], rule.get_right_side()[0]) not in chain_pairs):
                        new_chain_pairs.append((chain_pair[0], rule.get_right_side()[0]))
                        found_new = True
            chain_pairs.extend(new_chain_pairs)

        new_rules = []
        for chain_pain in chain_pairs:
            for rule in self._rules:
                if ((len(rule.get_right_side()) == 1) and (rule.get_right_side()[0] in self._nonterminals)) or (chain_pain[1] != rule.get_left_side()):
                    continue
                new_rules.append(Language.Rule("%s %s" % (chain_pain[0], ' '.join(rule.get_right_side()))))
        for rule in self._rules:
            if (len(rule.get_right_side()) != 1) or (rule.get_right_side()[0] not in self._nonterminals):
                new_rules.append(rule)
        self._rules = new_rules


    def remake_double_terms(self):
        new_rules = []
        placeholder = 0
        for rule in self._rules:
            if (len(rule.get_right_side()) != 2):
                new_rules.append(rule)
                continue

            rule_str = rule.get_left_side() + ' '

            if rule.get_right_side()[0] in self._terminals:
                rule_str = rule_str + ("PLACEHOLDER_%s" % placeholder) + ' '
                new_rules.append(Language.Rule("%s %s" % ("PLACEHOLDER_%s" % placeholder, rule.get_right_side()[0])))
                self._nonterminals.append("PLACEHOLDER_%s" % placeholder)
                placeholder = placeholder + 1
            else:
                rule_str = rule_str + rule.get_right_side()[0] + ' '

            if rule.get_right_side()[1] in self._terminals:
                rule_str = rule_str + ("PLACEHOLDER_%s" % placeholder)
                new_rules.append(Language.Rule("%s %s" % ("PLACEHOLDER_%s" % placeholder, rule.get_right_side()[1])))
                self._nonterminals.append("PLACEHOLDER_%s" % placeholder)
                placeholder = placeholder + 1
            else:
                rule_str = rule_str + rule.get_right_side()[1]

            new_rules.append(Language.Rule(rule_str))
        self._rules = new_rules


    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "Non-terminals: %s\nTerminals: %s\nRules: %s\nStart symbol: %s" % (self._nonterminals, self._terminals, self._rules, self._start_symbol)

    def build_parse_table(self, terminal_chain):
        terminal_chain = terminal_chain.split(' ')
        parse_table = [[set() for _ in range(0, len(terminal_chain) - i)] for i in range(0, len(terminal_chain))]
        for i in range(0, len(terminal_chain)):
            for rule in self._rules:
                if terminal_chain[i] in rule.get_right_side():
                    parse_table[i][0].add(rule.get_left_side())
        print(parse_table)

        for j in range(2, len(terminal_chain) + 1):
            for i in range(1, len(terminal_chain) - j + 2):
                for k in range(1, j):
                    for rule in self._rules:
                        if len(rule.get_right_side()) != 2:
                            continue
                        B = rule.get_right_side()[0]
                        C = rule.get_right_side()[1]
                        if (B in parse_table[i - 1][k - 1]) and (C in parse_table[i + k - 1][j - k - 1]):
                            parse_table[i - 1][j - 1].add(rule.get_left_side())

        return parse_table


    def left_parsing(self, terminal_chain, parse_table):
        terminal_chain = terminal_chain.split(' ')

        def gen(i, j, A):
            if j == 1:
                for rule in self._rules:
                    if (rule.get_right_side()[0] == terminal_chain[i - 1]) and (rule.get_left_side() == A):
                        print(rule)
                        return
            for k in range(1, j):
                for rule in self._rules:
                    if len(rule.get_right_side()) != 2:
                        continue
                    if rule.get_left_side() != A:
                        continue
                    B = rule.get_right_side()[0]
                    C = rule.get_right_side()[1]
                    if (B in parse_table[i - 1][k - 1]) and (C in parse_table[i + k - 1][j - k - 1]):
                        print(rule)
                        gen(i, k, B)
                        gen(i + k, j - k, C)
                        return

        if self._start_symbol not in parse_table[0][len(parse_table) - 1]:
            print('Impossible terminal chain')

        gen(1, len(terminal_chain), self._start_symbol)


language = Language(filename='grammer728.txt')
print('Original grammer:')
print(language)
print('')
print('')
print('Delete long rules:')
language.delete_long_rules()
print(language)
print('')
print('')
print('Delete chain rules:')
language.delete_chain_rules()
print(language)
print('')
print('')
print('Delete extra symbols:')
language.remove_unnecessary_nonterminals()
language.remove_unreachable_symbols()
print(language)
print('')
print('')
print('Normal Homskey form:')
language.remake_double_terms()
print(language)

terminal_chain = '( a + b ) * ( - a ) / pi'
parse_table = language.build_parse_table(terminal_chain)
print('')
print('')
print('Parsing table')
for i in range(0, len(terminal_chain.split(' '))):
    for j in range(0, len(terminal_chain.split(' ')) - i):
        print(i, j)
        print(parse_table[i][j], )
    print()
print('')
print('')
print('Production')
language.left_parsing(terminal_chain, parse_table)
