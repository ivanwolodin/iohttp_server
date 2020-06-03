# examples/server_simple.py
from aiohttp import web
import urllib
# import aiohttp.ClientSession as client 
"https://www.cbr-xml-daily.ru/daily_json.js"


async def get_json(client):
    pass
	# url = urllib.parse.urlsplit("http://example.com/path/page.html")
    #
    # if url.scheme == 'https':
    #     reader, writer = await asyncio.open_connection(
    #         url.hostname, 443, ssl=True)
    # else:
    #     reader, writer = await asyncio.open_connection(
    #         url.hostname, 80)
    #
    # query = (
    #     f"HEAD {url.path or '/'} HTTP/1.0\r\n"
    #     f"Host: {url.hostname}\r\n"
    #     f"\r\n"
    # )
    #
    # writer.write(query.encode('latin-1'))
    # while True:
    #     line = await reader.readline()
    #     if not line:
    #         break
    #
    #     line = line.decode('latin1').rstrip()
    #     if line:
    #         print(f'HTTP header> {line}')
    #
    # # Ignore the body, close the socket
    # writer.close()


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)


async def wshandle(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.text:
            await ws.send_str("Hello, {}".format(msg.data))
        elif msg.type == web.WSMsgType.binary:
            await ws.send_bytes(msg.data)
        elif msg.type == web.WSMsgType.close:
            break

    return ws


app = web.Application()
app.add_routes([web.get('/', handle),
                web.get('/echo', wshandle),
                #web.get('/{name}', handle),
				web.get('/json', get_json)],
)

if __name__ == '__main__':
    web.run_app(app)