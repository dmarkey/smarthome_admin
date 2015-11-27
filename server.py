import aiohttp
import asyncio
from aiohttp.web import Application
from aiohttp_wsgi import WSGIHandler
import json

from conf import wsgi
import asyncio_redis
from aiohttp import web

from smarthome_admin.events import incoming_event

aiohttp_application = Application()
wsgi_handler = WSGIHandler(wsgi.application)



loop = asyncio.get_event_loop()


connections = {}

subscriber = None
publisher = None
srv = None

@asyncio.coroutine
def websocket_handler(request):

    #import ipdb; ipdb.set_trace()
    ws = web.WebSocketResponse(autoping=True, protocols=("arduino",))
    yield from ws.prepare(request)

    controller_id = None
    send_messages = None

    try:
        while True:
            msg = yield from ws.receive()

            print(msg.data)

            if msg.tp == aiohttp.MsgType.text:
                data = json.loads(msg.data)
                if data['event'] == "BEACON":
                    controller_id = str(data['controller_id'])
                    connections[controller_id] = ws
                    yield from subscriber.subscribe(['/controllers/' + controller_id])
                    loop.run_in_executor(None, incoming_event, msg.data)

                if msg.data == 'close':
                    yield from ws.close()

            elif msg.tp == aiohttp.MsgType.error:
                print('ws connection closed with exception %s' %
                      ws.exception())

        print('websocket connection closed')

        return ws

    finally:
        if controller_id is not None:
            subscriber.unsubscribe(['/controllers/' + controller_id])
            connections.pop(controller_id)


@asyncio.coroutine
def redis_handler():
    connection = yield from asyncio_redis.Connection.create(host='127.0.0.1', port=6379)
    publisher = yield from asyncio_redis.Connection.create(host='127.0.0.1', port=6379)
    global subscriber
    subscriber = yield from connection.start_subscribe()

    while True:
        reply = yield from subscriber.next_published()
        obj = json.loads(reply.value)
        controller_id = obj['controller_id']
        if controller_id in connections:
            connections[controller_id].send_str(obj)

        print('Received: ', repr(reply.value), 'on channel', reply.channel)

app = web.Application()
app.router.add_route('GET', '/ws', websocket_handler)
app.router.add_route("*", "/{path_info:.*}", wsgi_handler.handle_request)

handler = app.make_handler()
f = loop.create_server(handler, '0.0.0.0', 8080)

loop.run_until_complete(f)



#loop.run_until_complete(redis_handler())
asyncio.ensure_future(redis_handler())
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.run_until_complete(handler.finish_connections(1.0))
    srv.close()
    loop.run_until_complete(srv.wait_closed())
    loop.run_until_complete(app.finish())
loop.close()
