import os

from aiohttp import web

from server import PromptServer  # type: ignore

routes = PromptServer.instance.routes


@routes.put("/ryuu/set_loglevel")
async def set_loglevel(request):
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    loglevel = data.get("loglevel", "")
    os.environ["RYUU_LOGLEVEL"] = loglevel.upper()

    resp_data = {"status": "success", "loglevel": loglevel.upper()}

    return web.json_response(resp_data)
