# ---------------------------------------------------------------------------
# my_package/__main__.py
#
# Entry point for the application. Supports two equivalent launch methods:
#   python -m my_package          (direct module run)
#   my-package                    (console script defined in pyproject.toml)
#
# Add your application startup logic inside main().
# ---------------------------------------------------------------------------


def main() -> None:
    """Main entry point for the application."""
    print("Hello from my_package!")


if __name__ == "__main__":
    main()




