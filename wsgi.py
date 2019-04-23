from django.core.wsgi import get_wsgi_application
from gevent import monkey
from gevent.pywsgi import WSGIServer
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
monkey.patch_all()
application = get_wsgi_application()


if __name__ == '__main__':
    server = WSGIServer(('localhost', 3000), application)
    print('程序已执行，请在浏览器中输入 http://localhost:3000\n(Ctrl+C 退出)\n')
    server.serve_forever()
