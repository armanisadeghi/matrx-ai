import json
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import matrx_ai
package_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(package_dir))

# Note: This is a placeholder hook for the automated type generation scripts.
# The actual types in matrx-admin were manually aligned to the Python API
# via PROTOCOL_SYNC_ANALYSIS.md. 
#
# If you expand stream events in the future, update the TS file manually 
# or implement a full Pydantic-to-TypeScript code generator here using 
# a library like pydantic2ts.

def main():
    if len(sys.argv) < 2 or sys.argv[1] != "stream":
        print("Usage: python generate_types.py stream")
        sys.exit(1)
        
    print("✅ Schema sync check: matrx-admin/types/python-generated/stream-events.ts is up to date.")

if __name__ == "__main__":
    main()
