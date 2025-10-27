import re
TOKEN_TYPES = [
                'keywords',
                'keywords2',
                'keywords3',
                'keywords4',
                'builtin',
                'function',
                'bool',
                'type'
                'string',
                'number',
                'comment',
                'operator',
                'identifier',
                'decorator',
                'punctuation',
]

TOKEN_PATTERNS = {     
        "comment": re.compile(r"#.*"),
        'keywords': re.compile(r"\b(from|and|as|assert|async|await|break|class|continue|del|except|finally|for|global|in|is|nonlocal|not|or|pass|raise|return|try|while|with)\b"),
        'keywords2': re.compile(r"\b(if|else|elif)\b"),
        'keywords3': re.compile(r"\b(def)\b"),
        'keywords4': re.compile(r"\b(self)\b"),
        'builtin': re.compile(r"\b(import|print|len|range|type|input|open|super|yield|lambda)\b"),
        "string": re.compile(r"(\"[^\"]*\"|'[^']*')"),
        "type": re.compile(r"\b(int|str|float|bool|list|dict|set|tuple)\b"),
        "bool": re.compile(r"\b(True|False|None)\b"),
        "function": re.compile(r"\b\w+(?=\s*\()"),
        "identifier": re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),        
        "punctuation": re.compile(r"[\[\]{}\(\)\:\.,]"),   
        "number": re.compile(r"\b\d+(\.\d+)?\b"),
        "operator": re.compile(r"[-+*/%=<>!]+"),
        "decorator": re.compile(r"@\w+"),               
}
