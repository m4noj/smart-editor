import re
from .tokens import TOKEN_PATTERNS

def lex_line(line:str):
    tokens = []
    matched_indices = set()
    
    for token_type, pattern in TOKEN_PATTERNS.items():
        for match in pattern.finditer(line):
            start, end = match.start(), match.end()

            if any(i in matched_indices for i in range(start,end)):
                continue

    return sorted(tokens,key=lambda x:x[1])    