import unittest
from spyql import get_upper_cased_component_value, joins as sql_joins

class TestSql(unittest.TestCase):
    maxDiff = None

    def test__sql__init(self):
        from spyql import SQL
        sql = SQL.from_string('select a.*, b.* from apples a inner join bananas b using (c,d) where length(a.y) != length(b.z) and length(a.y) > 2 group by a.y having count(a.y)<5 order by b.z limit 15')
        self.assertEqual(sql.as_string, 'SELECT a.*, b.* FROM apples a inner join bananas b using (c,d) WHERE length(a.y) != length(b.z) and length(a.y) > 2 GROUP BY a.y HAVING count(a.y)<5 ORDER BY b.z LIMIT 15')
        sql = SQL.from_string('select test from other;') # testing the processing of semi colons
        self.assertEqual(sql.as_string, 'SELECT test FROM other')

    def test__sql__add(self):
        from spyql import SQL, SQLWhere
        sql = SQL.from_string('SELECT a FROM b')
        self.assertEqual(sql.as_string, 'SELECT a FROM b')
        sql += SQL.from_string('SELECT c FROM d')
        self.assertEqual(sql.as_string, 'SELECT a, c FROM b, d')
        sql += SQLWhere('a > c')
        self.assertEqual(sql.as_string, 'SELECT a, c FROM b, d WHERE a > c')

        query_with_nests = 'select k from (select k from ztab left outer join ytab using (date)) tabk where k in (select k from ytab where k > 5)'
        sql += SQL.from_string(query_with_nests)
        self.assertEqual(sql.as_string, 'SELECT a, c, k FROM b, d, (select k from ztab left outer join ytab using (date)) tabk WHERE a > c and k in (select k from ytab where k > 5)')


    def test__sql_select__init(self):
        from spyql import SQLSelect
        must_receive_string_as_input(self, SQLSelect)
        sql_class_instance_as_string_has_uppered_class_type(self, SQLSelect, 'select test')

    def test__sql_select__add(self):
        from spyql import SQLSelect

        sql_select = SQLSelect('SELECT test1')
        self.assertEqual(sql_select.value, 'SELECT test1')

        sql_select += SQLSelect('select test2')
        self.assertEqual(sql_select.value, 'SELECT test1, test2')

        sql_select += 'SELECT test3'
        self.assertEqual(sql_select.value, 'SELECT test1, test2, test3')

        sql_select += 'test4'
        self.assertEqual(sql_select.value, 'SELECT test1, test2, test3, test4')


    def test__sql_from__init(self):
        from spyql import SQLFrom
        must_receive_string_as_input(self, SQLFrom)
        sql_class_instance_as_string_has_uppered_class_type(self, SQLFrom, 'from test')

    def test__sql_from__add(self):
        from spyql import SQLFrom

        sql_from = SQLFrom('FROM test1 as t1')
        self.assertEqual(sql_from.value, 'FROM test1 as t1')

        sql_from += SQLFrom('from test2 as t2')
        self.assertEqual(sql_from.value, 'FROM test1 as t1, test2 as t2')

        sql_from += 'FROM test3 as t3'
        self.assertEqual(sql_from.value, 'FROM test1 as t1, test2 as t2, test3 as t3')

        sql_from += 'test4'
        self.assertEqual(sql_from.value, 'FROM test1 as t1, test2 as t2, test3 as t3, test4')

        query = sql_from.as_string
        for join in sql_joins:
            addendum = '%s testingtable using (specific)' % join
            sql_from += addendum
            query += ' %s' % addendum
            self.assertEqual(sql_from.value, query)


    def test__sql_where__init(self):
        from spyql import SQLWhere
        must_receive_string_as_input(self, SQLWhere)
        sql_class_instance_as_string_has_uppered_class_type(self, SQLWhere, 'where test')

    def test__sql_where__add(self):
        from spyql import SQLWhere

        sql_where = SQLWhere('')
        self.assertEqual(sql_where.value, None)

        sql_where += SQLWhere('WHERE a.w = b.x')
        self.assertEqual(sql_where.value, 'WHERE a.w = b.x')

        sql_where += SQLWhere('where a.y = b.z')
        self.assertEqual(sql_where.value, 'WHERE a.w = b.x and a.y = b.z')

        sql_where += 'test1 > test2'
        self.assertEqual(sql_where.value, 'WHERE a.w = b.x and a.y = b.z and test1 > test2')

        sql_where += 'test4 = true'
        self.assertEqual(sql_where.value, 'WHERE a.w = b.x and a.y = b.z and test1 > test2 and test4 = true')


    def test__sql_group_by__init(self):
        from spyql import SQLGroupBy
        must_receive_string_as_input(self, SQLGroupBy)
        sql_class_instance_as_string_has_uppered_class_type(self, SQLGroupBy, 'group by test')

    def test__sql_group_by__add(self):
        from spyql import SQLGroupBy

        sql_group_by = SQLGroupBy('')
        self.assertEqual(sql_group_by.value, None)

        sql_group_by += SQLGroupBy('GROUP BY a.a')
        self.assertEqual(sql_group_by.value, 'GROUP BY a.a')

        sql_group_by += SQLGroupBy('group BY a.b')
        self.assertEqual(sql_group_by.value, 'GROUP BY a.a, a.b')

        sql_group_by += 'GROUP BY a.c'
        self.assertEqual(sql_group_by.value, 'GROUP BY a.a, a.b, a.c')

        sql_group_by += 'a.d'
        self.assertEqual(sql_group_by.value, 'GROUP BY a.a, a.b, a.c, a.d')


    def test__sql_having__init(self):
        from spyql import SQLHaving
        must_receive_string_as_input(self, SQLHaving)
        sql_class_instance_as_string_has_uppered_class_type(self, SQLHaving, 'having by test')

    def test__sql_having__add(self):
        from spyql import SQLHaving

        sql_having = SQLHaving('')
        self.assertEqual(sql_having.value, None)

        sql_having += SQLHaving('HAVING a.w = b.x')
        self.assertEqual(sql_having.value, 'HAVING a.w = b.x')

        sql_having += SQLHaving('having a.y = b.z')
        self.assertEqual(sql_having.value, 'HAVING a.w = b.x and a.y = b.z')

        sql_having += 'test1 > test2'
        self.assertEqual(sql_having.value, 'HAVING a.w = b.x and a.y = b.z and test1 > test2')

        sql_having += 'test4 = true'
        self.assertEqual(sql_having.value, 'HAVING a.w = b.x and a.y = b.z and test1 > test2 and test4 = true')


    def test__sql_order_by__init(self):
        from spyql import SQLOrderBy
        must_receive_string_as_input(self, SQLOrderBy)
        sql_class_instance_as_string_has_uppered_class_type(self, SQLOrderBy, 'order by test')

    def test__sql_order_by__add(self):
        from spyql import SQLOrderBy

        sql_order_by = SQLOrderBy('')
        self.assertEqual(sql_order_by.value, None)

        sql_order_by += SQLOrderBy('ORDER BY a.a')
        self.assertEqual(sql_order_by.value, 'ORDER BY a.a')

        sql_order_by += SQLOrderBy('order BY a.b')
        self.assertEqual(sql_order_by.value, 'ORDER BY a.a, a.b')

        sql_order_by += 'ORDER BY a.c'
        self.assertEqual(sql_order_by.value, 'ORDER BY a.a, a.b, a.c')

        sql_order_by += 'a.d'
        self.assertEqual(sql_order_by.value, 'ORDER BY a.a, a.b, a.c, a.d')


    def test__sql_limit__init(self):
        from spyql import SQLLimit
        must_receive_int_as_input(self, SQLLimit)
        self.assertEqual(SQLLimit('5').as_string, 'LIMIT 5')
        self.assertEqual(SQLLimit('LIMIT 5').as_string, 'LIMIT 5')
        self.assertEqual(SQLLimit('limit 5').as_string, 'LIMIT 5')
        self.assertEqual(SQLLimit(5).as_string, 'LIMIT 5')

    def test__sql_limit__add(self):
        from spyql import SQLLimit

        sql_limit_by = SQLLimit('')
        self.assertEqual(sql_limit_by.value, None)

        sql_limit_by += SQLLimit('LIMIT 50')
        self.assertEqual(sql_limit_by.value, 50)

        with self.assertRaises(ValueError):
            sql_limit_by += SQLLimit('LIMIT 60')

        with self.assertRaises(ValueError):
            sql_limit_by += SQLLimit(60)


    def test__sql_component__init(self):
        import spyql
        def test_sql_component_works_if_expected_type_returns_a_type():
            spyql.SQLComponent.expected_type = property(lambda x: int)
            sql_component = spyql.SQLComponent(5)
            self.assertEqual(sql_component.value, 5)
        test_sql_component_works_if_expected_type_returns_a_type()

        def test_default_sql_component_cannot_be_instantiated():
            reload(spyql)
            with self.assertRaises(NotImplementedError):
                sql_component = spyql.SQLComponent(5)
        test_default_sql_component_cannot_be_instantiated()


    def test__tokenize_sql_component(self):
        from spyql import tokenize_sql_component
        q0 = tokenize_sql_component('')
        q1 = tokenize_sql_component('SELECT s1, s2 FROM f1')
        q2 = tokenize_sql_component('SELECT s1, s2 FROM f1 as ff1, f2 as ff2 WHERE s1=s2 and s2 = s3 GROUP BY date ORDER BY thing LIMIT 1')
        q3 = tokenize_sql_component('SELECT * FROM CUSTOMERS WHERE ID IN (SELECT ID FROM CUSTOMERS WHERE SALARY > 4500) GROUP BY THING HAVING COUNT(TEST) > 4 LIMIT 10')
        q4 = tokenize_sql_component('SELECT sub.* FROM ( SELECT * FROM tutorial.sf_crime_incidents_2014_01 WHERE day_of_week = "Friday" ) sub INNER JOIN calls c WHERE sub.resolution = "NONE" order by pickles')
        qnonsense = tokenize_sql_component('the quick brown fox jumped over the lazy dog')

        self.assertEqual(q0, ['', '', '', '', '', '', ''])
        self.assertEqual(q1, ['s1, s2', 'f1', '', '', '', '', ''])
        self.assertEqual(q2, ['s1, s2', 'f1 as ff1, f2 as ff2', 's1=s2 and s2 = s3', 'date', '', 'thing', '1'])
        self.assertEqual(q3, ['*', 'CUSTOMERS', 'ID IN (SELECT ID FROM CUSTOMERS WHERE SALARY > 4500)', 'THING', 'COUNT(TEST) > 4', '', '10'])
        self.assertEqual(q4, ['sub.*', '( SELECT * FROM tutorial.sf_crime_incidents_2014_01 WHERE day_of_week = "Friday" ) sub INNER JOIN calls c', 'sub.resolution = "NONE"', '', '', 'pickles', ''])
        self.assertEqual(qnonsense, ['', '', '', '', '', '', ''])

    def test__tokenizing_multiline_statement(self):
        from spyql import tokenize_sql_component
        multiline_statement = """
        SELECT field1, field2
        FROM table1
        WHERE field1 IREGEXP '([0-9] ){15}' or field1 IREGEXP '^.*special information .*  [0-9].*' or '^.*also special info .*  [0-9].*'
        and specific > '2018-01-01'
        """
        q = tokenize_sql_component(multiline_statement)
        self.assertEqual(q, ['field1, field2', 'table1', "field1 IREGEXP '([0-9] ){15}' or field1 IREGEXP '^.*special information .*  [0-9].*' or '^.*also special info .*  [0-9].*'         and specific > '2018-01-01'", '', '', '', ''])

    def test__str_method_returns_query(self):
        from spyql import SQL, SQLSelect, SQLFrom, SQLWhere, SQLGroupBy, SQLHaving, SQLOrderBy, SQLLimit

        sql = SQL.from_string('SELECT test FROM other')
        self.assertEqual(str(sql), 'SELECT test FROM other')
        sql_select = SQLSelect('SELECT test1')
        self.assertEqual(str(sql_select), 'SELECT test1')
        sql_from = SQLFrom('FROM test1 as t1')
        self.assertEqual(str(sql_from), 'FROM test1 as t1')
        sql_where = SQLWhere('WHERE a.w = b.x')
        self.assertEqual(str(sql_where), 'WHERE a.w = b.x')
        sql_group_by = SQLGroupBy('GROUP BY a.a')
        self.assertEqual(str(sql_group_by), 'GROUP BY a.a')
        sql_having = SQLHaving('HAVING a.w = b.x')
        self.assertEqual(str(sql_having), 'HAVING a.w = b.x')
        sql_order_by = SQLOrderBy('ORDER BY a.a')
        self.assertEqual(str(sql_order_by), 'ORDER BY a.a')
        sql_limit_by = SQLLimit(50)
        self.assertEqual(str(sql_limit_by), 'LIMIT 50')

def must_receive_string_as_input(testobj, SQLClass):
    must_receive_as_input(testobj, SQLClass, 'test', 5)

def must_receive_int_as_input(testobj, SQLClass):
    must_receive_as_input(testobj, SQLClass, 5, 'test')

def must_receive_as_input(testobj, SQLClass, _input, _counter_input):
    with testobj.assertRaises(ValueError):
        sql_class_instance = SQLClass(_counter_input)
    sql_class_instance = SQLClass(_input)
    testobj.assertEqual(sql_class_instance.value, _input)

def sql_class_instance_as_string_has_uppered_class_type(testobj, SQLClass, value):
    upped_value = get_upper_cased_component_value(value, SQLClass.component_name)
    value_missing_component = value.replace(SQLClass.component_name.lower()+' ', '')
    testobj.assertEqual(SQLClass(value).as_string, upped_value)
    testobj.assertEqual(SQLClass(upped_value).as_string, upped_value)
    testobj.assertEqual(SQLClass(value_missing_component).as_string, upped_value)


if __name__ == '__main__':
    unittest.main(verbosity=2)
    