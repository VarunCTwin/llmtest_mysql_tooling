from typing import List

def parse_release_notes(text: str) -> List[str]:
    """Extract actionable items from release notes.
    Strategy: grab non-empty lines, strip bullets, ignore headers.
    """
    lines = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        # strip bullets and markdown markers
        s = s.lstrip('-*0123456789. ').strip()
        # ignore headings like '##', '#'
        if s.startswith('#'):
            continue
        lines.append(s)
    return lines
