import re
import sys
from typing import Optional, List
from rewrite_by_hand.data.variables import MAGIC_STRING
from rewrite_by_hand.cli.output import output_manager


class Block:
    def __init__(self, content: str, mark: Optional[str]):
        self.content = content
        self.mark = mark


class BlocksManager:
    def __init__(self):
        pass

    def cut(self, file_content: str) -> List[Block]:
        """
        Cut the file content into blocks.
        Raises BlockParsingError if there are nested blocks, unclosed blocks, or mismatched marks.
        """
        # Find all possible start and end markers to validate the structure
        start_pattern = re.compile(rf"/\*\s*{MAGIC_STRING}\s*:\s*(\w+)")
        end_pattern = re.compile(rf"{MAGIC_STRING}\s*:\s*(\w+)\s*\*/")

        # Validate block structure
        lines = file_content.splitlines()
        starts = []
        ends = []

        # Track line numbers for better error messages
        for i, line in enumerate(lines):
            line_number = i + 1
            for m in start_pattern.finditer(line):
                starts.append((m.group(1), m.start(), line_number))
            for m in end_pattern.finditer(line):
                ends.append((m.group(1), m.end(), line_number))

        # Check for block nesting or unclosed blocks
        if len(starts) != len(ends):
            if len(starts) > len(ends):
                # Find the unclosed block(s)
                unclosed = [
                    f"'{mark}' (started on line {line})"
                    for mark, _, line in starts
                    if mark not in [m for m, _, _ in ends]
                ]
                unclosed_str = ", ".join(unclosed)
                output_manager.err("Unclosed_Block", unclosed_str=unclosed_str)
                sys.exit(1)
            else:
                # Find the unopened block(s)
                unopened = [
                    f"'{mark}' (ended on line {line})"
                    for mark, _, line in ends
                    if mark not in [m for m, _, _ in starts]
                ]
                unopened_str = ", ".join(unopened)
                output_manager.err("Unopened_Block", unopened_str=unopened_str)
                sys.exit(1)

        # Combine and sort all markers by position in file
        all_markers = [(mark, pos, line, "start") for mark, pos, line in starts]
        all_markers.extend([(mark, pos, line, "end") for mark, pos, line in ends])
        all_markers.sort(
            key=lambda x: (x[2], x[1])
        )  # Sort by line number, then position

        # Track open blocks to detect nesting
        open_blocks = []  # Stack of (mark, line_number) tuples
        for mark, _, line_num, marker_type in all_markers:
            if marker_type == "start":
                # Opening a new block
                if open_blocks:
                    # If there's already an open block, this is nested
                    parent_mark, parent_line = open_blocks[-1]
                    output_manager.err(
                        "Nested_Block",
                        mark=mark,
                        line_num=line_num,
                        parent_mark=parent_mark,
                        parent_line=parent_line,
                    )
                    sys.exit(1)
                open_blocks.append((mark, line_num))
            else:
                # Closing a block
                if not open_blocks:
                    output_manager.err(
                        "Not_Matching_Block", mark=mark, line_num=line_num
                    )
                    sys.exit(1)
                last_mark, start_line = open_blocks[-1]
                if last_mark != mark:
                    output_manager.err(
                        "Missmatched_Block",
                        mark=mark,
                        line_num=line_num,
                        last_mark=last_mark,
                        start_line=start_line,
                    )
                    sys.exit(1)
                open_blocks.pop()

        # Regular expressions for block markers - more flexible patterns
        block_pattern = re.compile(
            rf"/\*\s*{MAGIC_STRING}\s*:\s*(\w+)[\s\S]*?{MAGIC_STRING}\s*:\s*\1\s*\*/"
        )

        # Find all possible blocks, including those with mismatched start/end marks
        all_blocks = []
        for match in re.finditer(block_pattern, file_content):
            all_blocks.append(
                (match.group(1), match.start(), match.end(), match.group(0))
            )

        # Now that we've validated the structure, extract the blocks
        result = []
        last_end = 0

        # Process blocks in order of appearance
        for mark, start, end, content in sorted(all_blocks, key=lambda x: x[1]):
            # If there's content before this block, add it as a non-marked block
            if start > last_end:
                non_block = file_content[last_end:start]
                if non_block.strip():
                    result.append(Block(non_block, None))

            # Add the matched block with its mark
            result.append(Block(content, mark))

            last_end = end

        # Add any remaining content after the last block
        if last_end < len(file_content):
            remaining = file_content[last_end:]
            if remaining.strip():
                result.append(Block(remaining, None))

        return result

    def get_marks(self, file_content: str) -> List[str]:
        """
        Extract all block marks from the file.
        Returns a list of unique marks.
        """
        blocks = self.cut(file_content)
        marks = [block.mark for block in blocks if block.mark is not None]
        return list(set(marks))

    def filter_blocks(self, file_content: str, marks_to_keep: List[str]) -> str:
        """
        Keep only blocks with specified marks and remove their markers.
        Remove other blocks entirely.
        Returns the modified file content.
        """
        blocks = self.cut(file_content)
        marks = [block.mark for block in blocks if block.mark is not None]
        for mark in marks_to_keep:
            if mark not in marks:
                output_manager.err("Block_Not_Found", mark=mark)
                sys.exit(1)
        result_parts = []

        for block in blocks:
            if block.mark is None:
                # Keep non-block content
                result_parts.append(block.content)
            elif block.mark in marks_to_keep:
                # Keep blocks with marks to keep, but strip markers
                # Use regex to remove the markers
                content = block.content

                # Remove start marker
                start_pattern = re.compile(
                    rf"/\*\s*{MAGIC_STRING}\s*:\s*{block.mark}\s*"
                )
                content = re.sub(start_pattern, "", content, count=1)

                # Remove end marker
                end_pattern = re.compile(rf"\s*{MAGIC_STRING}\s*:\s*{block.mark}\s*\*/")
                content = re.sub(end_pattern, "", content, count=1)

                result_parts.append(content.strip())

        return "\n".join(result_parts)


blocks_manager = BlocksManager()
