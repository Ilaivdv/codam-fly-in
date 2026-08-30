from .config import Config

def main() -> None:
    cfg = Config(map_path="hi")
    print(cfg.get_map_path())

if __name__ == "__main__":
    main()
