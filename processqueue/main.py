from app import build_app

app = build_app()

if __name__ == '__main__':
    from aiohttp import web
    web.run_app(app, host="0.0.0.0", port=8080)
