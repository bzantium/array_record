# Quick Start Guide

This guide will help you get started with ArrayRecord quickly. ArrayRecord is designed to be simple to use while providing high performance for both sequential and random access patterns.

## Basic Writing and Reading

### Writing Your First ArrayRecord File

```python
from array_record.python import array_record_module

# Create a writer with default settings
writer = array_record_module.ArrayRecordWriter('my_data.array_record')

# Write some records
for i in range(1000):
    data = f"Record number {i}".encode('utf-8')
    writer.write(data)

# Always close the writer to finalize the file
writer.close()
```

### Reading ArrayRecord Files

```python
from array_record.python import array_record_data_source

# Create a data source for reading
data_source = array_record_data_source.ArrayRecordDataSource('my_data.array_record')

# Get the total number of records
print(f"Total records: {len(data_source)}")

# Read the first record
first_record = data_source[0]
print(f"First record: {first_record.decode('utf-8')}")

# Read multiple records by index
batch = data_source[[0, 10, 100, 500]]
for i, record in enumerate(batch):
    print(f"Record: {record.decode('utf-8')}")
```

## Working with Binary Data

ArrayRecord excels at storing binary data like serialized protocol buffers:

```python
import json
from array_record.python import array_record_module

# Writing JSON data as bytes
writer = array_record_module.ArrayRecordWriter('json_data.array_record')

data_objects = [
    {"id": 1, "name": "Alice", "score": 95.5},
    {"id": 2, "name": "Bob", "score": 87.2},
    {"id": 3, "name": "Charlie", "score": 92.8},
]

for obj in data_objects:
    json_bytes = json.dumps(obj).encode('utf-8')
    writer.write(json_bytes)

writer.close()

# Reading JSON data back
from array_record.python import array_record_data_source

data_source = array_record_data_source.ArrayRecordDataSource('json_data.array_record')

for i in range(len(data_source)):
    json_bytes = data_source[i]
    obj = json.loads(json_bytes.decode('utf-8'))
    print(f"Object {i}: {obj}")
```

## Configuration Options

### Writer Options

ArrayRecord provides several configuration options for optimization:

```python
from array_record.python import array_record_module

# Configure writer options
options = {
    'group_size': '1000',      # Records per chunk (affects compression vs random access trade-off)
    'compression': 'brotli:6', # Compression algorithm and level
}

writer = array_record_module.ArrayRecordWriter(
    'optimized.array_record',
    ','.join([f'{k}:{v}' for k, v in options.items()])
)

# Write data...
writer.close()
```

### Reader Options

```python
from array_record.python import array_record_data_source

# Configure reader options for different access patterns
reader_options = {
    'readahead_buffer_size': '0',  # Disable readahead for pure random access
    'max_parallelism': '4',        # Number of parallel threads
}

data_source = array_record_data_source.ArrayRecordDataSource(
    'optimized.array_record',
    reader_options=reader_options
)
```

## Performance Tips

### Sequential Access

For sequential reading, use the default settings:

```python
# Default settings are optimized for sequential access
data_source = array_record_data_source.ArrayRecordDataSource('data.array_record')

# Iterate through all records
for i in range(len(data_source)):
    record = data_source[i]
    # Process record...
```

### Random Access

For random access, disable readahead:

```python
# Optimize for random access
reader_options = {
    'readahead_buffer_size': '0',
    'max_parallelism': '0',
}

data_source = array_record_data_source.ArrayRecordDataSource(
    'data.array_record',
    reader_options=reader_options
)

# Random access is now optimized
import random
indices = random.sample(range(len(data_source)), 100)
batch = data_source[indices]
```

### Batch Processing

Read multiple records at once for better performance:

```python
data_source = array_record_data_source.ArrayRecordDataSource('data.array_record')

# Process in batches
batch_size = 100
total_records = len(data_source)

for start in range(0, total_records, batch_size):
    end = min(start + batch_size, total_records)
    indices = list(range(start, end))
    batch = data_source[indices]
    
    # Process batch...
    for record in batch:
        # Process individual record...
        pass
```

## Context Manager Usage

Use context managers for automatic resource cleanup:

```python
from array_record.python import array_record_data_source

# Automatically handles cleanup
with array_record_data_source.ArrayRecordDataSource('data.array_record') as data_source:
    # Read data...
    for i in range(min(10, len(data_source))):
        record = data_source[i]
        print(f"Record {i}: {len(record)} bytes")
# File is automatically closed
```

## Error Handling

Always handle potential errors:

```python
from array_record.python import array_record_module, array_record_data_source

try:
    # Writing
    writer = array_record_module.ArrayRecordWriter('output.array_record')
    writer.write(b'test data')
    writer.close()
    
    # Reading
    data_source = array_record_data_source.ArrayRecordDataSource('output.array_record')
    record = data_source[0]
    print(f"Successfully read: {record}")
    
except Exception as e:
    print(f"Error: {e}")
```

## Next Steps

- Learn about [Core Concepts](core_concepts.md) for deeper understanding
- Explore [Python API Reference](python_reference.rst) for complete API documentation
- Check out [Apache Beam Integration](beam_integration.md) for large-scale processing
- See [Examples](examples.md) for real-world use cases
