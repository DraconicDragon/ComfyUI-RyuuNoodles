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

    # ryuu_log("Log level set to:", loglevel.upper(), loglevel=loglevel.lower())
    # ryuu_log("DEBUG Log Level test", loglevel="debug")
    # ryuu_log("INFO Log Level test", loglevel="info")
    # ryuu_log("WARNING Log Level test", loglevel="warning")
    # ryuu_log("ERROR Log Level test", loglevel="error")
    # ryuu_log("CRITICAL Log Level test", loglevel="critical")

    resp_data = {"status": "success", "loglevel": loglevel.upper()}

    return web.json_response(resp_data)
