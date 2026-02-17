# IETF Standards Compliance

## RFC Compliance

| RFC | Title | Status |
|-----|-------|--------|
| RFC 8259 | JSON | ✅ |
| RFC 6901 | JSON Pointer | ✅ |
| RFC 6902 | JSON Patch | ✅ |
| RFC 7231 | HTTP/1.1 | ✅ |
| RFC 7540 | HTTP/2 | ✅ |
| RFC 8446 | TLS 1.3 | ✅ |

## JSON Standards

### RFC 8259 - JSON

```json
{
  "valid": true,
  "data": {
    "name": "example",
    "value": 42
  }
}
```

### RFC 6901 - JSON Pointer

```
/person/name
/address/street
/items/0/id
```

### RFC 6902 - JSON Patch

```json
[
  {"op": "add", "path": "/name", "value": "New"},
  {"op": "remove", "path": "/old"},
  {"op": "replace", "path": "/status", "value": "active"}
]
```

## HTTP Standards

### Content Negotiation

```http
Accept: application/json
Accept-Language: en-US
```

### CORS

```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Headers: Content-Type
```

## URI Standards

### RFC 3986

```
https://api.example.com/v1/users?id=123
```

## Security

### OAuth 2.0 (RFC 6749)

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### JWT (RFC 7519)

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```
