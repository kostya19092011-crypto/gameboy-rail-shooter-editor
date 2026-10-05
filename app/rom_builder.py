from pathlib import Path
import json


def _str_to_bytes(value: str, length: int = 16) -> bytes:
    raw = value.encode("ascii", errors="ignore")
    if len(raw) > length:
        raw = raw[:length]
    return raw.ljust(length, b"\x00")


def generate_rom(project: dict) -> bytes:
    """Generate a minimal Game Boy ROM file containing metadata for a rail shooter prototype."""
    rom = bytearray(32768)

    # Minimal Game Boy cartridge header.
    rom[0x100:0x14D] = bytes.fromhex(
        "CE ED 66 66 CC 0D 00 0B 03 73 00 83 00 0C 00 0D "
        "00 08 11 1F 88 89 00 0E DC 99 17 67 83 43 00 0C "
        "00 0D 00 08 11 1F 88 89 00 0E DC 99 17 67 83 43"
    )

    title = (project.get("title", "RAIL RUNNER") or "RAIL RUNNER")[:15]
    rom[0x134:0x143] = _str_to_bytes(title, 15)
    rom[0x143] = 0x00  # cartridge type: ROM only
    rom[0x144] = 0x00  # ROM size: 32 KiB
    rom[0x145] = 0x00  # RAM size
    rom[0x146] = 0x01  # destination code
    rom[0x147] = 0x33  # old license code
    rom[0x148] = 0x00  # mask ROM version

    # Simple metadata section for the project.
    payload = {
        "title": project.get("title", "RAIL RUNNER"),
        "difficulty": project.get("difficulty", "normal"),
        "enemy_count": int(project.get("enemy_count", 12)),
        "player_speed": int(project.get("player_speed", 4)),
        "boss": project.get("boss", "specter"),
        "theme": project.get("theme", "sunset"),
        "background_color": project.get("background_color", "#F7B267"),
        "music": project.get("music", "neon-ride"),
        "scroll_speed": int(project.get("scroll_speed", 8)),
        "boss_health": int(project.get("boss_health", 16)),
    }
    serialized = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    meta_start = 0x400
    meta_end = meta_start + min(len(serialized), 0x800)
    rom[meta_start:meta_end] = serialized[: meta_end - meta_start]
    rom[meta_end:meta_end + 1] = b"\x00"

    # Very small checksum validation for cartridges.
    checksum = 0
    for index in range(0x134, 0x14D):
        checksum = (checksum + rom[index]) & 0xFF
    rom[0x14D] = checksum & 0xFF

    return bytes(rom)


def export_rom(rom: bytes, output_path: str) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as handle:
        handle.write(rom)
    return output_path
