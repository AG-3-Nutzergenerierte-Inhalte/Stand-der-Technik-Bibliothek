#!/bin/bash
#
# This script finds all non-binary files in the current directory and its
# subdirectories that are tracked by Git (respecting .gitignore), and
# concatenates them into a single context file.
# Large files (>1000 lines) are truncated to the first 200 lines to keep
# the context file manageable.
# USAGE:
# 1. Place this script in the root of your project directory.
# 2. Make it executable: chmod +x get_code_state_for_ai.sh
# 3. Run it with an optional filter:
#    ./get_code_state_for_ai.sh             # All tracked text files
#    ./get_code_state_for_ai.sh --code      # Only Python files (*.py)
#    ./get_code_state_for_ai.sh --json      # Only JSON files (*.json)
#    ./get_code_state_for_ai.sh --md        # Only Markdown files (*.md, *.markdown)
#    ./get_code_state_for_ai.sh --text      # Only text files (*.txt)
#    ./get_code_state_for_ai.sh --no-python # All files except Python files
#    ./get_code_state_for_ai.sh --automator # Only files in the bsi-audit-automator directory
#
# The output will be a file named 'project_context.txt'.

OUTPUT_FILE="project_context.txt"
FILTER_MSG="🔍 Finding all tracked text files"
FILE_PATTERN=""

# Simple argument parsing for different file types
case "$1" in
  --code)      FILTER_MSG="🐍 Finding Python files"; FILE_PATTERN="-- '*.py'";;
  --json)      FILTER_MSG="📄 Finding JSON files"; FILE_PATTERN="-- '*.json'";;
  --md)        FILTER_MSG="✍️  Finding Markdown files"; FILE_PATTERN="-- '*.md' '*.markdown'";;
  --text)      FILTER_MSG="🔤 Finding text files"; FILE_PATTERN="-- '*.txt'";;
  --no-python) FILTER_MSG="🚫🐍 Finding all files except Python"; FILE_PATTERN="-- . ':(exclude)*.py'";;
  --automator) FILTER_MSG="🤖 Finding bsi-audit-automator files"; FILE_PATTERN="-- 'bsi-audit-automator/'";;
  "")          ;; # No filter, use default behavior
  *)           echo "Error: Unknown option '$1'. See usage in script comments." >&2; exit 1;;
esac

# Check for required commands
if ! command -v git &> /dev/null; then
    echo "Error: 'git' command not found. This script must be run in a Git repository."
    exit 1
fi

if ! command -v file &> /dev/null; then
    echo "Error: 'file' command not found. This is required to identify text files."
    exit 1
fi

# Clear the output file to start fresh
> "$OUTPUT_FILE"

echo "$FILTER_MSG and generating context..."

# Use 'git ls-files' to get a list of all files tracked by git,
# respecting .gitignore. Pipe this list into a loop.
# --cached: All files tracked in the index.
# --others: All untracked files.
# --exclude-standard: Respects .gitignore, .git/info/exclude, and global gitignore.
eval "git ls-files --cached --others --exclude-standard $FILE_PATTERN" | while read -r filename; do
    # Check if the file is not binary. This is more reliable than just checking for
    # "text/*" and correctly includes files like JSON (`application/json`),
    # XML (`application/xml`), etc., while excluding true binary files.
    mimetype=$(file -b --mime "$filename")
    if ! [[ "$mimetype" =~ charset=binary ]]; then
        # Append a header with the filename
        echo "==== ${filename} ====" >> "$OUTPUT_FILE"

        # Get line count to determine if we need to truncate
        line_count=$(wc -l < "$filename")

        # If file is too long, truncate it. Otherwise, add it whole.
        if [ "$line_count" -gt 1000 ]; then
            echo "   Adding: $filename (Truncated to 200 lines from $line_count)"
            head -n 200 "$filename" >> "$OUTPUT_FILE"
            echo "" >> "$OUTPUT_FILE"
            echo "[... File truncated. Only first 200 of ${line_count} lines included. ...]" >> "$OUTPUT_FILE"
        else
            echo "   Adding: $filename"
            cat "$filename" >> "$OUTPUT_FILE"
        fi

        # Add a newline for spacing between files
        echo "" >> "$OUTPUT_FILE"
    fi
done

echo ""
echo "✅ Project context successfully generated in: $OUTPUT_FILE"