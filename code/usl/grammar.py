"""
USL语法定义

使用EBNF定义USL语法
"""

USL_GRAMMAR = """
start: schema

schema: "schema" IDENTIFIER "{" schema_body "}"

schema_body: (schema_element)*

schema_element: type_definition
             | field_definition
             | constraint_definition
             | relation_definition
             | metadata_definition

type_definition: "type" IDENTIFIER ":" type_specifier type_constraints?

type_specifier: primitive_type
             | array_type
             | map_type
             | IDENTIFIER

primitive_type: "String" -> string_type
             | "Integer" -> integer_type
             | "Float" -> float_type
             | "Boolean" -> boolean_type
             | "Date" -> date_type
             | "DateTime" -> datetime_type
             | "Decimal" -> decimal_type

array_type: "Array" "<" type_specifier ">"

map_type: "Map" "<" type_specifier "," type_specifier ">"

field_definition: "field" IDENTIFIER ":" type_specifier field_constraints?

type_constraints: "{" type_constraint* "}"

type_constraint: "constraint" ":" STRING
               | "format" ":" STRING
               | "enum" ":" "[" value ("," value)* "]"

field_constraints: "{" field_constraint* "}"

field_constraint: "required" ":" BOOLEAN
               | "default" ":" value
               | "min" ":" NUMBER
               | "max" ":" NUMBER
               | "pattern" ":" STRING
               | "enum" ":" "[" value ("," value)* "]"
               | "format" ":" STRING
               | "minLength" ":" NUMBER
               | "maxLength" ":" NUMBER
               | "precision" ":" NUMBER

constraint_definition: "constraint" IDENTIFIER "{" constraint_body "}"

constraint_body: constraint_item ("," constraint_item)*

constraint_item: IDENTIFIER ":" value

relation_definition: "relation" IDENTIFIER ":" relation_type "(" IDENTIFIER "," IDENTIFIER ")"

relation_type: "one_to_one" -> one_to_one
             | "one_to_many" -> one_to_many
             | "many_to_many" -> many_to_many

metadata_definition: "metadata" "{" metadata_item* "}"

metadata_item: IDENTIFIER ":" value

value: STRING | NUMBER | BOOLEAN | NULL

// 词法规则
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/

BOOLEAN.2: "true" | "false"

NULL.2: "null"

NUMBER: /-?\d+(\.\d+)?/

STRING: /"[^"]*"/

%import common.WS
%ignore WS
"""
