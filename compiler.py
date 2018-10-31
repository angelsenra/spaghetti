#! python3
from itertools import count
import re
"""
https://apps.timwhitlock.info/emoji/tables/unicode
https://www.branah.com/unicode-converter
"""
REP_TABLE = {"; ": "\n", ";": "\n", ":1": "📒", ":2": "📓",
             ":3": "📔", ":4": "📕", ":5": "📖",
             ":6": "📗", ":7": "📘", ":8": "📙"}
INS_SIZE = {"halt": 1, "set": 3, "push": 2, "pop": 2, "eq": 4, "gt": 4,
            "jmp": 2, "jt": 3, "jf": 3, "add": 4, "mult": 4, "mod": 4,
            "and": 4, "or": 4, "not": 3, "rmem": 3, "wmem": 3,
            "call": 2, "ret": 1, "out": 2, "in": 2, "noop": 1}
INS_TABLE = {
    "halt": "🌋",  # 127755
    "set": "📩",  # 128233
    "push": "📥",  # 128229
    "pop": "📤",  # 128228
    "eq": "👬",  # 128108
    "jmp": "🚀",  # 128640
    "jt": "❓",  # 10067
    "jf": "❗",  # 10071
    "add": "➕",  # 10133
    "and": "🅰",  # 127344
    "or": "🅾",  # 127358
    "rmem": "📜",  # 128220
    "wmem": "📝",  # 128221
    "call":  "📡",  # 128225
    "ret":  "💫",  # 128171
    "out":  "📺",  # 128250
    "in":  "🎹",  # 127929
    "noop":  "⏳"  # 9203
}
# ✔ ❌ ❓ ❗ ❔ ❕ ➕ ➖ ➗ ✖ ➡ 🚀 ‼ ⁉ 🇪🇸 ↩ ↪ ⏩ ⏪ 📲 🔋 🔙 🔚 🔛 🔜 🔝 🅰 🅾 👊 💫 📡 ⏳ ✏
# 📜 📝


def sreplace(d, text):
    """Multiple string replace at one time using regex"""
    regex = re.compile("(%s)" % "|".join(map(re.escape, d.keys())))
    return regex.sub(lambda x: d[x.string[x.start():x.end()]], text)


def nreplace(text):
    """Replace .num with the unicode value of num"""
    regex = re.compile(r"(\.\d+)")
    return regex.sub(lambda x: chr(int(x.string[x.start() + 1:x.end()])), text)


def process_tags(code):
    """Return dict containing offset of each tag"""
    tags = {}
    count = 0
    for ins in code.split(r"\n"):
        if not ins:
            count += 2
            continue
        args = ins.split(r"\s")
        arg = args[0]
        if arg[0] == "$":  # Include the whole line
            count += len(ins[1:].replace(r"\s", " ")) + 1
        elif arg[-1] == ":":  # It is a tag
            # print(arg, count)
            tags[":" + arg[:-1]] = chr(count)
        elif arg == "print":
            count += len("".join(args[1:])) * 2
        else:
            count += INS_SIZE[arg]
    return tags


def compile_code(_code, tags):
    """Return list of unicode instructions"""
    code = sreplace(tags, _code)
    out = []
    for ins in code.split(r"\n"):
        if not ins:
            out.append("🔜\n")  # 128284
            continue
        args = ins.split(r"\s")
        arg = args[0]
        if arg[0] == "$":  # Include the whole line
            out.append(ins[1:].replace(r"\s", " ") + "\n")
        elif arg[-1] == ":":  # It is a tag
            # print(arg, len("".join(out)))
            pass
        elif arg == "print":
            for i in "".join(args[1:]):
                out.append(INS_TABLE["out"] + i)
        else:
            size = INS_SIZE[arg]
            out.append(INS_TABLE[arg])
            for i in range(1, size):
                out.append(args[i])
    return out


def main():
    with open("main.src", "r") as f:
        _code = f.read()
    _code = sreplace(REP_TABLE, _code)
    _code = re.sub(r"(\n|[ ]+)//.*", "", _code)
    _code = _code.replace("\n", "\\n").replace(" ", "\\s")
    code = nreplace(_code)
    tags = process_tags(code)
    print("\n".join("%s -> %d" % (k, ord(v)) for k, v in tags.items()))
    compiled = compile_code(code, tags)
    with open("main.bin", "w") as f:
        f.write("".join(compiled))


"""== opcode listing ==
halt: 0
  stop execution and terminate the program
set: 1 a b
  set register <a> to the value of <b>
push: 2 a
  push <a> onto the stack
pop: 3 a
  remove the top element from the stack and write it into <a>; empty stack = error
eq: 4 a b c
  set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
gt: 5 a b c
  set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
jmp: 6 a
  jump to <a>
jt: 7 a b
  if <a> is nonzero, jump to <b>
jf: 8 a b
  if <a> is zero, jump to <b>
add: 9 a b c
  assign into <a> the sum of <b> and <c> (modulo 32768)
mult: 10 a b c
  store into <a> the product of <b> and <c> (modulo 32768)
mod: 11 a b c
  store into <a> the remainder of <b> divided by <c>
and: 12 a b c
  stores into <a> the bitwise and of <b> and <c>
or: 13 a b c
  stores into <a> the bitwise or of <b> and <c>
not: 14 a b
  stores 15-bit bitwise inverse of <b> in <a>
rmem: 15 a b
  read memory at address <b> and write it to <a>
wmem: 16 a b
  write the value from <b> into memory at address <a>
call: 17 a
  write the address of the next instruction to the stack and jump to <a>
ret: 18
  remove the top element from the stack and jump to it; empty stack = halt
out: 19 a
  write the character represented by ascii code <a> to the terminal
in: 20 a
  read a character from the terminal and write its ascii code to <a>; it can be assumed that once input starts, it will continue until a newline is encountered; this means that you can safely read whole lines from the keyboard and trust that they will be fully read
noop: 21
  no operation
"""

if __name__ == "__main__":
    main()
