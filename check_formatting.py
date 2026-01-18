#!/usr/bin/env python3
"""
AsciiDoc Formatting Issue Detector

This script scans AsciiDoc files for formatting issues that asciidoctor-pdf
might not properly handle, including:
- HTML tags in passthrough blocks
- Tables wrapped in passthrough blocks
- Orphan passthrough markers
- Unbalanced block delimiters
- HTML entities
- Problematic patterns
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict


class FormattingChecker:
    def __init__(self):
        self.issues = defaultdict(list)
        
    def check_file(self, filepath):
        """Check a single file for formatting issues."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return
        
        filename = os.path.basename(filepath)
        
        # Check for various issues
        self._check_html_tags(filename, lines)
        self._check_passthrough_tables(filename, content, lines)
        self._check_orphan_passthroughs(filename, lines)
        self._check_unbalanced_blocks(filename, lines)
        self._check_html_entities(filename, lines)
        self._check_problematic_patterns(filename, lines)
        
    def _check_html_tags(self, filename, lines):
        """Check for HTML tags that should be converted to AsciiDoc."""
        html_patterns = [
            (r'<div\s+data-type\s*=\s*"([^"]+)"', 'HTML div with data-type'),
            (r'<p\s+data-type\s*=\s*"([^"]+)"', 'HTML p with data-type'),
            (r'<p\s+class\s*=\s*"([^"]+)"', 'HTML p with class'),
            (r'<ul\s+class\s*=\s*"([^"]+)"', 'HTML ul with class'),
            (r'<li>', 'HTML li tag'),
            (r'<dl>', 'HTML definition list'),
            (r'<dt>', 'HTML definition term'),
            (r'<dd>', 'HTML definition description'),
            (r'<sup>', 'HTML superscript'),
            (r'<sub>', 'HTML subscript'),
            (r'<span\s+class\s*=', 'HTML span with class'),
            (r'<a\s+data-type\s*=\s*"xref"', 'HTML xref link'),
            (r'(?<!<)(?<!<)<table', 'HTML table'),  # Avoid matching <<table cross-refs
            (r'<pre\s+data-type\s*=', 'HTML pre with data-type'),
            (r'<math\s', 'MathML content'),
            (r'</div>', 'Closing div tag'),
            (r'</ul>', 'Closing ul tag'),
            (r'</table>', 'Closing table tag'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, description in html_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues[filename].append({
                        'line': i,
                        'type': 'HTML Tag',
                        'description': description,
                        'content': line.strip()[:80]
                    })
    
    def _check_passthrough_tables(self, filename, content, lines):
        """Check for tables wrapped in passthrough blocks."""
        # Find all ++++...++++ blocks
        in_passthrough = False
        passthrough_start = 0
        
        for i, line in enumerate(lines, 1):
            if line.strip() == '++++':
                if not in_passthrough:
                    in_passthrough = True
                    passthrough_start = i
                else:
                    in_passthrough = False
                    # Check if passthrough contained a table
                    block_content = '\n'.join(lines[passthrough_start-1:i])
                    if re.search(r'\|===', block_content):
                        self.issues[filename].append({
                            'line': passthrough_start,
                            'type': 'Passthrough Table',
                            'description': 'Table wrapped in passthrough block',
                            'content': f'Lines {passthrough_start}-{i}'
                        })
    
    def _check_orphan_passthroughs(self, filename, lines):
        """Check for orphan passthrough markers."""
        passthrough_count = 0
        passthrough_lines = []
        
        for i, line in enumerate(lines, 1):
            if line.strip() == '++++':
                passthrough_count += 1
                passthrough_lines.append(i)
        
        if passthrough_count % 2 != 0:
            self.issues[filename].append({
                'line': passthrough_lines[-1] if passthrough_lines else 0,
                'type': 'Orphan Passthrough',
                'description': f'Unbalanced passthrough markers (count: {passthrough_count})',
                'content': f'Passthrough markers at lines: {passthrough_lines}'
            })
    
    def _check_unbalanced_blocks(self, filename, lines):
        """Check for unbalanced block delimiters."""
        block_types = {
            '****': 'sidebar',
            '====': 'example',
            '----': 'listing',
            '____': 'quote',
            '....': 'literal',
        }
        
        for delimiter, block_type in block_types.items():
            count = 0
            block_lines = []
            for i, line in enumerate(lines, 1):
                # Only count if it's exactly the delimiter (not part of a header like ====)
                if line.strip() == delimiter:
                    count += 1
                    block_lines.append(i)
            
            if count % 2 != 0:
                self.issues[filename].append({
                    'line': block_lines[-1] if block_lines else 0,
                    'type': 'Unbalanced Block',
                    'description': f'Unbalanced {block_type} block ({delimiter}) - count: {count}',
                    'content': f'Block markers at lines: {block_lines[-5:]}'  # Show last 5
                })
    
    def _check_html_entities(self, filename, lines):
        """Check for HTML entities that might not render correctly."""
        entity_patterns = [
            (r'&nbsp;', 'Non-breaking space entity'),
            (r'&mdash;', 'Em dash entity'),
            (r'&ndash;', 'En dash entity'),
            (r'&hellip;', 'Ellipsis entity'),
            (r'&amp;', 'Ampersand entity'),
            (r'&lt;', 'Less than entity'),
            (r'&gt;', 'Greater than entity'),
            (r'&#x[0-9a-fA-F]+;', 'Hex character entity'),
            (r'&#[0-9]+;', 'Decimal character entity'),
        ]
        
        for i, line in enumerate(lines, 1):
            # Skip if line is inside a passthrough block marker context
            for pattern, description in entity_patterns:
                matches = re.findall(pattern, line)
                if matches and '+++' not in line:  # Ignore entities in passthrough
                    self.issues[filename].append({
                        'line': i,
                        'type': 'HTML Entity',
                        'description': description,
                        'content': line.strip()[:80]
                    })
                    break  # Only report once per line
    
    def _check_problematic_patterns(self, filename, lines):
        """Check for other problematic patterns."""
        patterns = [
            (r'<\[\[', 'Malformed anchor (starts with <)'),
            (r'pass:\[.*<<', 'Cross-reference in pass macro'),
            # Removed condensed table row check - too many false positives with ASCII art
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, description in patterns:
                if re.search(pattern, line):
                    self.issues[filename].append({
                        'line': i,
                        'type': 'Problematic Pattern',
                        'description': description,
                        'content': line.strip()[:80]
                    })
    
    def print_report(self):
        """Print a formatted report of all issues found."""
        if not self.issues:
            print("✅ No formatting issues found!")
            return
        
        total_issues = sum(len(issues) for issues in self.issues.values())
        print(f"\n{'='*70}")
        print(f"FORMATTING ISSUES REPORT - {total_issues} issue(s) found")
        print(f"{'='*70}\n")
        
        for filename in sorted(self.issues.keys()):
            file_issues = self.issues[filename]
            print(f"\n📄 {filename} ({len(file_issues)} issue(s))")
            print("-" * 60)
            
            # Group by type
            by_type = defaultdict(list)
            for issue in file_issues:
                by_type[issue['type']].append(issue)
            
            for issue_type, issues in sorted(by_type.items()):
                print(f"\n  [{issue_type}] ({len(issues)} occurrence(s))")
                for issue in issues[:10]:  # Limit to 10 per type
                    print(f"    Line {issue['line']}: {issue['description']}")
                    if issue['content']:
                        content = issue['content']
                        if len(content) > 60:
                            content = content[:60] + "..."
                        print(f"      → {content}")
                if len(issues) > 10:
                    print(f"    ... and {len(issues) - 10} more")
        
        print(f"\n{'='*70}")
        print(f"Summary: {total_issues} issue(s) in {len(self.issues)} file(s)")
        print(f"{'='*70}\n")


def main():
    # Get the directory to scan
    if len(sys.argv) > 1:
        scan_dir = sys.argv[1]
    else:
        scan_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Scanning for AsciiDoc formatting issues in: {scan_dir}\n")
    
    checker = FormattingChecker()
    
    # Find all .adoc files
    adoc_files = sorted(Path(scan_dir).glob("*.adoc"))
    
    if not adoc_files:
        print("No .adoc files found!")
        return
    
    print(f"Found {len(adoc_files)} AsciiDoc files to check...\n")
    
    for filepath in adoc_files:
        print(f"  Checking {filepath.name}...")
        checker.check_file(filepath)
    
    checker.print_report()


if __name__ == "__main__":
    main()

