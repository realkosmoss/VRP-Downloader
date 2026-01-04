from flask import Flask, request, Response
from rclone_fp import make_rclone

BASE_URL = "https://there-is-a.vrpmonkey.help"

app = Flask(__name__)
session = make_rclone()

@app.route("/", defaults={"path": ""}, methods=["GET", "HEAD"])
@app.route("/<path:path>", methods=["GET", "HEAD"])
def proxy(path):
    url = f"{BASE_URL}/{path}" if path else f"{BASE_URL}/"

    upstream = session.request(
        method=request.method,
        url=url,
        stream=True,
    )

    return Response(
        upstream.iter_content(chunk_size=8192),
        status=upstream.status_code,
        headers=[
            (k, v) for k, v in upstream.headers.items()
            if k.lower() not in ("content-encoding", "transfer-encoding", "connection")
        ],
    )


if __name__ == "__main__":
    app.run(port=8080, threaded=True)
