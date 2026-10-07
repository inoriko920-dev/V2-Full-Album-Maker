from __future__ import annotations

import sys

from full_album_maker.app_kernel import build_app_kernel
from full_album_maker.production_runtime import install_production_runtime


# Preserve the established import-time production preparation contract while
# consolidating its ownership into one ordered M9 bootstrap boundary.
install_production_runtime()


def _run_legacy_gui() -> int:
    # Import after installing the compatibility/presentation layers so the recovered
    # v1.4 window keeps its proven engine while the integrated workspaces extend it.
    from full_album_maker.v14_window import run

    return run()


def _run_legacy_portable_smoke() -> int:
    from full_album_maker.release_smoke import run_portable_smoke

    return run_portable_smoke()


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    kernel = build_app_kernel(
        gui_runner=_run_legacy_gui,
        portable_smoke_runner=_run_legacy_portable_smoke,
    )
    return kernel.run(args)


if __name__ == "__main__":
    raise SystemExit(main())