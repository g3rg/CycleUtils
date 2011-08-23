import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class MainPage(webapp.RequestHandler):
    
    
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')

class SpokeTensionCalc(webapp.RequestHandler):
    
    def servePage(self, template_values, page):
        fullTemplateValues = self.createTemplateVars(template_values)
        path = os.path.join(os.path.dirname(__file__), 'web', page + '.html')
        self.response.out.write(template.render(path,fullTemplateValues))
    
    def createTemplateVars(self, vars = {}):
        template_vars = {}
        for var in vars:
            template_vars[var] = vars[var]

        return template_vars    
    
    def get(self):
        self.servePage({}, 'spoketension')    
        
    def post(self):
        None


application = webapp.WSGIApplication(
    [('/', MainPage),('/spoketension', SpokeTensionCalc)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
