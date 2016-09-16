
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class Handler(webapp2.RequestHandler):                         #"Blog handler" on udacity
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params): #takes file name [template] and extra parameters and...... creates a string to get rendered back to the browser in the render function below
        t = jinja_env.get_template(template)  #use jinja environment created above and have it get the file name [template]  causes jinja to load file and store it in t
        return t.render(params)                               #then we render t and pass in the parameters that were called into this function

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))             #to send back to browser (a string)

#blogstuff

def entry_key(name = 'default'):                                 #note: per udacity hmwrk3 solution1 about 2 minutes in: the defaul is the parent name and possibly doesn't apply to lc assignment
    return db.Key.from_path('entries', name)                      #value of the blog key parent



class BlogPosts(db.Model):                               #class "Post" on udacity  #this will define an entity and we need to define types of that entity (types, date, int, float etc) (we're pulling from the database now)
    title = db.StringProperty(required = True)                  #class name BlogPosts =  the table name (see render_front in MainPage(Handler) below)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)           #look up google docs
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):                                              # this def render(self) added from solution Part1 of Basic Blog on udacity
        self._render_text = self.content.replace('\n', '<br>')     #this part makes new lines show up
        return render_str("front.html", p = self)



class NewPost(Handler):                                         #formerly MainHandler(handler) and in the self.render the html was "front.html"(-es9/14/16)
    def render_front(self, title="", entry="", error=""):
        entries = db.GqlQuery("SELECT * FROM BlogPosts "        # name of table is the class name BlogPosts
                              "ORDER BY created DESC "
                              "LIMIT 5")         # this query will store results as a cursor (aka a pointer to the results)(query uses descending for most recent first)
        self.render("newpost.html", title=title, entry=entry, error=error, entries=entries)  #the parameters are passed into the template

    def get(self):
        self.render_front()                                       #to draw the blank form

    def post(self):                                                     #to get entries submitted on the blog
        title = self.request.get("title")
        entry = self.request.get("entry")
        if title and entry:                     #this is a success case
            e = BlogPosts(title = title, entry = entry)    #taking from class BlogPosts
            e.put()                                                     #to store blog post entry in database
            x = str(e.key().id())
            self.redirect('/blog/%s' % x)                         #needs to redirect to permalink page with indiv.html-9/15/16
        else:                                   #this is a fail case
            error = "Please submit both a post title and a post entry.  Thank you."
            self.render_front(title, entry, error)




class MainBlog(Handler):      #a separate page for new posts to submit to created 9-14-16
    def get(self):
        entries = db.GqlQuery("SELECT * FROM BlogPosts "        # name of table is the class name BlogPosts
                              "ORDER BY created DESC "
                              "LIMIT 5")         # this query will store results as a cursor (aka a pointer to the results)(query uses descending for most recent first)
        self.render("mainblog.html", entries=entries)  #the parameters are passed into the template




# TO DO: make handler that directs to new entry permalink page
class ViewPostHandler(Handler):  #to direct to permalink of newest individual blog posts  #class ViewPostHandler(webapp2.RequestHandler)
    def get(self, id):
        int_id = int(id)
        new_post = BlogPosts.get_by_id(int_id)

        if new_post:
            # new_post = new_post.title + new_post.entry   #not sure this is great but it shows all
            #self.response.out.write(new_post)
            self.render("permalink.html", new_post=new_post)
        else:
            error = "Invalid id; please try again."
            self.response.out.write(error)



#    def post("permalink.html", id):


#TO DO: make each blog post title a permalink (Q:: will this happen on the MainBlog page???)



app = webapp2.WSGIApplication([
                               webapp2.Route(r'/', handler=MainBlog, name='home'),
                               webapp2.Route(r'/blog', handler=MainBlog, name='main_blog_page'),  #current front page (blog w/ 5 most recent posts)
                               webapp2.Route(r'/newpost', handler=NewPost, name='newpost'),  #routes to blog post form
                               webapp2.Route(r'/blog/newpost', handler=NewPost, name='newpost'), #routest to newpost form
                               webapp2.Route(r'/blog/<id:\d+>', ViewPostHandler, name='id')],  #routes to ViewPostHandler page (permalink page)
                               debug=True)
