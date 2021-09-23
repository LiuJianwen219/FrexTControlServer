import tornado.web

tag = "health"


class HealthHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('''
        <html>
          <head><title>Upload File</title></head>
          <body>
            <p>''' + tag + '''<p>
            </form>
          </body>
        </html>
        ''')