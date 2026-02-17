# W3C Standards Compliance

## Overview

This document outlines compliance with W3C standards relevant to schema definition and data interchange.

## JSON Schema

### Draft 2020-12 Support

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/schemas/user",
  "title": "User Schema",
  "type": "object"
}
```

### Supported Features

- ✅ `$schema` declaration
- ✅ `$id` for identification
- ✅ `$ref` and `$defs` for references
- ✅ `allOf`, `anyOf`, `oneOf` for composition
- ✅ `if-then-else` for conditional schemas
- ✅ `unevaluatedProperties` for strict validation

## JSON-LD

### Linked Data Support

```json
{
  "@context": {
    "schema": "http://schema.org/",
    "name": "schema:name",
    "email": "schema:email"
  },
  "@type": "schema:Person",
  "name": "John Doe",
  "email": "john@example.com"
}
```

### Context Definitions

| Prefix | URI | Description |
|--------|-----|-------------|
| schema | <http://schema.org/> | Schema.org vocabulary |
| rdfs | <http://www.w3.org/2000/01/rdf-schema#> | RDF Schema |
| owl | <http://www.w3.org/2002/07/owl#> | Web Ontology Language |
| xsd | <http://www.w3.org/2001/XMLSchema#> | XML Schema Datatypes |

## RDF and OWL

### RDF Triple Support

```turtle
@prefix schema: <http://schema.org/> .
@prefix ex: <https://example.com/> .

ex:user-1 a schema:Person ;
    schema:name "Alice" ;
    schema:email "alice@example.com" .
```

### OWL Class Definitions

```owl
Prefix: schema: <http://schema.org/>
Prefix: ex: <https://example.com/>

Class: ex:User
  SubClassOf: schema:Person

ObjectProperty: ex:hasRole
  Domain: ex:User
  Range: ex:Role
```

## XML Schema Datatypes

### XSD Type Mapping

| XSD Type | JSON Schema Type | Format |
|----------|-----------------|--------|
| xs:string | string | - |
| xs:integer | integer | - |
| xs:decimal | number | - |
| xs:boolean | boolean | - |
| xs:date | string | date |
| xs:dateTime | string | date-time |
| xs:anyURI | string | uri |

## Linked Data Platform (LDP)

### Container Patterns

```http
GET /api/resources/ HTTP/1.1
Host: example.com
Accept: text/turtle

HTTP/1.1 200 OK
Content-Type: text/turtle

@prefix ldp: <http://www.w3.org/ns/ldp#> .

<> a ldp:BasicContainer ;
   ldp:contains <resource1>, <resource2> .
```

## SHACL (Shapes Constraint Language)

### Shape Definitions

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <https://example.com/> .

ex:UserShape a sh:NodeShape ;
    sh:targetClass ex:User ;
    sh:property [
        sh:path ex:email ;
        sh:datatype xsd:string ;
        sh:pattern "^[^@]+@[^@]+$" ;
        sh:minCount 1 ;
    ] ;
    sh:property [
        sh:path ex:age ;
        sh:datatype xsd:integer ;
        sh:minInclusive 0 ;
        sh:maxInclusive 150 ;
    ] .
```

## SPARQL Query Support

### Schema-Driven Queries

```sparql
PREFIX schema: <http://schema.org/>
PREFIX ex: <https://example.com/>

SELECT ?user ?name ?email
WHERE {
    ?user a ex:User ;
          schema:name ?name ;
          schema:email ?email .
    FILTER (strstarts(?email, "admin@"))
}
```

## Validation Report

```json
{
  "@context": "https://www.w3.org/ns/shacl#",
  "@type": "ValidationReport",
  "conforms": false,
  "result": [
    {
      "@type": "ValidationResult",
      "focusNode": "ex:user-1",
      "resultPath": "schema:email",
      "resultSeverity": "sh:Violation",
      "resultMessage": "Invalid email format"
    }
  ]
}
```

## Compliance Checklist

- [x] JSON Schema Draft 2020-12
- [x] JSON-LD 1.1
- [x] RDF 1.1
- [x] OWL 2
- [x] SHACL
- [x] LDP
- [x] XSD Datatypes
- [x] SPARQL 1.1
