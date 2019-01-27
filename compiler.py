#! python3
import re

REP_TABLE = {
    ";": "\n",
    ":1": "📒",  # 128210
    ":2": "📓",  # 128211
    ":3": "📔",  # 128212
    ":4": "📕",  # 128213
    ":5": "📖",  # 128214
    ":6": "📗",  # 128215
    ":7": "📘",  # 128216
    ":8": "📙"  # 128217
}
INS_SIZE = {
    "halt": 1,
    "set": 3,
    "push": 2,
    "pop": 2,
    "eq": 4,
    "gt": 4,
    "jmp": 2,
    "jt": 3,
    "jf": 3,
    "add": 4,
    "mult": 4,
    "mod": 4,
    "and": 4,
    "or": 4,
    "not": 3,
    "rmem": 3,
    "wmem": 3,
    "call": 2,
    "ret": 1,
    "out": 2,
    "in": 2,
    "noop": 1
}
INS_TABLE = {
    "halt": "🌋",  # 127755
    "set": "📩",  # 128233
    "push": "📥",  # 128229
    "pop": "📤",  # 128228
    "eq": "👬",  # 128108
    "gt": "💪",  # 128170
    "jmp": "🚀",  # 128640
    "jt": "❓",  # 10067
    "jf": "❗",  # 10071
    "add": "➕",  # 10133
    "mult": "✖",  # 10006
    "mod": "➗",  # 10135
    "and": "🅰",  # 127344
    "or": "🅾",  # 127358
    "not": "➖",  # 10134
    "rmem": "📜",  # 128220
    "wmem": "📝",  # 128221
    "call": "📡",  # 128225
    "ret": "💫",  # 128171
    "out": "📺",  # 128250
    "in": "🎹",  # 127929
    "noop": "⏳"  # 9203
}


def replace_str(dictionary, text):
    """
    Multiple string replace at one time using regex

    :param dict dictionary: Maps a substring with its replacement
    :param str text: Text to be replaced

    :return: Text replaced
    :rtype: str
    """
    regex = re.compile("(%s)" % "|".join(map(re.escape, dictionary.keys())))
    return regex.sub(lambda x: dictionary[x.string[x.start():x.end()]], text)


def replace_num(text):
    """
    Replace '.num' with the unicode value of 'num'

    :param str text: Text to be replaced

    :return: Text replaced
    :rtype: str
    """
    regex = re.compile(r"(\.\d+)")
    return regex.sub(lambda x: chr(int(x.string[x.start() + 1:x.end()])), text)


def process_tags(code, debug=False):
    """
    Return dict containing offset of each tag

    :param str code: Code text

    :return: Tags dictionary
    :rtype: dict
    """
    if debug:
        print("TAGS".center(50, "-"))
    tags = {}
    count = 0
    for ins in code.split(r"\n"):
        if not ins:
            if debug:
                print(r"[%08d] \n x2" % count)
            count += 2
            continue
        args = ins.split(r"\s")
        arg = args[0]
        if arg[0] == "$":
            if debug:
                print("[%08d] whole line" % count)
            count += len(ins[1:].replace(r"\s", " ")) + 1
        elif arg[0] == "{":
            if debug:
                print("[%08d] list of tags" % count)
            count += ins[1:].count("$") // 2 + 1
        elif arg[-1] == ":":  # It is a tag
            if debug:
                print("[%08d] [TAG] %s" % (count, arg[:-1]))
            tags["$" + arg[:-1] + "$"] = chr(count)
        elif arg == "print":
            if debug:
                print("[%08d] PRINT" % count)
            count += len("".join(args[1:])) * 2
        else:
            count += INS_SIZE[arg]
    return tags, count


def compile_code(code, tags, debug=False):
    """
    Return unicode instructions out of source and tags

    :param str code: Code text
    :param dict tags: Tags dictionary

    :return: Compiled code
    :rtype: str
    """
    if debug:
        print("COMPILED".center(50, "-"))
    compiled = []
    for ins in replace_str(tags, code).split(r"\n"):
        if not ins:
            if debug:
                print(r"{%08d} \n x2" % sum(map(len, compiled)))
            compiled.append("🔜\n")  # 128284
            continue
        args = ins.split(r"\s")
        arg = args[0]
        if arg[0] == "$":
            if debug:
                print("{%08d} whole line" % sum(map(len, compiled)))
            compiled.append(ins[1:].replace(r"\s", " ") + "\n")
        elif arg[0] == "{":
            if debug:
                print("{%08d} list of tags" % sum(map(len, compiled)))
            compiled.append(ins[1:].replace(r"\s", " ") + "\n")
        elif arg[-1] == ":":  # It is a tag
            if debug:
                print("{%08d} [TAG] %s" % (sum(map(len, compiled)), arg[:-1]))
            pass
        elif arg == "print":
            if debug:
                print("{%08d} PRINT" % sum(map(len, compiled)))
            for i in "".join(args[1:]):
                compiled.append(INS_TABLE["out"] + i)
        else:
            compiled.append(INS_TABLE[arg])
            for i in range(1, INS_SIZE[arg]):
                compiled.append(args[i])
    return "".join(compiled), sum(map(len, compiled))


def pre_compile(code):
    """
    Treat source before the tags are processed and it is compiled

    :param str code: Code text

    :return: Replaced code
    :rtype: str
    """
    code_ = code
    code_ = re.sub(r"\n[ ]+", "\n", code_)  # Remove indentation
    code_ = re.sub(r"[ ]+\n", "\n", code_)  # Remove trailing spaces
    code_ = re.sub(r"\n+//.*", "", code_)  # Remove line comments
    code_ = re.sub(r"([^\$].*?:) (\$[^\$]*?)", r"\1\n\2", code_)
    code_ = re.sub(r"(\$.*?\$)\(\)", r"call \1", code_)
    code_ = re.sub(r"(\$.*?\$)\((.+?)\)", r"\2\ncall \1", code_)
    code_ = re.sub(r"(j[tf]) \((.*?) = (.*?)\) (\$.*?\$)",
                   r"\2 = \3\n\1 \2 \4", code_)
    code_ = re.sub(r"(.*?) = (.*?) == (.*?)", r"eq \1 \2 \3", code_)
    code_ = re.sub(r"(.*?) = (.*?) > (.*?)", r"gt \1 \2 \3", code_)
    code_ = re.sub(r"(.*?) = \~(.*?)", r"not \1 \2", code_)
    code_ = re.sub(r"(.*?) = (.*?) \+ (.*?)", r"add \1 \2 \3", code_)
    code_ = re.sub(r"(.*?) \+= (.*?)", r"add \1 \1 \2", code_)
    code_ = re.sub(r"(.*?) = (.*?) \* (.*?)", r"mult \1 \2 \3", code_)
    code_ = re.sub(r"(.*?) \*= (.*?)", r"mult \1 \1 \2", code_)
    code_ = re.sub(r"(.*?) = (.*?) \% (.*?)", r"mod \1 \2 \3", code_)
    code_ = re.sub(r"(.*?) \%= (.*?)", r"mod \1 \1 \2", code_)
    code_ = re.sub(r"(.*?) = (.*?) \& (.*?)", r"and \1 \2 \3", code_)
    code_ = re.sub(r"(.*?) \&= (.*?)", r"and \1 \1 \2", code_)
    code_ = re.sub(r"(.*?) = (.*?) \| (.*?)", r"or \1 \2 \3", code_)
    code_ = re.sub(r"(.*?) \|= (.*?)", r"or \1 \1 \2", code_)
    code_ = re.sub(r"(.*?) = (.*?)", r"set \1 \2", code_)
    print(code_)
    code_ = replace_str(REP_TABLE, code_)  # Registers
    code_ = re.sub(r"([ ]+)//.*", "", code_)  # Remove inline comments
    code_ = code_.replace("\n", "\\n").replace(" ", "\\s")  # \n and \s to raw
    code_ = replace_num(code_)  # Literal integers
    return code_


def print_warnings(tags, compiled, code, tcount, ccount):
    print()
    print(f"{tcount} vs {ccount}")
    for i in tags:
        if i not in code:
            print(f"tag {i} was never called")
    for i in re.findall(r"\$(.*?)\$", compiled):
        print(f"tag {i} not defined")


def main(debug=1):
    with open("source.emoji", "r") as f:
        code = pre_compile(f.read())
    tags, tcount = process_tags(code, debug=debug)
    compiled, ccount = compile_code(code, tags, debug=debug)
    print_warnings(tags, compiled, code, tcount, ccount)
    with open("bin", "w") as f:
        f.write(compiled)


if __name__ == "__main__":
    main()
