"""FastAPI entry point for the QueryScale local application."""

from __future__ import annotations

from fastapi import FastAPI

from backend.routes.benchmark import router as benchmark_router
from backend.routes.queries import router as queries_router
from backend.routes.recommendations import router as recommendations_router


app = FastAPI(title="QueryScale", version="0.1.0")
app.include_router(benchmark_router, prefix="/api")
app.include_router(queries_router, prefix="/api")
app.include_router(recommendations_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the application process is ready to receive requests."""

    return {"status": "ok"}


def main() -> None:
    import uvicorn

    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()