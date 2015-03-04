import base64
import os

def generate_random_token():
    "Generates a random 24 byte string"
    return base64.b64encode(os.urandom(24))

from sqlalchemy import Integer, ex
from sqlalchemy.ext.compiler import compiles
class date_diff(expression.FunctionElement):
    type = Integer()
    name = 'age'

@compiles(date_diff, 'default')
def _default_date_diff(element, compiler, **kw):  # pragma: no cover
    return "DATEDIFF(%s, %s)" % (compiler.process(element.clauses.clauses[0]),
                                 compiler.process(element.clauses.clauses[1]),
                                 )
@compiles(date_diff, 'mysql')
def _my_date_diff(element, compiler, **kw):  # pragma: no cover
    return "DATEDIFF(%s, %s)" % (compiler.process(element.clauses.clauses[0]),
                                 compiler.process(element.clauses.clauses[1]),
                                 )

@compiles(date_diff, 'sqlite')
def _sl_date_diff(element, compiler, **kw):    # pragma: no cover
    return "julianday(%s) - julianday(%s)" % (compiler.process(element.clauses.clauses[0]),
                                              compiler.process(element.clauses.clauses[1]),
                                              )