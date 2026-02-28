# MATRX Pattern System

A robust, efficient system for embedding and fetching database content within text using special MATRX patterns.

## Overview

The MATRX system consists of two main components:
1. **Pattern Recognition** - Parse MATRX patterns from text
2. **Data Fetching** - Fetch database content and replace patterns

## Pattern Syntax

### Basic Pattern
```
<<MATRX>><<TABLE>><<COLUMN>>value<</MATRX>>
```

**Example:**
```
<<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<</MATRX>>
```

### Pattern with Field Specification
```
<<MATRX>><<TABLE>><<COLUMN>>value<<FIELDS>>attribute<</MATRX>>
```

**Example:**
```
<<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<<FIELDS>>label<</MATRX>>
```

### Pattern with Multiple Fields
```
<<MATRX>><<TABLE>><<COLUMN>>value<<FIELDS>>attr1,attr2<</MATRX>>
```

**Example:**
```
<<MATRX>><<CONTENT_BLOCKS>><<CATEGORY_ID>>uuid<<FIELDS>>template,label<</MATRX>>
```

## Components

### 1. Pattern Recognition (`variable_recognition_test.py`)

#### `MatrxPattern` Dataclass
Represents a parsed pattern with:
- `table`: Table name (e.g., "CONTENT_BLOCKS")
- `column`: Column to filter by (e.g., "BLOCK_ID", "ID")
- `value`: Search value
- `field`: Optional field(s) to retrieve
- `raw`: Original pattern string
- `start_pos`, `end_pos`: Position in text

#### `MatrxPatternParser` Class

**Parse all patterns:**
```python
from instructions.tests.variable_recognition_test import MatrxPatternParser

text = "Template: <<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<</MATRX>>"
patterns = MatrxPatternParser.parse(text)

for pattern in patterns:
    print(f"Table: {pattern.table}, Column: {pattern.column}, Value: {pattern.value}")
```

**Find first pattern:**
```python
pattern = MatrxPatternParser.find_first(text)
if pattern:
    print(f"Found: {pattern}")
```

**Replace patterns with custom function:**
```python
def replacer(pattern):
    return f"[{pattern.table}.{pattern.column}={pattern.value}]"

result = MatrxPatternParser.replace_patterns(text, replacer)
```

### 2. Data Fetching (`matrx_fetcher.py`)

#### `MatrxFetcher` Class

**Core fetch method:**
```python
from instructions.matrx_fetcher import MatrxFetcher

# Fetch with default field
content = MatrxFetcher.fetch("CONTENT_BLOCKS", "BLOCK_ID", "flashcards")

# Fetch with specific field
label = MatrxFetcher.fetch("CONTENT_BLOCKS", "BLOCK_ID", "flashcards", field="label")

# Fetch with multiple fields
content = MatrxFetcher.fetch("CONTENT_BLOCKS", "CATEGORY_ID", "uuid", field="template,label")
```

**Table-specific methods:**
```python
# Direct method call
content = MatrxFetcher.fetch_content_blocks("BLOCK_ID", "flashcards")

# With specific field
label = MatrxFetcher.fetch_content_blocks("BLOCK_ID", "flashcards", field="label")

# Multiple results by category
all_content = MatrxFetcher.fetch_content_blocks("CATEGORY_ID", "uuid-here")
```

**Process text with patterns:**
```python
text = "Template: <<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<</MATRX>>"
patterns = MatrxPatternParser.parse(text)
result = MatrxFetcher.process_text_with_patterns(text, patterns)
print(result)  # Pattern replaced with actual content
```

## Usage Examples

### Example 1: Simple Replacement

```python
from instructions.tests.variable_recognition_test import MatrxPatternParser
from instructions.matrx_fetcher import MatrxFetcher

text = """
Use this template:
<<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<</MATRX>>
"""

patterns = MatrxPatternParser.parse(text)
result = MatrxFetcher.process_text_with_patterns(text, patterns)
print(result)
```

### Example 2: Multiple Patterns with Fields

```python
text = """
Block name: <<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<<FIELDS>>label<</MATRX>>

Block template:
<<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<<FIELDS>>template<</MATRX>>
"""

patterns = MatrxPatternParser.parse(text)
result = MatrxFetcher.process_text_with_patterns(text, patterns)
```

### Example 3: Fetch Multiple Records

```python
# Fetches all content blocks in a category
text = """
All blocks:
<<MATRX>><<CONTENT_BLOCKS>><<CATEGORY_ID>>9980e68f-97fc-4f71-bf1d-22583b6cdf38<</MATRX>>
"""

patterns = MatrxPatternParser.parse(text)
result = MatrxFetcher.process_text_with_patterns(text, patterns)
```

### Example 4: Helper Function (All-in-One)

```python
from instructions.tests.integration_test import process_text_with_matrx

text = "Template: <<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<</MATRX>>"
result = process_text_with_matrx(text, verbose=True)
```

## Adding New Tables

To add support for a new table:

### 1. Add Configuration

Edit `matrx_fetcher.py`:

```python
TABLE_CONFIGS = {
    "CONTENT_BLOCKS": {
        "model": ContentBlocks,
        "default_field": "template",
        "supported_fields": ["template", "label", "block_id"],
    },
    "YOUR_TABLE": {
        "model": YourModel,
        "default_field": "name",
        "supported_fields": ["name", "description", "value"],
    },
}
```

### 2. (Optional) Add Specific Method

For custom logic, add a dedicated method:

```python
@classmethod
def fetch_your_table(cls, column: str, value: str, field: Optional[str] = None) -> str:
    """Fetch from your table with custom logic."""
    column = column.lower()
    fields = cls._parse_fields(field, default="name")
    
    query_params = {column: value}
    results = YourModel.filter_sync(**query_params)
    
    # Custom processing here
    output_parts = []
    for result in results:
        for field_name in fields:
            attr_value = getattr(result, field_name, "")
            if attr_value:
                output_parts.append(str(attr_value))
    
    return "\n\n".join(output_parts)
```

## Key Features

✅ **Robust Pattern Matching** - Works anywhere in text, unaffected by surrounding content  
✅ **Optional Field Specification** - Fetch specific attributes or use defaults  
✅ **Multiple Fields** - Comma-separated fields like `template,label`  
✅ **Single or Multiple Results** - Automatically handles both cases  
✅ **Table-Specific Methods** - Each table has optimized handling  
✅ **Error Handling** - Gracefully handles missing data  
✅ **Efficient** - Direct database queries with minimal overhead  
✅ **Extensible** - Easy to add new tables  

## Testing

Run the test suites:

```bash
# Test pattern recognition
python ai/instructions/tests/variable_recognition_test.py

# Test data fetching
python ai/instructions/matrx_fetcher.py

# Test complete integration
python ai/instructions/tests/integration_test.py
```

## Pattern Recognition Rules

1. Patterns can appear **anywhere** in text
2. Patterns are **not affected** by surrounding content
3. Values can contain **any characters** (text, UUIDs, numbers, spaces, etc.)
4. Field specification is **optional**
5. Multiple patterns in the same text are **fully supported**
6. Patterns are **case-insensitive** for table/column names (normalized internally)

## Performance

- **Regex-based** parsing for maximum speed
- **Single query per pattern** - no N+1 issues
- **Efficient string replacement** - processes patterns in reverse order
- **No redundant parsing** - text is parsed once

## Future Enhancements

Potential additions:
- Caching layer for frequently accessed content
- Support for computed fields
- Pattern validation before fetching
- Batch fetching for multiple patterns from same table
- Custom formatters for different content types
