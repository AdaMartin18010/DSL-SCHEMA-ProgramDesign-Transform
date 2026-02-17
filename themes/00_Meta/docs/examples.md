# Examples

## Basic Validation

```python
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"}
    }
}

data = {"name": "Alice"}
```

## Advanced Schema

```python
schema = {
    "type": "object",
    "properties": {
        "user": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"}
            }
        }
    }
}
```
