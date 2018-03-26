"""A library for handling SQL-like queries with light input validation and basic arithmetic support for combining queries.
"""

joins = ['inner join', 'left outer join']

class SQLComponent(object):
    def __init__(self, value):
        if not value:
            self.value = None
            return self
        self.validate_type(value)
        self.value = value

    @property
    def expected_type(self):
        raise NotImplementedError('expected_type has not been defined for %s' % self.__class__.__name__)

    def validate_type(self, value):
        tipe = self.expected_type
        if not isinstance(value, self.expected_type):
            raise ValueError('%s is not of type %s' % (value, self.expected_type))

    @property
    def as_string(self):
        if not self.value.upper().startswith(self.component_name):
            return '%s %s' % (self.component_name, self.value)
        value = get_upper_cased_component_value(self.value, self.component_name)
        return value

    def get_value_without_component(self):
        if self.value.upper().startswith(self.component_name):
            return self.value[len(self.component_name):].strip()
        return self.value

    def _add_instance(self):
        raise NotImplementedError('_add_rule has not been defined for %s' % self.__class__.__name__)

    def __radd__(self, other):
        return __add__(self, other)

    def __add__(self, other):
        if hasattr(other, 'value') and not other.value:
            return self
        if isinstance(other, self.__class__):
            self._add_instance(other)
        elif isinstance(other, self.expected_type):
            self._add_instance(self.__class__(other))
        else:
            raise ValueError('Cannot produce %s from %s' % (self.__class__.__name__, type(other).__name__))
        return self

    def __str__(self):
        return self.as_string

class SQLSelect(SQLComponent):
    component_name = 'SELECT'
    def __init__(self, value):
        super(SQLSelect, self).__init__(value)

    @property
    def expected_type(self):
        return str

    def _add_instance(self, other):
        basic_add_instance(self, other)

class SQLFrom(SQLComponent):
    component_name = 'FROM'
    def __init__(self, value):
        super(SQLFrom, self).__init__(value)

    @property
    def expected_type(self):
        return str

    def _add_instance(self, other):
        if not self.value:
            self.value = other.value
        else:
            other_value_plain = other.get_value_without_component()
            for join in joins:
                if other_value_plain.lower().strip().startswith(join):
                    self.value += ' %s' % other_value_plain
                    return
            self.value += ', %s' % other_value_plain


class SQLWhere(SQLComponent):
    component_name = 'WHERE'
    def __init__(self, value):
        super(SQLWhere, self).__init__(value)

    @property
    def expected_type(self):
        return str

    def _add_instance(self, other):
        if not self.value:
            self.value = other.value
        else:
            other_value_plain = other.get_value_without_component()
            self.value += ' and %s' % other_value_plain

class SQLGroupBy(SQLComponent):
    component_name = 'GROUP BY'
    def __init__(self, value):
        super(SQLGroupBy, self).__init__(value)

    @property
    def expected_type(self):
        return str

    def _add_instance(self, other):
        basic_add_instance(self, other)

class SQLHaving(SQLComponent):
    component_name = 'HAVING'
    def __init__(self, value):
        super(SQLHaving, self).__init__(value)

    @property
    def expected_type(self):
        return str

    def _add_instance(self, other):
        if not self.value:
            self.value = other.value
        else:
            other_value_plain = other.get_value_without_component()
            self.value += ' and %s' % other_value_plain

class SQLOrderBy(SQLComponent):
    component_name = 'ORDER BY'
    def __init__(self, value):
        super(SQLOrderBy, self).__init__(value)

    @property
    def expected_type(self):
        return str

    def _add_instance(self, other):
        basic_add_instance(self, other)

class SQLLimit(SQLComponent):
    component_name = 'LIMIT'
    def __init__(self, value):
        if isinstance(value, str):
            value = value.strip()
            if not value:
                value = None
            else:
                if value.upper().startswith(self.component_name):
                    import re
                    value = re.sub(r'%s ' % self.component_name, '', value, count=1, flags=re.IGNORECASE)
                value = int(value)
        super(SQLLimit, self).__init__(value)

    @property
    def expected_type(self):
        return int

    @property
    def as_string(self):
        return '%s %s' % (self.component_name, self.value)

    def _add_instance(self, other):
        if not self.value:
            self.value = other.value
        else:
            raise ValueError('Cannot specify more than 1 LIMIT.')

class SQL(object):
    def __init__(self, _select=None, _from=None, _where=None, _group_by=None, _having=None, _order_by=None, _limit=None):
        if not _select and not _from:
            raise ValueError('Cannot instantiate SQL object without SELECT or FROM.')
        self._select = _select and isinstance(_select, SQLSelect) or SQLSelect(_select)
        self._from = _from and isinstance(_from, SQLFrom) or SQLFrom(_from)
        self._where = _where and isinstance(_where, SQLWhere) or SQLWhere(_where)
        self._group_by = _group_by and isinstance(_group_by, SQLGroupBy) or SQLGroupBy(_group_by)
        self._having = _having and isinstance(_having, SQLHaving) or SQLHaving(_having)
        self._order_by = _order_by and isinstance(_order_by, SQLOrderBy) or SQLOrderBy(_order_by)
        self._limit = _limit and isinstance(_limit, SQLLimit) or SQLLimit(_limit)

    @classmethod
    def from_string(cls, sql_string):
        SELECT = 0
        FROM = 1
        WHERE = 2
        GROUP_BY = 3
        HAVING = 4
        ORDER_BY = 5
        LIMIT = 6

        plain_components = tokenize_sql_component(sql_string)

        _select = plain_components[SELECT] or None
        _from = plain_components[FROM] or None
        _where = plain_components[WHERE] or None
        _group_by = plain_components[GROUP_BY] or None
        _having = plain_components[HAVING] or None
        _order_by = plain_components[ORDER_BY] or None
        _limit = plain_components[LIMIT] and int(plain_components[LIMIT]) or None

        return cls(_select, _from, _where, _group_by, _having, _order_by, _limit)

    @property
    def as_string(self):
        string = '%s %s' % (self._select.as_string, self._from.as_string)
        if self._where.value:
            string += ' %s' % self._where.as_string
        if self._group_by.value:
            string += ' %s' % self._group_by.as_string
        if self._having.value:
            string += ' %s' % self._having.as_string
        if self._order_by.value:
            string += ' %s' % self._order_by.as_string
        if self._limit.value:
            string += ' %s' % self._limit.as_string
        return string

    def __radd__(self, other):
        return __add__(self, other)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            self._select += other._select
            self._from += other._from
            self._where += other._where
            self._group_by += other._group_by
            self._having += other._having
            self._order_by += other._order_by
            self._limit += other._limit
        elif isinstance(other, SQLComponent):
            for attr, value in self.__dict__.iteritems():
                if isinstance(other, value.__class__):
                    value += other
                    break
        return self

    def __str__(self):
        return self.as_string

def tokenize_sql_component(statement):
    component_names = {
        'select':0,
        'from':1,
        'where':2,
        'group by':3,
        'having':4,
        'order by':5,
        'limit':6
    }
    component_index = -1
    components = ['' for x in range(len(component_names.keys()))]
    left_parens = 0
    word = ''
    statement = statement.replace('\n', ' ').replace('\t', ' ').strip()
    for char in statement:
        if not left_parens and word.lower().strip() in component_names:
            component_index = component_names[word.lower().strip()]
        if char == '(':
            left_parens += 1
        elif char == ')':
            left_parens -= 1
        if char in [' '] and not filter(lambda x: ' ' in x and word.lower() in x, component_names.keys()):
            word = ''
        else:
            word += char
        if component_index != -1 and char != ';':
            components[component_index] += char
    def get_components_without_useless_characters(components):
        cleaned_components = []
        for component in components:
            component = component.strip()
            for component_name in component_names.keys():
                if component.lower().endswith(component_name):
                    component = delete_last_occurence(component, component_name).strip()
            cleaned_components.append(component)
        return cleaned_components
    plain_components = get_components_without_useless_characters(components)
    return plain_components

def basic_add_instance(sql_component, other):
    if not sql_component.value:
        sql_component.value = other.value
    else:
        other_value_plain = other.get_value_without_component()
        sql_component.value += ', %s' % other_value_plain

def delete_last_occurence(s, occurence):
    i = get_index_of_last_occurence(s, occurence)
    return s[:i]

def get_index_of_last_occurence(s, occurence):
    return s.lower().rfind(occurence)

def get_upper_cased_component_value(value, component_name):
    return value.replace(component_name.lower(), component_name, 1)
