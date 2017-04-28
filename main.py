#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2


from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)
class Blogs(db.Model):
    title = db.StringProperty(required = True)
    blogpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def render_front(self, title="", blogpost="", error=""):


        self.render("front.html", title=title, blogpost=blogpost, error=error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        blogpost = self.request.get("blogpost")

        if title and blogpost:
            a = Blogs(title = title, blogpost = blogpost)
            a.put()

            id=a.key().id()
            self.redirect("/blog/%s" % id)

        else:
            error = "we need both a title and a blogpost!"
            self.render_front(title, blogpost, error)

class Blog(Handler):
    def render_blog(self):
        blogs = db.GqlQuery("SELECT * FROM Blogs ORDER by created DESC LIMIT 5")

        self.render("blogpages.html", blogs=blogs)

    def get(self):
        self.render_blog()
class ViewPostHandler(Handler):
        def get(self, id):
            """ Render a page with post determined by the id (via the URL/permalink) """

            post = Blogs.get_by_id(int(id))
            if post:
                t = jinja_env.get_template("post.html")
                response = t.render(post=post)
            else:
                error = "there is no post with id %s" % id
                t = jinja_env.get_template("404.html")
                response = t.render(error=error)

            self.response.out.write(response)



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', Blog),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
