"""Initialize omarchy-hue: ensure config directory exists."""

from .config import CONFIG_DIR


def main() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Config directory: {CONFIG_DIR}")
    print("Ready. Run `uv run setup` to configure the Hue bridge and room.")


if __name__ == "__main__":
    main()
