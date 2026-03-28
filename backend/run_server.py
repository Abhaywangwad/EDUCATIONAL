from __future__ import annotations

import sys

import uvicorn


class StandaloneServer(uvicorn.Server):
    def install_signal_handlers(self) -> None:
        # The Codex/Windows terminal environment can send console events that
        # cause the default Uvicorn signal handlers to stop the server
        # immediately. Running without installing those handlers keeps the
        # backend alive until the process is explicitly terminated.
        return


def main() -> None:
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            port = 8000

    config = uvicorn.Config(
        "app.main:app",
        host="127.0.0.1",
        port=port,
        log_level="info",
        reload=False,
    )
    server = StandaloneServer(config)
    server.run()


if __name__ == "__main__":
    main()
