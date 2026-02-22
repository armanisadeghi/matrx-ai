# MATRX Pattern System - Quick Reference

## Pattern Formats

### Basic Pattern (uses default field)
```
<<MATRX>><<TABLE>><<COLUMN>>value<</MATRX>>
```

### With Specific Field
```
<<MATRX>><<TABLE>><<COLUMN>>value<<FIELDS>>attribute<</MATRX>>
```

### With Multiple Fields
```
<<MATRX>><<TABLE>><<COLUMN>>value<<FIELDS>>attr1,attr2<</MATRX>>
```

## Common Patterns

### Content Blocks

```
// Get template (default)
<<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<</MATRX>>

// Get label
<<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<<FIELDS>>label<</MATRX>>

// Get by UUID
<<MATRX>><<CONTENT_BLOCKS>><<ID>>b46e284e-ccb0-4d32-8a96-07f85d50d134<</MATRX>>

// Get all in category
<<MATRX>><<CONTENT_BLOCKS>><<CATEGORY_ID>>9980e68f-97fc-4f71-bf1d-22583b6cdf38<</MATRX>>

// Get multiple fields
<<MATRX>><<CONTENT_BLOCKS>><<CATEGORY_ID>>uuid<<FIELDS>>template,label<</MATRX>>
```

## Quick Code Snippets

### Parse Patterns
```python
from ai.instructions.tests.variable_recognition_test import MatrxPatternParser

patterns = MatrxPatternParser.parse(text)
for p in patterns:
    print(f"{p.table}.{p.column} = {p.value} [field: {p.field}]")
```

### Fetch Data
```python
from ai.instructions.matrx_fetcher import MatrxFetcher

# Simple fetch
content = MatrxFetcher.fetch("CONTENT_BLOCKS", "BLOCK_ID", "flashcards")

# With field
label = MatrxFetcher.fetch("CONTENT_BLOCKS", "BLOCK_ID", "flashcards", "label")

# Table-specific method
content = MatrxFetcher.fetch_content_blocks("BLOCK_ID", "flashcards")
```

### Process Text (All-in-One)
```python
from ai.instructions.tests.variable_recognition_test import MatrxPatternParser
from ai.instructions.matrx_fetcher import MatrxFetcher

patterns = MatrxPatternParser.parse(text)
result = MatrxFetcher.process_text_with_patterns(text, patterns)
```

### Helper Function
```python
from ai.instructions.tests.integration_test import process_text_with_matrx

result = process_text_with_matrx(text, verbose=False)
```

## Pattern Object Structure

```python
@dataclass
class MatrxPattern:
    table: str        # "CONTENT_BLOCKS"
    column: str       # "BLOCK_ID"
    value: str        # "flashcards"
    field: str|None   # "template" or None
    raw: str          # Full original pattern
    start_pos: int    # Position in text
    end_pos: int      # End position in text
```

## Table Configurations

### Current Tables

#### CONTENT_BLOCKS
- **Model:** `ContentBlocks`
- **Default Field:** `template`
- **Supported Fields:** `template`, `label`, `block_id`, `category_id`
- **Common Queries:**
  - By BLOCK_ID: `<<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>name<</MATRX>>`
  - By ID: `<<MATRX>><<CONTENT_BLOCKS>><<ID>>uuid<</MATRX>>`
  - By Category: `<<MATRX>><<CONTENT_BLOCKS>><<CATEGORY_ID>>uuid<</MATRX>>`

## Adding New Tables

1. **Import the model:**
   ```python
   from database.main.models import YourModel
   ```

2. **Add configuration:**
   ```python
   TABLE_CONFIGS = {
       "YOUR_TABLE": {
           "model": YourModel,
           "default_field": "name",
           "supported_fields": ["name", "description"],
       }
   }
   ```

3. **(Optional) Add specific method:**
   ```python
   @classmethod
   def fetch_your_table(cls, column, value, field=None):
       # Custom logic here
       pass
   ```

## Testing Commands

```bash
# Test pattern recognition
python ai/instructions/tests/variable_recognition_test.py

# Test data fetching
python ai/instructions/matrx_fetcher.py

# Test full integration
python ai/instructions/tests/integration_test.py
```

## Tips & Best Practices

✅ **Always specify table name in UPPERCASE** - Normalized internally but clearer  
✅ **Column names are case-insensitive** - Will be normalized to lowercase  
✅ **Field specification is optional** - Defaults are configured per table  
✅ **Multiple fields use commas** - No spaces: `template,label`  
✅ **UUIDs work directly** - No special handling needed  
✅ **Patterns work anywhere** - Surrounded by any text  

⚠️ **Don't use special characters in pattern delimiters** - Only in values  
⚠️ **Field must exist on model** - Will return empty if not found  
⚠️ **Table must be configured** - Add to TABLE_CONFIGS first  

## Error Handling

```python
# Fetcher catches errors gracefully
result = MatrxFetcher.process_text_with_patterns(text, patterns)
# Returns: "[FETCH_ERROR: ...]" if fetch fails
```

## Real-World Example

```python
# Input text with multiple patterns
text = """
# AI Instructions

Use flashcard template:
<<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<</MATRX>>

Block name: <<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<<FIELDS>>label<</MATRX>>

All interactive blocks:
<<MATRX>><<CONTENT_BLOCKS>><<CATEGORY_ID>>9980e68f-97fc-4f71-bf1d-22583b6cdf38<<FIELDS>>label<</MATRX>>
"""

# Process
from ai.instructions.tests.integration_test import process_text_with_matrx
result = process_text_with_matrx(text)

# Result has all patterns replaced with actual database content
```
