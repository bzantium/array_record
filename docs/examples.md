# Examples

This section provides practical examples of using ArrayRecord in various scenarios, from basic file operations to advanced machine learning workflows.

## Basic File Operations

### Writing and Reading Simple Data

```python
from array_record.python import array_record_module, array_record_data_source

# Writing data
writer = array_record_module.ArrayRecordWriter('simple_data.array_record')

# Write different types of data
data_samples = [
    b"Hello, ArrayRecord!",
    b"This is record 2",
    b"Binary data: \x00\x01\x02\x03",
    "Unicode text: 你好".encode('utf-8')
]

for data in data_samples:
    writer.write(data)

writer.close()

# Reading data back
with array_record_data_source.ArrayRecordDataSource('simple_data.array_record') as ds:
    print(f"Total records: {len(ds)}")
    
    for i in range(len(ds)):
        record = ds[i]
        print(f"Record {i}: {record}")
```

### Working with JSON Data

```python
import json
from array_record.python import array_record_module, array_record_data_source

# Sample data
users = [
    {"id": 1, "name": "Alice", "age": 30, "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "age": 25, "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "age": 35, "email": "charlie@example.com"},
]

# Writing JSON data
writer = array_record_module.ArrayRecordWriter('users.array_record')

for user in users:
    json_bytes = json.dumps(user).encode('utf-8')
    writer.write(json_bytes)

writer.close()

# Reading JSON data
with array_record_data_source.ArrayRecordDataSource('users.array_record') as ds:
    for i in range(len(ds)):
        json_bytes = ds[i]
        user = json.loads(json_bytes.decode('utf-8'))
        print(f"User {user['id']}: {user['name']} ({user['age']} years old)")
```

## Machine Learning Examples

### Storing Image Data

```python
import numpy as np
import json
from array_record.python import array_record_module, array_record_data_source
from PIL import Image
import io

def create_image_dataset():
    """Create a dataset with images and metadata."""
    writer = array_record_module.ArrayRecordWriter(
        'image_dataset.array_record',
        'group_size:100,brotli:6'  # Optimize for image data
    )
    
    # Generate sample images
    for i in range(1000):
        # Create a simple colored image
        image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        
        # Convert to PNG bytes
        pil_image = Image.fromarray(image)
        img_buffer = io.BytesIO()
        pil_image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        # Create record with image and metadata
        record = {
            'image_data': img_bytes.hex(),  # Store as hex string
            'width': 64,
            'height': 64,
            'channels': 3,
            'label': i % 10,  # Simple label
            'filename': f'image_{i:04d}.png'
        }
        
        writer.write(json.dumps(record).encode('utf-8'))
    
    writer.close()
    print("Image dataset created!")

def read_image_dataset():
    """Read and process the image dataset."""
    with array_record_data_source.ArrayRecordDataSource('image_dataset.array_record') as ds:
        print(f"Dataset contains {len(ds)} images")
        
        # Read a few samples
        for i in range(5):
            record_bytes = ds[i]
            record = json.loads(record_bytes.decode('utf-8'))
            
            # Decode image
            img_bytes = bytes.fromhex(record['image_data'])
            image = Image.open(io.BytesIO(img_bytes))
            
            print(f"Image {i}: {record['filename']}, "
                  f"size: {record['width']}x{record['height']}, "
                  f"label: {record['label']}")

# Create and read the dataset
create_image_dataset()
read_image_dataset()
```

### Text Processing with Embeddings

```python
import numpy as np
import json
from array_record.python import array_record_module, array_record_data_source

def create_text_embedding_dataset():
    """Create a dataset with text and embeddings."""
    writer = array_record_module.ArrayRecordWriter(
        'text_embeddings.array_record',
        'group_size:1000,brotli:9'  # High compression for text
    )
    
    # Sample texts
    texts = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is transforming technology",
        "ArrayRecord provides efficient data storage",
        "Natural language processing enables understanding",
        "Deep learning models require large datasets"
    ]
    
    for i, text in enumerate(texts * 200):  # Repeat for larger dataset
        # Simulate text embedding (normally from a model like BERT)
        embedding = np.random.randn(768).astype(np.float32)  # 768-dim embedding
        
        record = {
            'id': i,
            'text': text,
            'embedding': embedding.tolist(),  # Convert to list for JSON
            'length': len(text),
            'word_count': len(text.split())
        }
        
        writer.write(json.dumps(record).encode('utf-8'))
    
    writer.close()
    print(f"Text embedding dataset created with {len(texts) * 200} records!")

def search_similar_texts(query_embedding, top_k=5):
    """Find similar texts using cosine similarity."""
    query_embedding = np.array(query_embedding)
    similarities = []
    
    with array_record_data_source.ArrayRecordDataSource('text_embeddings.array_record') as ds:
        for i in range(len(ds)):
            record_bytes = ds[i]
            record = json.loads(record_bytes.decode('utf-8'))
            
            embedding = np.array(record['embedding'])
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            
            similarities.append((similarity, record))
    
    # Sort by similarity and return top-k
    similarities.sort(key=lambda x: x[0], reverse=True)
    return similarities[:top_k]

# Create dataset and search
create_text_embedding_dataset()

# Example search
query = np.random.randn(768).astype(np.float32)
results = search_similar_texts(query, top_k=3)

print("Top similar texts:")
for similarity, record in results:
    print(f"Similarity: {similarity:.4f}, Text: {record['text'][:50]}...")
```

## Apache Beam Examples

### Large-Scale Data Conversion

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from array_record.beam.pipelines import convert_tf_to_arrayrecord_gcs

def convert_large_dataset():
    """Convert a large TFRecord dataset to ArrayRecord on GCS."""
    
    # Configure pipeline for large dataset
    pipeline_options = PipelineOptions([
        '--runner=DataflowRunner',
        '--project=my-project',
        '--region=us-central1',
        '--temp_location=gs://my-bucket/temp',
        '--staging_location=gs://my-bucket/staging',
        '--max_num_workers=50',
        '--worker_machine_type=n1-standard-4',
        '--disk_size_gb=100'
    ])
    
    # Run conversion
    pipeline = convert_tf_to_arrayrecord_gcs(
        overwrite_extension=True,
        file_path_suffix='.array_record',
        args=[
            '--input', 'gs://large-dataset/tfrecords/*.tfrecord',
            '--output', 'gs://processed-dataset/arrayrecords/'
        ],
        pipeline_options=pipeline_options
    )
    
    result = pipeline.run()
    result.wait_until_finish()
    print("Conversion completed!")

# Run the conversion
convert_large_dataset()
```

### Custom Beam Pipeline

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from array_record.python import array_record_module
import tempfile
import json

class ProcessAndWriteArrayRecordDoFn(beam.DoFn):
    """Custom DoFn to process data and write ArrayRecord files."""
    
    def process(self, element):
        batch_id, records = element
        
        # Create temporary ArrayRecord file
        with tempfile.NamedTemporaryFile(suffix='.array_record', delete=False) as tmp_file:
            writer = array_record_module.ArrayRecordWriter(
                tmp_file.name,
                'group_size:1000,brotli:6'
            )
            
            processed_count = 0
            for record in records:
                # Process each record
                processed_record = self.process_record(record)
                writer.write(json.dumps(processed_record).encode('utf-8'))
                processed_count += 1
            
            writer.close()
            
            yield {
                'batch_id': batch_id,
                'file_path': tmp_file.name,
                'record_count': processed_count
            }
    
    def process_record(self, record):
        """Apply custom processing to each record."""
        # Example: add processing timestamp and normalize text
        processed = {
            'original': record,
            'processed_text': record.get('text', '').lower().strip(),
            'word_count': len(record.get('text', '').split()),
            'processing_timestamp': beam.utils.timestamp.Timestamp.now().to_utc_datetime().isoformat()
        }
        return processed

def run_custom_pipeline():
    """Run a custom pipeline that processes data and creates ArrayRecord files."""
    
    # Sample input data
    sample_data = [
        {'id': 1, 'text': 'Hello World', 'category': 'greeting'},
        {'id': 2, 'text': 'Machine Learning', 'category': 'tech'},
        {'id': 3, 'text': 'Data Processing', 'category': 'tech'},
    ] * 100  # Repeat for larger dataset
    
    pipeline_options = PipelineOptions(['--runner=DirectRunner'])
    
    with beam.Pipeline(options=pipeline_options) as pipeline:
        # Create input data
        input_data = pipeline | 'CreateData' >> beam.Create(sample_data)
        
        # Group into batches
        batched_data = (
            input_data 
            | 'AddKeys' >> beam.Map(lambda x: (x['category'], x))
            | 'GroupByCategory' >> beam.GroupByKey()
            | 'CreateBatches' >> beam.Map(lambda x: (x[0], list(x[1])))
        )
        
        # Process and write ArrayRecord files
        results = (
            batched_data 
            | 'ProcessAndWrite' >> beam.ParDo(ProcessAndWriteArrayRecordDoFn())
        )
        
        # Output results
        results | 'PrintResults' >> beam.Map(
            lambda x: print(f"Processed batch {x['batch_id']}: "
                          f"{x['record_count']} records -> {x['file_path']}")
        )

run_custom_pipeline()
```

## Performance Optimization Examples

### Optimizing for Different Access Patterns

```python
from array_record.python import array_record_module, array_record_data_source
import time
import random

def create_test_dataset(filename, num_records=10000):
    """Create a test dataset for performance testing."""
    writer = array_record_module.ArrayRecordWriter(filename)
    
    for i in range(num_records):
        data = f"Record {i}: " + "x" * random.randint(100, 1000)
        writer.write(data.encode('utf-8'))
    
    writer.close()

def benchmark_sequential_access(filename):
    """Benchmark sequential access performance."""
    print("Benchmarking sequential access...")
    
    # Default settings (optimized for sequential access)
    start_time = time.time()
    
    with array_record_data_source.ArrayRecordDataSource(filename) as ds:
        total_bytes = 0
        for i in range(len(ds)):
            record = ds[i]
            total_bytes += len(record)
    
    end_time = time.time()
    
    print(f"Sequential access: {end_time - start_time:.2f}s, "
          f"{total_bytes / (1024*1024):.2f} MB processed")

def benchmark_random_access(filename):
    """Benchmark random access performance."""
    print("Benchmarking random access...")
    
    # Settings optimized for random access
    reader_options = {
        'readahead_buffer_size': '0',
        'max_parallelism': '0'
    }
    
    start_time = time.time()
    
    with array_record_data_source.ArrayRecordDataSource(
        filename, reader_options=reader_options
    ) as ds:
        # Random access pattern
        total_bytes = 0
        indices = random.sample(range(len(ds)), min(1000, len(ds)))
        
        for idx in indices:
            record = ds[idx]
            total_bytes += len(record)
    
    end_time = time.time()
    
    print(f"Random access: {end_time - start_time:.2f}s, "
          f"{total_bytes / (1024*1024):.2f} MB processed")

def benchmark_batch_access(filename):
    """Benchmark batch access performance."""
    print("Benchmarking batch access...")
    
    start_time = time.time()
    
    with array_record_data_source.ArrayRecordDataSource(filename) as ds:
        batch_size = 100
        total_bytes = 0
        
        for start_idx in range(0, len(ds), batch_size):
            end_idx = min(start_idx + batch_size, len(ds))
            indices = list(range(start_idx, end_idx))
            
            batch = ds[indices]
            for record in batch:
                total_bytes += len(record)
    
    end_time = time.time()
    
    print(f"Batch access: {end_time - start_time:.2f}s, "
          f"{total_bytes / (1024*1024):.2f} MB processed")

# Run performance benchmarks
test_file = 'performance_test.array_record'
create_test_dataset(test_file)

benchmark_sequential_access(test_file)
benchmark_random_access(test_file)
benchmark_batch_access(test_file)
```

### Compression Comparison

```python
from array_record.python import array_record_module, array_record_data_source
import os
import time

def test_compression_options(data, base_filename):
    """Test different compression options."""
    
    compression_options = [
        ('uncompressed', 'uncompressed'),
        ('snappy', 'snappy'),
        ('brotli_fast', 'brotli:1'),
        ('brotli_default', 'brotli:6'),
        ('brotli_max', 'brotli:11'),
        ('zstd_fast', 'zstd:1'),
        ('zstd_default', 'zstd:3'),
        ('zstd_max', 'zstd:22'),
    ]
    
    results = []
    
    for name, options in compression_options:
        filename = f"{base_filename}_{name}.array_record"
        
        # Write with compression
        start_time = time.time()
        writer = array_record_module.ArrayRecordWriter(filename, options)
        
        for item in data:
            writer.write(item.encode('utf-8'))
        
        writer.close()
        write_time = time.time() - start_time
        
        # Check file size
        file_size = os.path.getsize(filename)
        
        # Read back (for read performance)
        start_time = time.time()
        with array_record_data_source.ArrayRecordDataSource(filename) as ds:
            for i in range(len(ds)):
                _ = ds[i]
        read_time = time.time() - start_time
        
        results.append({
            'name': name,
            'write_time': write_time,
            'read_time': read_time,
            'file_size_mb': file_size / (1024 * 1024),
            'compression_ratio': file_size / results[0]['file_size_mb'] if results else 1.0
        })
        
        print(f"{name:15} | Write: {write_time:6.2f}s | "
              f"Read: {read_time:6.2f}s | Size: {file_size/(1024*1024):7.2f} MB")
    
    return results

# Generate test data
test_data = []
for i in range(5000):
    # Mix of repetitive and random data
    if i % 2 == 0:
        data = f"Repetitive data entry {i % 100}: " + "Lorem ipsum " * 20
    else:
        data = f"Random entry {i}: " + os.urandom(200).hex()
    test_data.append(data)

print("Compression Performance Comparison")
print("=" * 70)
print(f"{'Method':<15} | {'Write Time':<12} | {'Read Time':<11} | {'File Size'}")
print("-" * 70)

results = test_compression_options(test_data, 'compression_test')
```

## Integration Examples

### Using with TensorFlow

```python
import tensorflow as tf
from array_record.python import array_record_data_source
import json

def create_tf_compatible_dataset():
    """Create ArrayRecord dataset compatible with TensorFlow."""
    from array_record.python import array_record_module
    
    writer = array_record_module.ArrayRecordWriter('tf_dataset.array_record')
    
    # Create sample data similar to tf.data format
    for i in range(1000):
        # Simulate image classification data
        features = {
            'image': tf.random.normal([224, 224, 3]).numpy().tolist(),
            'label': i % 10,
            'id': i
        }
        writer.write(json.dumps(features).encode('utf-8'))
    
    writer.close()

def create_tf_dataset_from_arrayrecord(filename):
    """Create TensorFlow dataset from ArrayRecord file."""
    
    def generator():
        with array_record_data_source.ArrayRecordDataSource(filename) as ds:
            for i in range(len(ds)):
                record_bytes = ds[i]
                record = json.loads(record_bytes.decode('utf-8'))
                
                # Convert back to tensors
                image = tf.constant(record['image'], dtype=tf.float32)
                label = tf.constant(record['label'], dtype=tf.int32)
                
                yield {'image': image, 'label': label}
    
    # Create TensorFlow dataset
    dataset = tf.data.Dataset.from_generator(
        generator,
        output_signature={
            'image': tf.TensorSpec(shape=[224, 224, 3], dtype=tf.float32),
            'label': tf.TensorSpec(shape=[], dtype=tf.int32)
        }
    )
    
    return dataset

# Create and use TensorFlow dataset
create_tf_compatible_dataset()
tf_dataset = create_tf_dataset_from_arrayrecord('tf_dataset.array_record')

# Use in training pipeline
tf_dataset = tf_dataset.batch(32).prefetch(tf.data.AUTOTUNE)

print("TensorFlow dataset created from ArrayRecord:")
for batch in tf_dataset.take(1):
    print(f"Batch shape - Images: {batch['image'].shape}, Labels: {batch['label'].shape}")
```

### Using with PyTorch

```python
import torch
from torch.utils.data import Dataset, DataLoader
from array_record.python import array_record_data_source
import json
import numpy as np

class ArrayRecordDataset(Dataset):
    """PyTorch Dataset wrapper for ArrayRecord files."""
    
    def __init__(self, filename, transform=None):
        self.filename = filename
        self.transform = transform
        
        # Open data source
        self.data_source = array_record_data_source.ArrayRecordDataSource(filename)
        self.length = len(self.data_source)
    
    def __len__(self):
        return self.length
    
    def __getitem__(self, idx):
        # Read record
        record_bytes = self.data_source[idx]
        record = json.loads(record_bytes.decode('utf-8'))
        
        # Convert to PyTorch tensors
        image = torch.tensor(record['image'], dtype=torch.float32)
        label = torch.tensor(record['label'], dtype=torch.long)
        
        if self.transform:
            image = self.transform(image)
        
        return image, label
    
    def __del__(self):
        # Clean up
        if hasattr(self, 'data_source'):
            self.data_source.__exit__(None, None, None)

def create_pytorch_dataloader():
    """Create PyTorch DataLoader from ArrayRecord file."""
    
    # Create dataset
    dataset = ArrayRecordDataset('tf_dataset.array_record')  # Reuse from TF example
    
    # Create DataLoader
    dataloader = DataLoader(
        dataset,
        batch_size=32,
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )
    
    return dataloader

# Use with PyTorch
dataloader = create_pytorch_dataloader()

print("PyTorch DataLoader created from ArrayRecord:")
for batch_idx, (images, labels) in enumerate(dataloader):
    print(f"Batch {batch_idx}: Images shape: {images.shape}, Labels shape: {labels.shape}")
    if batch_idx >= 2:  # Just show first few batches
        break
```

## Advanced Use Cases

### Multi-Modal Data Storage

```python
import json
import base64
from array_record.python import array_record_module, array_record_data_source

def create_multimodal_dataset():
    """Create a dataset with multiple data modalities."""
    
    writer = array_record_module.ArrayRecordWriter(
        'multimodal_dataset.array_record',
        'group_size:100,brotli:6'
    )
    
    for i in range(500):
        # Simulate multi-modal record
        record = {
            'id': i,
            'text': f"This is sample text for item {i}",
            'image_data': base64.b64encode(np.random.bytes(1024)).decode('utf-8'),  # Fake image
            'audio_features': np.random.randn(128).tolist(),  # Audio features
            'metadata': {
                'timestamp': f"2024-01-{(i % 30) + 1:02d}T10:00:00Z",
                'source': 'synthetic',
                'quality_score': np.random.uniform(0.5, 1.0)
            },
            'labels': {
                'category': ['tech', 'science', 'art'][i % 3],
                'sentiment': np.random.choice(['positive', 'negative', 'neutral']),
                'confidence': np.random.uniform(0.7, 0.99)
            }
        }
        
        writer.write(json.dumps(record).encode('utf-8'))
    
    writer.close()
    print("Multi-modal dataset created!")

def query_multimodal_dataset(category_filter=None, min_quality=0.8):
    """Query the multi-modal dataset with filters."""
    
    results = []
    
    with array_record_data_source.ArrayRecordDataSource('multimodal_dataset.array_record') as ds:
        for i in range(len(ds)):
            record_bytes = ds[i]
            record = json.loads(record_bytes.decode('utf-8'))
            
            # Apply filters
            if category_filter and record['labels']['category'] != category_filter:
                continue
            
            if record['metadata']['quality_score'] < min_quality:
                continue
            
            results.append(record)
    
    return results

# Create and query multi-modal dataset
create_multimodal_dataset()

# Query examples
tech_records = query_multimodal_dataset(category_filter='tech', min_quality=0.9)
print(f"Found {len(tech_records)} high-quality tech records")

for record in tech_records[:3]:
    print(f"ID: {record['id']}, Text: {record['text'][:50]}...")
    print(f"Quality: {record['metadata']['quality_score']:.3f}, "
          f"Sentiment: {record['labels']['sentiment']}")
    print()
```

## MaxText LLM Training Integration

This example shows how to use ArrayRecord with [MaxText](https://github.com/AI-Hypercomputer/maxtext) for efficient large language model training, leveraging Grain for data processing:

```python
import json
import numpy as np
import grain
from array_record.python import array_record_module, array_record_data_source

def create_llm_pretraining_dataset():
    """Create a large-scale pretraining dataset for LLMs using ArrayRecord."""
    
    # Use group_size:1 for maximum random access performance during training
    writer = array_record_module.ArrayRecordWriter(
        'llm_pretraining.array_record',
        'group_size:1,brotli:6'  # Fast random access + moderate compression
    )
    
    # Simulate tokenized text data (replace with your actual tokenizer)
    vocab_size = 32000
    max_sequence_length = 2048
    
    # Generate sample training data
    num_examples = 100000
    
    for i in range(num_examples):
        # Simulate tokenized text sequence
        sequence_length = np.random.randint(512, max_sequence_length + 1)
        input_ids = np.random.randint(1, vocab_size, size=sequence_length).tolist()
        
        # Create training example
        example = {
            'input_ids': input_ids,
            'attention_mask': [1] * sequence_length,  # All tokens are real
            'position_ids': list(range(sequence_length)),
            'sequence_length': sequence_length,
            'document_id': f"doc_{i // 100}",  # Multiple sequences per document
            'metadata': {
                'source': 'web_crawl' if i % 3 == 0 else 'books',
                'language': 'en',
                'quality_score': np.random.uniform(0.7, 1.0)
            }
        }
        
        # Write as JSON bytes
        writer.write(json.dumps(example).encode('utf-8'))
        
        if i % 10000 == 0:
            print(f"Created {i:,} training examples...")
    
    writer.close()
    print(f"✅ Created LLM pretraining dataset with {num_examples:,} examples")

def create_maxtext_data_pipeline(
    data_path: str,
    batch_size: int = 128,
    max_sequence_length: int = 2048,
    shuffle_buffer_size: int = 10000
):
    """Create MaxText-compatible data pipeline using ArrayRecord + Grain."""
    
    # ArrayRecord data source - optimized for random access
    data_source = array_record_data_source.ArrayRecordDataSource(data_path)
    print(f"📊 Loaded dataset with {len(data_source):,} examples")
    
    def parse_and_process_example(raw_bytes):
        """Parse JSON and prepare for training."""
        example = json.loads(raw_bytes.decode('utf-8'))
        
        # Extract sequences
        input_ids = example['input_ids']
        attention_mask = example['attention_mask']
        
        # Pad or truncate to max_sequence_length
        if len(input_ids) > max_sequence_length:
            input_ids = input_ids[:max_sequence_length]
            attention_mask = attention_mask[:max_sequence_length]
        else:
            padding_length = max_sequence_length - len(input_ids)
            input_ids.extend([0] * padding_length)  # 0 = PAD token
            attention_mask.extend([0] * padding_length)  # 0 = ignore
        
        # For causal LM, labels are input_ids shifted by 1
        labels = input_ids[1:] + [-100]  # -100 = ignore in loss
        
        return {
            'input_ids': np.array(input_ids, dtype=np.int32),
            'attention_mask': np.array(attention_mask, dtype=np.int32),
            'labels': np.array(labels, dtype=np.int32),
            'sequence_length': example['sequence_length']
        }
    
    def quality_filter(example_bytes):
        """Filter examples by quality score."""
        example = json.loads(example_bytes.decode('utf-8'))
        return example['metadata']['quality_score'] > 0.8
    
    # Create Grain dataset pipeline (MaxText style)
    dataset = (
        grain.MapDataset.source(data_source)
        .filter(quality_filter)  # Filter high-quality examples
        .map(parse_and_process_example)  # Parse and pad sequences
        .shuffle(seed=42, buffer_size=shuffle_buffer_size)  # Shuffle for training
        .batch(batch_size)  # Batch for efficient training
        .prefetch(4)  # Prefetch batches to prevent data loading bottlenecks
    )
    
    return dataset

def simulate_maxtext_training_loop():
    """Simulate MaxText training loop with ArrayRecord data pipeline."""
    
    print("🚀 Starting MaxText-style LLM training simulation...")
    
    # Create pretraining dataset
    create_llm_pretraining_dataset()
    
    # Create data pipeline
    train_dataset = create_maxtext_data_pipeline(
        'llm_pretraining.array_record',
        batch_size=64,  # Adjust based on your hardware
        max_sequence_length=1024,
        shuffle_buffer_size=50000
    )
    
    # Training loop
    total_tokens = 0
    
    for step, batch in enumerate(train_dataset):
        # Batch shapes:
        # - input_ids: [batch_size, sequence_length]
        # - attention_mask: [batch_size, sequence_length]
        # - labels: [batch_size, sequence_length]
        
        batch_size, seq_len = batch['input_ids'].shape
        tokens_in_batch = np.sum(batch['attention_mask'])  # Count non-padded tokens
        total_tokens += tokens_in_batch
        
        print(f"Step {step:,}: "
              f"Batch size={batch_size}, "
              f"Seq len={seq_len}, "
              f"Tokens={tokens_in_batch:,}, "
              f"Total tokens={total_tokens:,}")
        
        # In real MaxText training, you would:
        # 1. Forward pass through the model
        # 2. Compute loss (cross-entropy on labels)
        # 3. Backward pass and optimizer step
        # 4. Log metrics and checkpoints
        
        # Example pseudo-code:
        # logits = model(batch['input_ids'], batch['attention_mask'])
        # loss = compute_cross_entropy_loss(logits, batch['labels'])
        # loss.backward()
        # optimizer.step()
        
        if step >= 100:  # Demo: stop after 100 steps
            break
    
    print(f"✅ Training simulation completed!")
    print(f"📈 Processed {total_tokens:,} tokens across {step + 1} steps")

def benchmark_random_access_performance():
    """Benchmark random access performance with different configurations."""
    
    print("🔬 Benchmarking ArrayRecord configurations for LLM training...")
    
    import time
    
    # Test different configurations
    configs = [
        ('group_size:1', 'Maximum random access'),
        ('group_size:100,brotli:6', 'Balanced performance'),
        ('group_size:1000,brotli:9', 'Maximum compression')
    ]
    
    for config, description in configs:
        print(f"\n📊 Testing: {description} ({config})")
        
        # Create test dataset
        filename = f'benchmark_{config.replace(":", "_").replace(",", "_")}.array_record'
        writer = array_record_module.ArrayRecordWriter(filename, config)
        
        # Write test data
        for i in range(10000):
            example = {
                'input_ids': list(range(i, i + 512)),  # 512 tokens
                'labels': list(range(i + 1, i + 513))
            }
            writer.write(json.dumps(example).encode('utf-8'))
        writer.close()
        
        # Benchmark random access
        data_source = array_record_data_source.ArrayRecordDataSource(filename)
        
        # Random access test
        indices = np.random.randint(0, len(data_source), size=1000)
        
        start_time = time.time()
        for idx in indices:
            _ = data_source[idx]
        random_access_time = time.time() - start_time
        
        print(f"  Random access: {random_access_time:.3f}s for 1000 reads")
        print(f"  Avg per read: {random_access_time * 1000 / 1000:.3f}ms")

# Run the complete example
if __name__ == "__main__":
    simulate_maxtext_training_loop()
    benchmark_random_access_performance()
```

### Key Benefits for LLM Training

**🚀 Performance Advantages:**
- **Ultra-fast random access** with `group_size:1` for efficient shuffling
- **Parallel data loading** doesn't bottleneck GPU training
- **Memory efficient** - only loads needed data, crucial for large models
- **Scalable** to datasets with billions of tokens

**🔧 MaxText Integration:**
- **Seamless Grain compatibility** for data pipeline composition
- **Flexible preprocessing** with map/filter/batch operations
- **Quality filtering** and data validation built-in
- **Production-ready** - used by Google's MaxText for real LLM training

**📊 Real-world Usage:**
Based on the [MaxText implementation](https://github.com/AI-Hypercomputer/maxtext/blob/main/src/MaxText/input_pipeline/_grain_data_processing.py), this pattern is used for training large language models with:
- Datasets containing billions of tokens
- Efficient random sampling for training stability
- High-throughput data loading to keep GPUs/TPUs busy
- Flexible data preprocessing and augmentation

This combination of ArrayRecord + Grain + MaxText provides a production-ready solution for large-scale language model training.

This comprehensive set of examples covers the major use cases for ArrayRecord, from basic file operations to advanced machine learning workflows and integrations with popular frameworks. Each example includes practical code that can be adapted for specific needs.
