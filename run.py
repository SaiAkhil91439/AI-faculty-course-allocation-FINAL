import os
import sys
import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print(" AI Faculty Course Allocation Optimization Engine")
    print(" Server URL: http://localhost:8000 (or http://127.0.0.1:8000)")
    print(" Default Login: admin / admin123")
    print("=" * 65)
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
