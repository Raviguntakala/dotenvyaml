"""Generate YAML fixtures of varying sizes for benchmarking."""

from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def generate_flat(num_keys: int) -> str:
    """Generate a flat YAML file with N key-value pairs."""
    lines = []
    for i in range(num_keys):
        lines.append(f"KEY_{i}: \"value_{i}\"")
    return "\n".join(lines)


def generate_nested(depth: int, breadth: int) -> str:
    """Generate a nested YAML file with given depth and breadth."""
    lines = []

    def _add_level(prefix: str, current_depth: int, indent: int) -> None:
        for i in range(breadth):
            key = f"{prefix}_{i}" if prefix else f"group_{i}"
            if current_depth > 0:
                lines.append(f"{'  ' * indent}{key}:")
                _add_level(key, current_depth - 1, indent + 1)
            else:
                lines.append(f"{'  ' * indent}{key}: \"val_{i}\"")

    _add_level("", depth, 0)
    return "\n".join(lines)


def generate_mixed(num_groups: int) -> str:
    """Generate a realistic mixed YAML config."""
    lines = []
    for i in range(num_groups):
        lines.append(f"service_{i}:")
        lines.append(f"  host: \"host-{i}.example.com\"")
        lines.append(f"  port: {8000 + i}")
        lines.append(f"  debug: {'true' if i % 2 == 0 else 'false'}")
        lines.append(f"  tags:")
        lines.append(f"    - \"tag_a_{i}\"")
        lines.append(f"    - \"tag_b_{i}\"")
        lines.append(f"  database:")
        lines.append(f"    host: \"db-{i}.internal\"")
        lines.append(f"    port: {5432 + i}")
        lines.append(f"    name: \"db_{i}\"")
    return "\n".join(lines)


def main() -> None:
    """Generate all benchmark fixtures."""
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

    fixtures = {
        "small_flat_10.yaml": generate_flat(10),
        "medium_flat_100.yaml": generate_flat(100),
        "large_flat_1000.yaml": generate_flat(1000),
        "small_nested_3x3.yaml": generate_nested(3, 3),
        "medium_nested_4x5.yaml": generate_nested(4, 5),
        "small_mixed_5.yaml": generate_mixed(5),
        "medium_mixed_50.yaml": generate_mixed(50),
        "large_mixed_200.yaml": generate_mixed(200),
    }

    for name, content in fixtures.items():
        path = FIXTURE_DIR / name
        path.write_text(content)
        size = len(content.encode())
        print(f"  {name}: {size:,} bytes")

    print(f"\nGenerated {len(fixtures)} fixtures in {FIXTURE_DIR}")


if __name__ == "__main__":
    main()