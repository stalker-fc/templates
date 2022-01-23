from app import startup_app

if __name__ == '__main__':
    from aiohttp import web

    web.run_app(startup_app(), host="0.0.0.0", port=8080)
