
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params): #takes file name [template] and extra parameters and...... creates a string to get rendered back to the browser in the render function below
        t = jinja_env.get_template(template)  #use jinja environment created above and have it get the file name [template]  causes jinja to load file and store it in t
        return t.render(params)   #then we render t and pass in the parameters that were called into this function

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw)) #to send back to browser (a string)


class BlogPosts(db.Model):        #this will define an entity and we need to define types of that entity (types, date, int, float etc) (we're pulling from the database now)
    title = db.StringProperty(required = True)       #class name BlogPosts =  the table name (see render_front in MainPage(Handler) below)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)  #look up google docs





class MainPage(Handler):                                # we want to show the form and the submitted blog posts
    def render_front(self, title="", entry="", error=""):
        entries = db.GqlQuery("SELECT * FROM BlogPosts "        # name of table is the class name BlogPosts
                              "ORDER BY created DESC ")         # this query will store results as a cursor (aka a pointer to the results)(query uses descending for most recent first)


        self.render("front.html", title=title, entry=entry, error=error, entries=entries)  #the parameters are passed into the template

    def get(self):
        self.render_front()                                       #to draw the blank form


    def post(self):                                                     #to get entries submitted on the blog
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:                     #this is a success case
            e = BlogPosts(title = title, entry = entry)    #taking from class BlogPosts
            e.put()                                                                         #to store blog post entry in database

            self.redirect("/")                  #to redirect to frontpage
        else:
            error = "Please submit both a post title and a post entry.  Thank you."    #this is a fail case
            self.render_front(title, entry, error)



app = webapp2.WSGIApplication([('/', MainPage)], debug=True)