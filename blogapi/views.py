# REST FRAMEWORK
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# from .serializers import PostSerializer

# Just basic old full stack
from .models import *

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden

from . utils import NotificationManager


from django_gravatar.helpers import get_gravatar_url




def is_admin(func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have permission to access this route.")
    return wrapper



# @api_view(['GET', 'POST'])
# def allPosts(request):
#     if request.method == 'GET':
#         allpost = blogpost.objects.all()
#         serializer = PostSerializer(allpost, many=True)
#         return Response(serializer.data)


#     elif request.method == 'POST':
#         serializer = PostSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, satus=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'PUT', 'DELETE'])
# def mypost(request, pk):
#     try:
#         getpost = blogpost.objects.get(pk=pk)
#     except blogpost.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#     else:
#         if request.method == 'GET':
#             serializer = PostSerializer(getpost)
#             return Response(serializer.data)

#         elif request.method == 'PUT':
#             serializer = PostSerializer(getpost, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         elif request.method == 'DELETE':
#             getpost.delete()
#             return Response(status=status.HTTP_200_SUCCESS)



def home(request):
    blogpost = BlogPost.objects.all()
    # day=current_day, month=current_month, year=current_year, feed=feed,current_user=current_user, logged_in=logged_in
    return render(request, "index.html", {'feed': blogpost})


def about(request):
    return render(request,"about.html")


def contact(request):
    global logged_in
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        msg = f"Name: {name}\nEmail: {email}\nPhone Number: {phone}\nMessage: {message}"
        notify = NotificationManager(msg=msg, recipient="imlearning862@gmail.com", subject="Blog Message")
        if notify:
            success_msg = "Successfully, sent your message."
            return render(request, "contact.html", {'success':True, 'success_msg': success_msg})
        else:
            return render(request,'error.html')
    return render(request, "contact.html", {'success': False})



@is_admin
def delete(request, pk):
    blogpost = BlogPost.objects.get(pk=pk)
    blogpost.delete()

    return redirect('/')


@login_required
def edit(request, pk):
    # Fetch the blog post or return a 404 if not found
    post = get_object_or_404(BlogPost, pk=pk)

    # Pre-fill data for the template
    data = {
        'title': post.title,
        'subtitle': post.subtitle,
        'img': request.build_absolute_uri(post.img_url.url) if post.img_url else None,
        'body': post.body,
        'blog': post
    }

    # Process POST request for updating the blog post
    if request.method == "POST":
        post.title = request.POST.get('title', post.title)
        post.subtitle = request.POST.get('subtitle', post.subtitle)
        post.body = request.POST.get('body', post.body)

        # Handle image upload if a new image is provided
        if 'img' in request.FILES:
            post.img_url = request.FILES['img']

        post.save()



        # Redirect to the blog post's detail page after updating
        return redirect('blog:get-post', pk=post.pk)

    # Render the edit form with the existing data
    return render(request, 'edit.html', data)



def login_user(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')


        try:
            user = User.objects.get(username=username)

        except User.DoesNotExist:
            error = "This email does not exist. Please try again."
            messages.error(request, error)
            return redirect('blog:login')
        else:
            if check_password(password, user.password):

                login(request, user)
                return redirect("blog:home")
            else:
                error = "Incorrect password. Please try again."
                redirect('blog:login')
    return render(request, "login.html")




def logout_user(request):
    logout(request)
    return redirect('blog:home')



@login_required
def create_post(request):
    if request.method == "POST":
        new_post = BlogPost(title=request.POST.get('title'),
                            subtitle=request.POST.get('subtitle'),
                            author=request.user,
                            img_url=request.FILES.get('img'),
                            body=request.POST.get('body'),
                            )
        try:
            new_post.save()
        except:
            # Handle unique constraint failure
            data  = {}
            data['error'] = "A blog post with this title already exists."
            return render(request, 'edit.html', data)

        return redirect("/")
    return render(request, "make-post.html")


def get_post(request, pk):
    feed = BlogPost.objects.get(pk=pk)

    # Fetch comments for the post
    comments = Comment.objects.filter(blog_post=feed)


    if request.method == 'POST':
        # Handle new comment submission
        comment_text = request.POST.get('comment')
        try:
            new_comment = Comment(comment_author=request.user, comment_text=comment_text, blog_post=feed)
        except:
            error = "Please Login and try again."
            messages.error(request, error)
            return redirect('blog:login')
        new_comment.save()
        return redirect('blog:get-post', pk=feed.pk)

    # Render the template
    return render(request, "post.html", {'feed': feed, 'comments': comments})


def register(request):
    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get('username')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        password = request.POST.get('password')

        # Check if a user with the same email or username already exists
        if User.objects.filter(email=email).exists():
            error = 'Sorry, that email is already registered. Login instead.'
            return redirect('blog:login')

        if User.objects.filter(username=username).exists():
            error = 'Sorry, that username is already taken. Choose a different one.'
            return render(request, "register.html", {"error": error})

        # Create new user
        new_user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=firstname,
            last_name=lastname
        )

        login(request, new_user)
        return redirect('blog:home')

    return render(request, "register.html")
