"""
USL语法定义

使用EBNF定义USL语法
"""

USL_GRAMMAR = """
start: schema

schema: "schema" identifier "{" schema_body "}"

schema_body: (type_definition | field_definition | constraint_definition | relation_definition | metadata_definition)*

type_definition: "type" identifier ":" type_specifier constraint_clause?

type_specifier: primitive_type | composite_type | reference_type

primitive_type: "String" | "Integer" | "Float" | "Boolean" | "Date" | "DateTime" | "Decimal"

composite_type: "Array" "<" type_specifier ">" 
              | "Map" "<" type_specifier "," type_specifier ">" 
              | "Object" "{" field_definition* "}"

reference_type: identifier

field_definition: "field" identifier ":" type_specifier constraint_clause? default_clause?

constraint_clause: "{" constraint* "}"

constraint: "required" ":" boolean
          | "min" ":" number
          | "max" ":" number
          | "pattern" ":" string
          | "enum" ":" "[" value ("," value)* "]"
          | "format" ":" string
          | "minLength" ":" number
          | "maxLength" ":" number
          | "precision" ":" number

default_clause: "default" ":" value

relation_definition: "relation" identifier ":" relation_type "(" identifier "," identifier ")"

relation_type: "one_to_one" | "one_to_many" | "many_to_many"

metadata_definition: "metadata" "{" metadata_item* "}"

metadata_item: identifier ":" value

identifier: /[a-zA-Z_][a-zA-Z0-9_]*/

boolean: "true" | "false"

number: /-?\d+(\.\d+)?/

string: /"[^"]*"/

value: string | number | boolean | "null"

%import common.WS
%ignore WS
"""
