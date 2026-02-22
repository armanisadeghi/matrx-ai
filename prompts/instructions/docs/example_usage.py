"""
MATRX Pattern System - Simple Usage Examples

Copy these patterns to get started quickly.
"""

from prompts.instructions.tests.variable_recognition_test import MatrxPatternParser
from prompts.instructions.matrx_fetcher import MatrxFetcher


# ============================================================================
# Example 1: Simple Pattern Parsing
# ============================================================================

def example_parse_patterns():
    """Parse MATRX patterns from text."""
    print("\n" + "=" * 80)
    print("Example 1: Parse Patterns")
    print("=" * 80)
    
    text = """
    Get the flashcard template:
    <<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<</MATRX>>
    
    And the label:
    <<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<<FIELDS>>label<</MATRX>>
    """
    
    patterns = MatrxPatternParser.parse(text)
    
    print(f"\nFound {len(patterns)} pattern(s):")
    for i, pattern in enumerate(patterns, 1):
        print(f"\n{i}. Table:  {pattern.table}")
        print(f"   Column: {pattern.column}")
        print(f"   Value:  {pattern.value}")
        print(f"   Field:  {pattern.field or '(default)'}")


# ============================================================================
# Example 2: Fetch Data Directly
# ============================================================================

def example_fetch_data():
    """Fetch data using the MatrxFetcher."""
    print("\n" + "=" * 80)
    print("Example 2: Fetch Data")
    print("=" * 80)
    
    # Fetch with default field (template)
    print("\n[Fetch 1] Default field:")
    content = MatrxFetcher.fetch_content_blocks("BLOCK_ID", "flashcards")
    print(content[:100] + "...")  # First 100 chars
    
    # Fetch specific field (label)
    print("\n[Fetch 2] Specific field (label):")
    label = MatrxFetcher.fetch_content_blocks("BLOCK_ID", "flashcards", field="label")
    print(label)
    
    # Fetch by UUID
    print("\n[Fetch 3] By UUID:")
    content = MatrxFetcher.fetch_content_blocks(
        "ID", "b46e284e-ccb0-4d32-8a96-07f85d50d134"
    )
    print(content[:100] + "...")


# ============================================================================
# Example 3: Process Text (Replace Patterns)
# ============================================================================

def example_process_text():
    """Parse and replace patterns in text."""
    print("\n" + "=" * 80)
    print("Example 3: Process Text (Replace Patterns)")
    print("=" * 80)
    
    text = """
# Flashcard Instructions

Use this structure:
<<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<<FIELDS>>label<</MATRX>>

Full template:
<<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<</MATRX>>
"""
    
    print("\n[Original Text]")
    print(text)
    
    # Parse patterns
    patterns = MatrxPatternParser.parse(text)
    
    # Replace patterns with fetched content
    result = MatrxFetcher.process_text_with_patterns(text, patterns)
    
    print("\n[Processed Text]")
    print(result)


# ============================================================================
# Example 4: Fetch Multiple Records
# ============================================================================

def example_fetch_multiple():
    """Fetch multiple records by category."""
    print("\n" + "=" * 80)
    print("Example 4: Fetch Multiple Records")
    print("=" * 80)
    
    # Fetch all blocks in a category (just labels)
    print("\n[Fetch all labels in category]")
    labels = MatrxFetcher.fetch_content_blocks(
        "CATEGORY_ID", 
        "9980e68f-97fc-4f71-bf1d-22583b6cdf38",
        field="label"
    )
    print(labels)
    
    # Fetch multiple fields
    print("\n[Fetch multiple fields: template,label]")
    content = MatrxFetcher.fetch_content_blocks(
        "CATEGORY_ID",
        "9980e68f-97fc-4f71-bf1d-22583b6cdf38",
        field="template,label"
    )
    print(content[:200] + "...")  # First 200 chars


# ============================================================================
# Example 5: Custom Processing
# ============================================================================

def example_custom_processing():
    """Demonstrate custom pattern processing."""
    print("\n" + "=" * 80)
    print("Example 5: Custom Pattern Processing")
    print("=" * 80)
    
    text = "Template: <<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<</MATRX>>"
    
    # Parse patterns
    patterns = MatrxPatternParser.parse(text)
    
    # Process each pattern manually
    for pattern in patterns:
        print(f"\nPattern Found:")
        print(f"  Position: {pattern.start_pos} to {pattern.end_pos}")
        print(f"  Query: {pattern.table}.{pattern.column} = '{pattern.value}'")
        
        # Fetch data
        content = MatrxFetcher.fetch(
            pattern.table,
            pattern.column,
            pattern.value,
            pattern.field
        )
        
        print(f"\nFetched Content (first 100 chars):")
        print(content[:100] + "...")
        
        # Could do custom processing here
        # e.g., transform, validate, cache, etc.


# ============================================================================
# Example 6: Real-World Use Case
# ============================================================================

def example_real_world():
    """Real-world example: AI instruction assembly."""
    print("\n" + "=" * 80)
    print("Example 6: Real-World Use Case - AI Instructions")
    print("=" * 80)
    
    # Instruction template with embedded patterns
    instruction_template = """
You are an AI content generator. Follow these formats:

## Flashcards
Create flashcards using:
<<MATRX>><<CONTENT_BLOCKS>><<BLOCK_ID>>flashcards<</MATRX>>

## Presentations  
Create presentations using:
<<MATRX>><<CONTENT_BLOCKS>><<ID>>b46e284e-ccb0-4d32-8a96-07f85d50d134<</MATRX>>

## Available Interactive Formats
<<MATRX>><<CONTENT_BLOCKS>><<CATEGORY_ID>>9980e68f-97fc-4f71-bf1d-22583b6cdf38<<FIELDS>>label<</MATRX>>
"""
    
    print("\n[Template with patterns]")
    print(instruction_template)
    
    # Process the template
    patterns = MatrxPatternParser.parse(instruction_template)
    final_instructions = MatrxFetcher.process_text_with_patterns(
        instruction_template, 
        patterns
    )
    
    print("\n[Final instructions with content]")
    print(final_instructions[:500] + "...\n")  # First 500 chars
    
    print("✓ Instructions ready to send to AI model")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    from matrx_utils import clear_terminal
    
    clear_terminal()
    
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "MATRX PATTERN SYSTEM - EXAMPLES" + " " * 26 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Run all examples
    try:
        example_parse_patterns()
        example_fetch_data()
        example_process_text()
        example_fetch_multiple()
        example_custom_processing()
        example_real_world()
        
        print("\n" + "=" * 80)
        print("✓ All examples completed successfully!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
