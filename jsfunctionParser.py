# jsonParser.py
#
# Implementation of a simple JSON parser, returning a hierarchical
# ParseResults object support both list- and dict-style data access.
#
# Copyright 2006, by Paul McGuire
#
# Updated 8 Jan 2007 - fixed dict grouping bug, and made elements and
#   members optional in array and object collections
#
json_bnf = """
object 
    { members } 
    {} 
members 
    string : value 
    members , string : value 
array 
    [ elements ]
    [] 
elements 
    value 
    elements , value 
value 
    string
    number
    object
    array
    true
    false
    null
"""

from pyparsing import *

TRUE = Keyword("true").setParseAction( replaceWith(True) )
FALSE = Keyword("false").setParseAction( replaceWith(False) )
NULL = Keyword("null").setParseAction( replaceWith(None) )

jsonString = quotedString.setParseAction( removeQuotes )
jsonNumber = Combine( Optional('-') + ( '0' | Word('123456789',nums) ) +
                    Optional( '.' + Word(nums) ) +
                    Optional( Word('eE',exact=1) + Word(nums+'+-',nums) ) )

jsonObject = Forward()
jsonArray = Forward()
jsonValue = Forward()
jsonElements = delimitedList( jsonValue )
jsonArray1 = Group(Suppress('[') + Optional(jsonElements) + Suppress(']') )
jsonArray2 = Group(Suppress(CaselessLiteral('new'))+Suppress(White())+Suppress(CaselessLiteral('array(')) + Optional(jsonElements) + Suppress(')') )
jsonArray << ( jsonArray1 | jsonArray2 )
jsonValue << ( jsonString | jsonNumber | Group(jsonObject)  | jsonArray | TRUE | FALSE | NULL )
memberDef = Group( jsonString + Suppress(':') + jsonValue )
jsonMembers = delimitedList( memberDef )
jsonObject << Dict( Suppress('{') + Optional(jsonMembers) + Suppress('}') )
jsFunctionName = Word(alphas + "_.",  alphanums + "_.")
jsFunctionCall = jsFunctionName+Suppress("(")+Group(Optional(jsonElements))+Suppress(")"+Optional(";"))

jsonComment = cppStyleComment 
jsonObject.ignore( jsonComment )

def convertNumbers(s,l,toks):
    n = toks[0]
    try:
        return int(n)
    except ValueError, ve:
        return float(n)
        
jsonNumber.setParseAction( convertNumbers )

def parser_js_function_call(string):
    return jsFunctionCall.parseString(string).asList()
    
if __name__ == "__main__":
    testdata = """queryUrl(1,'3BC3BEC436094736BF19350711D4A5556F4B7536','123806924','[Dymy][Nurarihyon_no_Mago_Sennen_Makyou][18v2][BIG5][RV10][848x480].rmvb','0',new Array('[Dymy][Nurarihyon_no_Mago_Sennen_Makyou][18v2][BIG5][RV10][848x480].rmvb'),new Array('118M'),new Array('123806924'),new Array('1'),new Array('RMVB'),new Array('0'),'13206731991951250210.5123566347')"""
    testdata1 = """ queryCid('4E1FA9C76605CA8E77DD35DA08D817617403BF26', '87B9431F2F5606721BD761FAA5638A809DAF3080', '8055706', 'hbzz.rar', 0, 0, 0,'13206731991951250210.5123566347','rar')"""
    testdata2 = """ parent.begin_task_batch_resp()"""
    import pprint
    pprint.pprint( parser_js_function_call(testdata) )
    pprint.pprint( parser_js_function_call(testdata1) )
    pprint.pprint( parser_js_function_call(testdata2) )
