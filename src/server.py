"""Simple FastAPI server to serve CSV files."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI(title="AutoDealer CSV Server")

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def _serve_file(filename: str) -> FileResponse:
    """Helper to serve a CSV file."""
    file_path = PROJECT_ROOT / filename
    if not file_path.exists():
        return FileResponse(
            file_path,
            media_type="text/plain",
            status_code=404,
        )
    return FileResponse(
        file_path,
        media_type="text/csv",
        filename=filename,
    )


@app.get("/output")
async def serve_output():
    """Serve output.csv file."""
    return _serve_file("output.csv")


@app.get("/warehouse")
async def serve_warehouse():
    """Serve warehouse.csv file."""
    return _serve_file("warehouse.csv")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
