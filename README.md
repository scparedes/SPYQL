# SPYQL
A library for handling SQL-like queries with light input validation and basic arithmetic support for combining queries.

## Working with SPYQL
The way SPYQL works is by chunking the highest level pre-defined components of a SQL query (SELECT, FROM, WHERE, etc.) into attributes of a SPYQL SQL object.
```python
>>> from spyql import SQL
>>> query = 'SELECT a.*, b.* FROM apples a inner join bananas b using (c,d) WHERE length(a.y) != length(b.z) and length(a.y) > 2 GROUP BY a.y HAVING count(a.y)<5 ORDER BY b.z LIMIT 15'
>>> sql = SQL.from_string(query)
>>> sql._select
<spyql.SQLSelect object at 0x100d29750>
>>> sql._from
<spyql.SQLFrom object at 0x100d29850>
```
Each component can be individually converted into a string:
```python
>>> sql._select.as_string
'SELECT a.*, b.*'
>>> sql._from.as_string
'FROM apples a inner join bananas b using (a,b)'
```
All the components can be retrieved at once and formatted at the highest level too:
```python
>>> sql.as_string
'SELECT a.*, b.* FROM apples a inner join bananas b using (a,b) WHERE length(a.y) != length(b.z) and length(a.y) > 2 GROUP BY a.y HAVING count(a.y)<5 ORDER BY b.z LIMIT 15'
```
### Component Addition
You can use SPYQL to build complex queries by adding SQL objects together:
```python
from spyql import SQL, SQLWhere

sql = SQL.from_string('SELECT a FROM b')
assert sql.as_string == 'SELECT a FROM b'

sql += SQL.from_string('SELECT c FROM d')
assert sql.as_string == 'SELECT a, c FROM b, d'

sql += SQLWhere('a > c')
assert sql.as_string == 'SELECT a, c FROM b, d WHERE a > c'
```
SPYQL can handle compound/sub-queries too:
```python
query_with_nests = 'select k from (select k from ztab left outer join ytab using (date)) tabk where k in (select k from ytab where k > 5)'
sql += SQL.from_string(query_with_nests)
assert sql.as_string, 'SELECT a, c, k FROM b, d, (select k from ztab left outer join ytab using (date)) tabk WHERE a > c and k in (select k from ytab where k > 5)'
```
#### More on that...
Here's a demo of repeatedly adding smaller constraints and entire SQL objects to `specific_sql` (with intermediate states being printed along the way):
```python
from spyql import SQL, SQLWhere, SQLLimit, SQLGroupBy, SQLHaving, SQLFrom

unaltered_sql = SQL.from_string('SELECT a FROM b')
sql = unaltered_sql + SQLWhere("date >= '2018-01-01'") + SQLLimit(100)
print sql.as_string
# SELECT a FROM b WHERE date >= '2018-01-01' LIMIT 100

sql += SQL.from_string('SELECT c FROM d')
print sql.as_string
# SELECT a, c FROM b, d WHERE date >= '2018-01-01' LIMIT 100

sql += SQLGroupBy('a, c')
print sql.as_string
# SELECT a, c FROM b, d WHERE date >= '2018-01-01' GROUP BY a, c LIMIT 100

sql += SQLHaving('a > 1')
print sql.as_string
# SELECT a, c FROM b, d WHERE date >= '2018-01-01' GROUP BY a, c HAVING a > 1 LIMIT 100

sql += SQLHaving('a < 5')
print sql.as_string
# SELECT a, c FROM b, d WHERE date >= '2018-01-01' GROUP BY a, c HAVING a > 1 and a < 5 LIMIT 100

sql += SQLFrom('e ex')
sql += SQLFrom('from f') # <---- leading 'from' will be stripped from SQL object to circumvent syntactic/semantic issues (all components are handled similarly)
print sql.as_string
# SELECT a, c FROM b, d, e ex, f WHERE date >= '2018-01-01' GROUP BY a, c HAVING a > 1 and a < 5 LIMIT 100

sql += SQLFrom('INNER JOIN test t USING (common_attribute)')
print sql.as_string
# SELECT a, c FROM b, d, e ex, f INNER JOIN test t USING (common_attribute) WHERE date >= '2018-01-01' GROUP BY a, c HAVING a > 1 and a < 5 LIMIT 100
```

## Why SPYQL?
I made SPYQL to pull myself out of the mire of low-level string manipulation for building SQL-like queries.  Instead I wanted to deal with a more robust OOP-inspired interface.  I'll be updating SPYQL as needs demand and time allows.

Oh, and the name? SP for my initials, PY for python, QL for paying respects to SQL, i.e. pronounced spy-quill or spy-queue-ell.

## The Gritty Details
For fuller understanding of current capabilities/limitations, I recommend referring to the unit tests in `test_spyql.py` and `spyql.py` itself.
