import os

# Force using in-memory mock DB so the app can run without a real MongoDB.
# This sets the same variable that app.config reads (USE_MOCK_DB).
os.environ.setdefault("USE_MOCK_DB", "1")

from app import create_app

app = create_app()


if __name__ == "__main__":
    port = app.config["PORT"]
    print("=" * 52)
    print("  Pharmacy Plus started (using mock DB)")
    print(f"  Open: http://localhost:{port}")
    print(f"  Seed: http://localhost:{port}/seed")
    print("=" * 52)
    app.run(host="0.0.0.0", port=port, debug=app.config["FLASK_DEBUG"])
