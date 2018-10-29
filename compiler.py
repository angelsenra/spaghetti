#! python3
from itertools import count
import re
"""
https://apps.timwhitlock.info/emoji/tables/unicode
https://www.branah.com/unicode-converter
"""


def sreplace(d, text):
    regex = re.compile("(%s)" % "|".join(map(re.escape, d.keys())))
    return regex.sub(lambda x: d[x.string[x.start():x.end()]], text)

code = u"""jmp .3
end:  // Set end tag
halt
print Hello .10
print Do .32 you .32 think .32 you .32 can .32 guess .32 the .32 password? .10
out >
in :1;
loop:  // Set loop tag
in :8
eq :8 :8 .10
jf :8 loop;  // If input not /n then goto loop
// print Answer: .32 :1 .10;
and :8 Y y
eq :8 :8 :1
jf :8 end;  // If answer not y then goto end
print That's .32 wonderful! .10 .10
print The .32 password .32 is .32 formed .32 by .32 choosing .32
print letters .32 from .32 the .32 answers .32 to .32
print the .32 following .32 questions: .10
print (Arrays .32 start .32 at .32 zero) .10
print (Keep .32 in .32 mind .32 Coredumped's .32 lore) .10
print Que .32 las .32 preguntas .32 van .32 sobre .32 nosotros .32 vaya .10 .10
"""  # ✔ ❌ ❓ ❗ ❔ ❕ ➕ ➖ ➗ ✖ ➡ 🚀 ‼ ⁉ 🇪🇸 ↩ ↪ ⏩ ⏪ 📲 🔋 🔙 🔚 🔛 🔜 🔝 🅰 🅾 👊 💫 📡

table = {"; ": "\n", ";": "\n", ":1": "📒", ":2": "📓",
         ":3": "📔", ":4": "📕", ":5": "📖",
         ":6": "📗", ":7": "📘", ":8": "📙"}

with open("main.bin", "w") as f:
    tags = {}
    count = 0
    for line in sreplace(table, code).translate(table).splitlines():
        if not line:
            f.write("🔜\n")  # 128284
            count += 2
            continue
        pos = f.tell()
        args = [chr(int(i[1:])) if i.startswith(".") and len(i) != 1 else i
                for i in line.split(" ")]
        if args[0] == "//" or args[0:2] == ["", "//"]:
            continue
        print(count, pos, args)
        if args[0] == "halt":  # 0
            f.write("🔚")  # 128282
            count += 1
        elif args[0] == "push":  # 2 a
            f.write("📩")  # 128233
            f.write(args[1])
            count += 2
        elif args[0] == "eq":  # 4 a b c
            f.write("👬")  # 128108
            f.write(args[1])
            f.write(args[2])
            f.write(args[3])
            count += 4
        elif args[0] == "jmp":  # 6 a
            f.write("🚀")  # 128640
            f.write(tags.pop(args[1], args[1]))
            count += 2
        elif args[0] == "jt":  # 7 a b
            f.write("❓")  # 10067
            f.write(args[1])
            f.write(tags.pop(args[2], args[2]))
            count += 3
        elif args[0] == "jf":  # 8 a b
            f.write("❗")  # 10071
            f.write(args[1])
            f.write(tags.pop(args[2], args[2]))
            count += 3
        elif args[0] == "and":  # 12 a b c
            f.write("🅰")  # 127344
            f.write(args[1])
            f.write(args[2])
            f.write(args[3])
            count += 4
        elif args[0] == "or":  # 13 a b c
            f.write("🅾")  # 127358
            f.write(args[1])
            f.write(args[2])
            f.write(args[3])
            count += 4
        elif args[0] == "call":  # 17 a
            f.write("📡")  # 128225
            f.write(args[1])
            count += 2
        elif args[0] == "ret":  # 18
            f.write("💫")  # 128171
            count += 1
        elif args[0] == "out":  # 19 a
            f.write("📺")  # 128250
            f.write(args[1])
            count += 2
        elif args[0] == "in":  # 20 a
            f.write("🎹")  # 127929
            f.write(args[1])
            count += 2
        # MACROS
        elif args[0] == "print":
            for i in "".join(args[1:]):
                f.write("📺")  # 128250
                f.write(i)
                count += 2
        # TAG
        elif args[0][-1] == ":":
            tags[args[0][:-1]] = chr(count)
        else:
            print("unrecognized instruction")
    print(count, f.tell())


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
