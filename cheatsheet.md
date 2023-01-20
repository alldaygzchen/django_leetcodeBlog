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

### Deployment considerations (elastic beanstalk & rds & s3)

1. Choose Database
2. Adjust settings
3. Collect static files (since not served automatically)
4. Choose a host

### How to deploy to AWS

settings.py   
1. DEBUG = False

2. colleting all static files to this folder   

        [STATIC_ROOT = BASE_DIR /"staticfiles"]  
        python manage.py collectstatic  

3. from os import getenv

        getenv("SECRET_KEY")
        getenv("IS_DEVELOPMENT",True)
        getenv("APP_HOST","localhost")     

4. method1: 
        
        1. urls.py => static(settings.STATIC_URL,document_root = settings.STATIC_ROOT)
        2. create .ebextensions folder and django.config
        3. create a zip folder without venv and static folders (staticfiles folder is included) 
        4. Open AWS elastic beanstalk and configure settings
        5. elastic beanstalk software settings => env variables

5. method2: 
        
        1. add static-files.config in  .ebextensions folder

6. method3: (static files from other https service like s3 bucket)
        
        1. go to amazon s3 bucket and uncheck the block settings
        2. 靜態網站託管 => 啟用
        3. 許可 => 編輯跨來源資源分享 (CORS)
        [
                {
                "AllowedHeaders":["*"],
                "AllowedMethods":["GET"],
                "AllowedOrigins":["*"],
                "ExposeHeaders":[]
                }
        ]
        4. 許可 => 儲存貯體政策
        {
        "Version":"2012-10-17",
        "Statement":[{
                "Sid":"PublicReadGetObject",
                "Effect":"Allow",
                "Principal": "*",
                "Action":["s3:GetObject"],
                "Resource":["arn:aws:s3:::django-leetcode/*"
        ]}
        ]
        }

        5. aws Iam
        建立使用者群組 => AmazonS3FullAccess 授權
        建立使用者 => progrmatically access
        #https://repost.aws/questions/QUYmfTq-vOT-ehonIKesLJtg/change-access-type-for-an-iam-user
        
        pip install django-storages boto3


        AWS_STORAGE_BUCKET_NAME = ""
        AWS_S3_REGION_NAME = ""
        AWS_ACCESS_KEY_ID  =""
        AWS_SECRET_ACCESS_KEY = ""

        AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
        STATICFILES_STORAGE = "custom_storages.MediaFileStorage"
        DEFAULT_FILE_STORAGE = "custom_storages.MediaFileStorage"

        add custom-storages.py




6. real db server
        1. pip install psycopg2-binary
        2. python -m pip freeze > requirements.txt
        3. 
        go to aws rds and create database (free tier)
        public access: Yes

        settings.py 
        DATABASES = {
        'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'postgres',
                'USER': '<your-rds-db-username>',
                'PASSWORD': '<your-rds-db-user-password>',
                'HOST': '<your-rds-db-host>',
                'PORT': '5432'
        }
        }

        4. rds 編輯傳入規則: change ip to anywhere (db can connect to anywhere not only local)




5. SSL and domains is not free in beanstalk
1. python -m pip freeze > requirements.txt
 



### Notes
1. Django is a web framework not web server
2. wsgi   
        https://ithelp.ithome.com.tw/articles/10157271  
        https://medium.com/@eric248655665/%E4%BB%80%E9%BA%BC%E6%98%AF-wsgi-%E7%82%BA%E4%BB%80%E9%BA%BC%E8%A6%81%E7%94%A8-wsgi-f0d5f3001652  

        client <=> web server (gunicorn is a WSGI server and WSGI is a protocol of server and python application)  <=>  web application (django)
3. Django does not serve static files (images, css ...) automatically (Django won't find this file except python manage.py runserver)

        method1: Configure Django to server such files [add static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)]  

        method2: Configure web server to serve static files

        method3: Use another service (better performance)
4. Django orm supports postgres, mariaDB, mySql, Oracle ,SQlite