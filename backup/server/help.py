import tornado.web

tag = "help"

class HelpHandler(tornado.web.RequestHandler):
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