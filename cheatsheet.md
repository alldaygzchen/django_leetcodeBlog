# Counter session in Django
create request.session["stored_posts"] and check post_id in stored_posts or stored_posts = None


### models.py (cross model query)

        post = models.ForeignKey(
                Post, on_delete=models.CASCADE, related_name="comments")
        related_name="comments"


### views.py (just add CommentForm to context ) 

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context["post_tags"] = self.object.tags.all()
        context["comment_form"] = CommentForm() 
        return context

### post-detail.html (check overall comment_form is correct)

        {% if comment_form.errors %} 
        <div id="alert">
        <h2>Saving the comment failed!</h2>
        <p>Please check the comment form below the post and fix your erros.</p>
        <a href="#comment-form">Fix!</a>
        </div>
        {% endif %}

        <div id="read-later">
                <form action="{% url "read-later" %}" method="POST">
                {% csrf_token %}
                <input type="hidden" value="{{ post.id }}" name="post_id">
                <button>Read Later</button>
                </form>
        </div>


### views.py and post-detail.html (Deal with sessions)

                class ReadLaterView(View):
                        def get(self, request):
                                stored_posts = request.session.get("stored_posts")

                                context = {}

                                if stored_posts is None or len(stored_posts) == 0:
                                context["posts"] = []
                                context["has_posts"] = False
                                else:
                                posts = Post.objects.filter(id__in=stored_posts)
                                context["posts"] = posts
                                context["has_posts"] = True

                                return render(request, "blog/stored-posts.html", context)


                        def post(self, request):
                                stored_posts = request.session.get("stored_posts")

                                if stored_posts is None:
                                stored_posts = []

                                post_id = int(request.POST["post_id"])

                                if post_id not in stored_posts:
                                stored_posts.append(post_id)
                                request.session["stored_posts"] = stored_posts
                                
                                return HttpResponseRedirect("/")

                <form action="{% url "read-later" %}" method="POST">
                        {% csrf_token %}
                        <input type="hidden" value="{{ post.id }}" name="post_id">
                        <button>Read Later</button>
                </form>

