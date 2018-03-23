# SPYQL
Custom library for SQL-like queries with light input validation and basic support for the addition operator.

## Working with SPYQL
The way SPYQL works is by chunking the highest level pre-defined components of a SQL query (SELECT, FROM, WHERE, etc.) into attributes of a SPYQL SQL object.
```python
>>> from spyql import SQL
...
>>> query = 'SELECT a.*, b.* FROM apples a inner join bananas b using (a,b) WHERE length(a.y) != length(b.z) and length(a.y) > 2 GROUP BY a.y HAVING count(a.y)<5 ORDER BY b.z LIMIT 15'
...
>>> sql = SQL.from_string(query)
...
>>> sql._select
<spyql.SQLSelect object at 0x100d29750>
>>> sql._select.as_string
'SELECT a.*, b.*'
>>> sql._from
<spyql.SQLFrom object at 0x100d29850>
>>> sql._from.as_string
'FROM apples a inner join bananas b using (a,b)'
...
>>> sql.as_string
'SELECT a.*, b.* FROM apples a inner join bananas b using (a,b) WHERE length(a.y) != length(b.z) and length(a.y) > 2 GROUP BY a.y HAVING count(a.y)<5 ORDER BY b.z LIMIT 15'
```
### Component Addition
You can use SPYQL to build compound queries.  Say, for instance, you had a base query and you wanted to add some constraints:
```python
from spyql import SQL, SQLWhere, SQLLimit

base_query = 'SELECT a FROM b'
general_sql = SQL.from_string(base_query)
specific_sql = general_sql + SQLWhere("date >= '2018-01-01'") + SQLLimit(100)

print specific_sql.as_string
# SELECT a FROM b WHERE date >= '2018-01-01' LIMIT 100
```
Finally here's a demo of adding entire SQL objects to `specific_sql` and repeatedly adding smaller constraints to `specific_sql` as well:
```python
...
from spyql import SQLGroupBy, SQLHaving, SQLFrom

specific_sql += SQL.from_string('SELECT c FROM d')
print specific_sql.as_string
# SELECT a, c FROM b, d WHERE date >= '2018-01-01' LIMIT 100

specific_sql += SQLGroupBy('a, c')
print specific_sql.as_string
# SELECT a, c FROM b, d WHERE date >= '2018-01-01' GROUP BY a, c LIMIT 100

specific_sql += SQLHaving('a > 1')
print specific_sql.as_string
# SELECT a, c FROM b, d WHERE date >= '2018-01-01' GROUP BY a, c HAVING a > 1 LIMIT 100

specific_sql += SQLHaving('a < 5')
print specific_sql.as_string
# SELECT a, c FROM b, d WHERE date >= '2018-01-01' GROUP BY a, c HAVING a > 1 and a < 5 LIMIT 100

specific_sql += SQLFrom('e ex')
specific_sql += SQLFrom('from f') # <---- leading 'from', as any leading component keyword, will be stripped from SQL object
print specific_sql.as_string
# SELECT a, c FROM b, d, e ex, f WHERE date >= '2018-01-01' GROUP BY a, c HAVING a > 1 and a < 5 LIMIT 100

specific_sql += SQLFrom('INNER JOIN test t USING (common_attribute)')
print specific_sql.as_string
# SELECT a, c FROM b, d, e ex, f INNER JOIN test t USING (common_attribute) WHERE date >= '2018-01-01' GROUP BY a, c HAVING a > 1 and a < 5 LIMIT 100
```

## Why SPYQL?
I made SPYQL to pull myself out of the mire of low-level string manipulation for building SQL-like queries.  Instead I wanted to deal with a more robust OOP-inspired interface.  I'll be updating SPYQL as needs demand and time allows.

## The Gritty Details
For fuller understanding of current capabilities/limitations, I recommend referring to the unit tests in `test_spyql.py` and `spyql.py` itself.