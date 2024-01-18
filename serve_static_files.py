import os

from settings import STATIC_DIR


def serve_statics(request):
    served = False
    if ".js" in request.path:
        served = True
        file_path = os.path.join(STATIC_DIR + '/js/', request.path.split('/')[-1])
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
                request.send_response(200)
                request.send_header('Content-type', 'application/javascript')
                request.end_headers()
                request.wfile.write(content)
        except FileNotFoundError:
            request.send_error(404, "File Not Found")

    elif ".css" in request.path:
        file_path = os.path.join(STATIC_DIR + '/css/', request.path.split('/')[-1])
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
                request.send_response(200)
                request.send_header('Content-type', 'text/css')
                request.end_headers()
                request.wfile.write(content)
        except FileNotFoundError:
            request.send_error(404, "File Not Found")
        served = True

    return served