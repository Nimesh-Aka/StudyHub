
import time
import requests

url = "https://studyhub-backend-8u98.onrender.com/health"

for i in range(5):
    start = time.perf_counter()

    response = requests.get(url)

    elapsed = time.perf_counter() - start

    print(
        f"Request {i + 1}: "
        f"Status={response.status_code}, "
        f"Time={elapsed * 1000:.2f} ms"
    )
