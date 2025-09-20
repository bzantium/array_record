# ArrayRecord Python - High-Performance Data Storage for ML

[![PyPI version](https://badge.fury.io/py/array-record-python.svg)](https://badge.fury.io/py/array-record-python)
[![Python](https://img.shields.io/pypi/pyversions/array-record-python.svg)](https://pypi.org/project/array-record-python/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation](https://readthedocs.org/projects/arrayrecord/badge/?version=latest)](https://arrayrecord.readthedocs.io/en/latest/?badge=latest)

**ArrayRecord** is a high-performance file format designed for machine learning workloads, offering parallel I/O, random access by record index, and efficient compression. Built on top of [Riegeli](https://github.com/google/riegeli), ArrayRecord provides a new frontier of IO efficiency for training and evaluating ML models.

## ✨ Key Features

- **🚀 High Performance**: Optimized for both sequential and random access patterns
- **⚡ Parallel I/O**: Built-in support for concurrent read and write operations  
- **🎯 Random Access**: Efficient access to any record by index without full file scanning
- **🗜️ Advanced Compression**: Multiple algorithms (Brotli, Zstd, Snappy) with configurable levels
- **📊 Apache Beam Integration**: Seamless integration for large-scale data processing
- **🌍 Cross-Platform**: Available for Linux (x86_64, aarch64) and macOS (aarch64)
- **🔧 Framework Integration**: Works with TensorFlow, JAX, PyTorch, and more

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install array-record-python

# With Apache Beam support for large-scale processing
pip install array-record-python[beam]

# With all optional dependencies
pip install array-record-python[beam,test]
```

> **Note**: This is a source distribution that includes Python bindings and Apache Beam integration. The C++ components need to be built separately using Bazel. For pre-compiled binaries, consider using the original `array_record` package or building from source following the [development guide](#-development).

### Basic Usage

ArrayRecord provides a simple and intuitive API for high-performance data storage:

```python
from array_record.python import array_record_module, array_record_data_source

# Writing data
writer = array_record_module.ArrayRecordWriter('dataset.array_record')
for i in range(1000):
    data = f"Record {i}".encode('utf-8')
    writer.write(data)
writer.close()

# Reading data with random access
with array_record_data_source.ArrayRecordDataSource('dataset.array_record') as ds:
    print(f"Dataset contains {len(ds)} records")
    
    # Random access
    record_100 = ds[100]
    
    # Batch access
    batch = ds[[10, 50, 100, 500]]
    
    # Sequential access
    for i in range(len(ds)):
        record = ds[i]
```

### Performance Optimization

Configure ArrayRecord for your specific use case:

```python
# High compression for storage efficiency
writer = array_record_module.ArrayRecordWriter(
    'compressed.array_record',
    'group_size:10000,brotli:9,max_parallelism:4'
)

# Optimized for random access
reader_options = {
    'readahead_buffer_size': '0',
    'max_parallelism': '0'
}
ds = array_record_data_source.ArrayRecordDataSource(
    'dataset.array_record',
    reader_options=reader_options
)

# High throughput sequential processing
reader_options = {
    'readahead_buffer_size': '64MB',
    'max_parallelism': '8'
}
```

## 📊 Apache Beam Integration

Process large datasets efficiently with Apache Beam:

```python
import apache_beam as beam
from array_record.beam.pipelines import convert_tf_to_arrayrecord_gcs

# Convert TFRecords to ArrayRecord on Google Cloud
pipeline = convert_tf_to_arrayrecord_gcs(
    args=[
        '--input', 'gs://source-bucket/tfrecords/*',
        '--output', 'gs://dest-bucket/arrayrecords/'
    ],
    pipeline_options=beam.options.pipeline_options.PipelineOptions([
        '--runner=DataflowRunner',
        '--project=my-project',
        '--region=us-central1'
    ])
)
pipeline.run().wait_until_finish()
```

## 🔧 Framework Integration

### TensorFlow

```python
import tensorflow as tf
from array_record.python import array_record_data_source

def create_tf_dataset(filename):
    def generator():
        with array_record_data_source.ArrayRecordDataSource(filename) as ds:
            for i in range(len(ds)):
                record = ds[i]
                # Process record as needed
                yield record
    
    return tf.data.Dataset.from_generator(
        generator,
        output_signature=tf.TensorSpec(shape=(), dtype=tf.string)
    )

dataset = create_tf_dataset('data.array_record')
dataset = dataset.batch(32).prefetch(tf.data.AUTOTUNE)
```

### JAX/Grain

ArrayRecord works seamlessly with [Grain](https://github.com/google/grain) for JAX workflows:

```python
import grain
from array_record.python import array_record_data_source

# Use ArrayRecord as a Grain data source
data_source = array_record_data_source.ArrayRecordDataSource('data.array_record')

dataset = (
    grain.MapDataset.source(data_source)
    .shuffle(seed=42)
    .map(lambda x: process_record(x))
    .batch(batch_size=32)
)

for batch in dataset:
    # Training step
    pass
```

### PyTorch

```python
import torch
from torch.utils.data import Dataset, DataLoader
from array_record.python import array_record_data_source

class ArrayRecordDataset(Dataset):
    def __init__(self, filename):
        self.data_source = array_record_data_source.ArrayRecordDataSource(filename)
    
    def __len__(self):
        return len(self.data_source)
    
    def __getitem__(self, idx):
        record = self.data_source[idx]
        # Process record as needed
        return record

dataset = ArrayRecordDataset('data.array_record')
dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4)
```

## 🏗️ File Format and Architecture

ArrayRecord files are organized for optimal performance:

```
┌─────────────────────┐
│    User Data        │  ← Your records, compressed in chunks
│  Riegeli Chunk 1    │
├─────────────────────┤
│    User Data        │
│  Riegeli Chunk 2    │
├─────────────────────┤
│       ...           │
├─────────────────────┤
│   Footer Chunk      │  ← Index for random access
│  (Index Data)       │
├─────────────────────┤
│   Postscript        │  ← File metadata (64KB)
│ (File Metadata)     │
└─────────────────────┘
```

### Key Concepts

- **Records**: Basic units of data (any binary data, protocol buffers, etc.)
- **Chunks**: Groups of records compressed together (configurable group size)
- **Index**: Enables O(1) random access to any record
- **Compression**: Multiple algorithms with different speed/size trade-offs

## ⚡ Performance Guide

### Access Patterns

| Pattern | Configuration | Use Case |
|---------|---------------|----------|
| **Sequential** | `readahead_buffer_size: 16MB`<br/>`max_parallelism: auto` | Training loops, data validation |
| **Random** | `readahead_buffer_size: 0`<br/>`max_parallelism: 0` | Inference, sampling, debugging |
| **Batch** | `readahead_buffer_size: 4MB`<br/>`max_parallelism: 2` | Mini-batch processing |

### Compression Comparison

| Algorithm | Ratio | Speed | Use Case |
|-----------|-------|-------|----------|
| **Uncompressed** | 1.0x | ⚡⚡⚡⚡ | Maximum speed |
| **Snappy** | 2-4x | ⚡⚡⚡ | High throughput |
| **Brotli (default)** | 4-6x | ⚡⚡ | Balanced |
| **Zstd** | 4-6x | ⚡⚡⚡ | Fast alternative |
| **Brotli (max)** | 5-7x | ⚡ | Maximum compression |

### Benchmarking

```python
import time
from array_record.python import array_record_data_source

def benchmark_access_pattern(filename, access_pattern='sequential'):
    start_time = time.time()
    
    if access_pattern == 'sequential':
        reader_options = {'readahead_buffer_size': '16MB'}
    else:  # random
        reader_options = {'readahead_buffer_size': '0', 'max_parallelism': '0'}
    
    with array_record_data_source.ArrayRecordDataSource(
        filename, reader_options=reader_options
    ) as ds:
        if access_pattern == 'sequential':
            for i in range(len(ds)):
                _ = ds[i]
        else:  # random
            import random
            indices = random.sample(range(len(ds)), 1000)
            for idx in indices:
                _ = ds[idx]
    
    elapsed = time.time() - start_time
    print(f"{access_pattern.title()} access: {elapsed:.2f}s")

# Benchmark your data
benchmark_access_pattern('your_data.array_record', 'sequential')
benchmark_access_pattern('your_data.array_record', 'random')
```

## 🌍 Platform Support

| Platform | x86_64 | aarch64 |
|----------|--------|---------|
| **Linux** | ✅ | ✅ |
| **macOS** | ❌ | ✅ |
| **Windows** | ❌ | ❌ |

## 📚 Examples and Use Cases

### Machine Learning Datasets

```python
import json
from array_record.python import array_record_module

# Store structured ML data
def create_ml_dataset(output_file, samples):
    writer = array_record_module.ArrayRecordWriter(
        output_file,
        'group_size:1000,brotli:6'  # Balanced compression
    )
    
    for sample in samples:
        # Store as JSON for flexibility
        record = {
            'features': sample['features'],
            'label': sample['label'],
            'metadata': sample.get('metadata', {})
        }
        writer.write(json.dumps(record).encode('utf-8'))
    
    writer.close()

# Usage
samples = [
    {'features': [1.0, 2.0, 3.0], 'label': 0, 'metadata': {'id': 'sample_1'}},
    {'features': [4.0, 5.0, 6.0], 'label': 1, 'metadata': {'id': 'sample_2'}},
    # ... more samples
]
create_ml_dataset('ml_dataset.array_record', samples)
```

### Large-Scale Data Processing

```python
import apache_beam as beam
from array_record.beam.arrayrecordio import WriteToArrayRecord

# Process and store large datasets
with beam.Pipeline() as pipeline:
    # Read from various sources
    data = (
        pipeline 
        | 'ReadCSV' >> beam.io.ReadFromText('gs://bucket/data/*.csv')
        | 'ParseCSV' >> beam.Map(parse_csv_line)
        | 'ProcessData' >> beam.Map(process_record)
        | 'SerializeRecords' >> beam.Map(lambda x: json.dumps(x).encode('utf-8'))
    )
    
    # Write to ArrayRecord
    data | WriteToArrayRecord(
        file_path_prefix='gs://output-bucket/processed/data',
        file_name_suffix='.array_record',
        num_shards=100
    )
```

### Multi-Modal Data Storage

```python
import base64
from array_record.python import array_record_module

def store_multimodal_data(output_file, samples):
    writer = array_record_module.ArrayRecordWriter(output_file)
    
    for sample in samples:
        record = {
            'text': sample['text'],
            'image_data': base64.b64encode(sample['image_bytes']).decode(),
            'audio_features': sample['audio_features'],
            'labels': sample['labels']
        }
        writer.write(json.dumps(record).encode('utf-8'))
    
    writer.close()
```

## 📖 Documentation

- **[Full Documentation](https://arrayrecord.readthedocs.io)** - Complete API reference and guides
- **[Quick Start Guide](https://arrayrecord.readthedocs.io/en/latest/quickstart.html)** - Get started quickly
- **[Performance Guide](https://arrayrecord.readthedocs.io/en/latest/performance.html)** - Optimization strategies
- **[Apache Beam Integration](https://arrayrecord.readthedocs.io/en/latest/beam_integration.html)** - Large-scale processing
- **[Examples](https://arrayrecord.readthedocs.io/en/latest/examples.html)** - Real-world use cases

## 🛠️ Development

### Building from Source

```bash
# Clone the repository
git clone https://github.com/bzantium/array_record.git
cd array_record

# Install development dependencies
pip install -e .[test,beam]

# Build C++ components (requires Bazel)
bazel build //...

# Run tests
bazel test //...
pytest python/ -v
```

### Contributing

We welcome contributions! Please see our [Contributing Guide](https://arrayrecord.readthedocs.io/en/latest/contributing.html) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 🐛 Issues and Support

- **[Bug Reports](https://github.com/bzantium/array_record/issues)** - Report bugs or request features
- **[Discussions](https://github.com/bzantium/array_record/discussions)** - Ask questions and share ideas
- **[Documentation Issues](https://github.com/bzantium/array_record/issues/new?labels=documentation)** - Help improve our docs

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of [Riegeli](https://github.com/google/riegeli) compression library
- Inspired by [Grain](https://github.com/google/grain) for JAX data processing
- Originally developed by the Google ArrayRecord team
- Enhanced and maintained by the community

## 🔗 Related Projects

- **[Grain](https://github.com/google/grain)** - JAX-focused data processing library
- **[TensorFlow](https://www.tensorflow.org/)** - Machine learning framework with tf.data integration
- **[Apache Beam](https://beam.apache.org/)** - Unified programming model for batch and streaming data
- **[Riegeli](https://github.com/google/riegeli)** - Fast and efficient file format

---

**ArrayRecord Python** - Making high-performance data storage accessible for machine learning workflows.

*Star ⭐ this repository if you find it useful!*