from app import create_app

app = create_app()

# This is required for Vercel deployment
# The app object needs to be directly importable
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)