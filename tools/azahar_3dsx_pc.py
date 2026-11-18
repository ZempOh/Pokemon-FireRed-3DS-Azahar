"""Disassemble the linked 3DSX code around an Azahar guest program counter."""

import argparse
import hashlib
from pathlib import Path
import struct
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("engine", type=Path)
    parser.add_argument("pc", type=lambda value: int(value, 0))
    parser.add_argument("--text-base", required=True, type=lambda value: int(value, 0))
    parser.add_argument("--objdump", default="arm-none-eabi-objdump")
    parser.add_argument("--thumb", action="store_true")
    args = parser.parse_args()

    engine = args.engine.read_bytes()
    if len(engine) < 32 or engine[:4] != b"3DSX":
        parser.error("engine must be a 3DSX file with a complete header")
    header_size, relocation_header_size = struct.unpack_from("<HH", engine, 4)
    code_size = struct.unpack_from("<I", engine, 16)[0]
    code_offset = header_size + 3 * relocation_header_size
    if header_size < 32 or code_offset + code_size > len(engine):
        parser.error("3DSX code segment falls outside the file")

    pc = args.pc & ~1 if args.thumb else args.pc
    text_end = args.text_base + code_size
    if not args.text_base <= pc < text_end:
        parser.error("PC is outside the code segment at the supplied text base")

    print(f"{args.engine.name} SHA-256 {hashlib.sha256(engine).hexdigest()}", flush=True)
    print(f"Guest PC 0x{pc:08x} at code offset 0x{pc - args.text_base:x}", flush=True)
    with tempfile.TemporaryDirectory() as scratch:
        code = Path(scratch) / "code.bin"
        code.write_bytes(engine[code_offset:code_offset + code_size])
        command = [
            args.objdump, "-D", "-b", "binary", "-m", "arm",
            f"--adjust-vma={args.text_base:#x}",
            f"--start-address={max(args.text_base, pc - 32):#x}",
            f"--stop-address={min(text_end, pc + 48):#x}",
        ]
        if args.thumb:
            command.extend(("-M", "force-thumb"))
        subprocess.run([*command, str(code)], check=True)


if __name__ == "__main__":
    main()
