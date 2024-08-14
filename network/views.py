import json
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Posts, Followers, Likes


def index(request):
    
    # Get all posts in descending order
    posts = Posts.objects.all().order_by('-id')

    # Paginator
    paginator = Paginator(posts, 10) # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get already liked posts
    try:
        liked = Likes.objects.filter(user=request.user)

        likedPosts = []
        for l in liked:
            likedPosts.append(l.post)
    except:
        likedPosts=[]

    # Get all posts with their like count
    posts_with_like_count = Posts.objects.annotate(like_count=Count('liked_post'))

    return render(request, "network/index.html", {
        "posts": posts,
        "page_obj": page_obj,
        "header": "All Posts",
        "likedPosts": likedPosts,
        "posts_with_like_count": posts_with_like_count,
    })


def add_post(request):
    if request.method == 'POST':
        user = User.objects.get(pk=request.user.id)
        content = request.POST['new_post']

        post = Posts(user=user, content=content)
        post.save()
        return HttpResponseRedirect(reverse(index))
    else:
        return HttpResponseRedirect(reverse(index))


def profile(request, user_id):
    if request.method == 'POST':
        follower = User.objects.get(pk=request.user.id)
        followed = User.objects.get(pk=user_id)

        # If user followed another user, add to the database
        if request.POST["un/follow"] == "Follow":
            f = Followers(
                user=followed,
                follower=follower
            )
            f.save()

        # If user unfollowed another user, remove from database
        else:
            f = Followers.objects.get(user=followed, follower=follower)
            f.delete()

        return HttpResponseRedirect(reverse(profile, kwargs={'user_id':user_id}))

    # Get all posts uploaded by user
    try:
        user = User.objects.get(pk=user_id)
    except:
        return render(request, "network/profile.html", {
            "error": "404 - user not found"
        })
    user_posts = Posts.objects.filter(user=user).order_by('-id')

    # Paginator
    paginator = Paginator(user_posts, 10) # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get the number of followers and and following for user's profile
    following = Followers.objects.filter(follower=user)
    followers = Followers.objects.filter(user=user)

    # Check if current user already follow the profile user
    follow_check = followers.filter(follower=User.objects.get(pk=request.user.id))
    if len(follow_check) == 0:
        isfollowing = False
    else:
        isfollowing = True

    # Get already liked posts
    try:
        liked = Likes.objects.filter(user=request.user)

        likedPosts = []
        for l in liked:
            likedPosts.append(l.post)
    except:
        likedPosts=[]

    # Get all posts with their like count
    posts_with_like_count = Posts.objects.annotate(like_count=Count('liked_post'))

    return render(request, "network/profile.html", {
        "posts": user_posts,
        "page_obj": page_obj,
        "username": user.username,
        "user_id": user_id,
        "following": following,
        "followers": followers,
        "isfollowing": isfollowing,
        "likedPosts": likedPosts,
        "posts_with_like_count": posts_with_like_count,
    })

def following(request):
    current_user = request.user.id
    following = Followers.objects.filter(follower=current_user)
    posts = []

    for person in following:
        post = Posts.objects.filter(user=person.user).order_by("-id")
        for p in post:
            posts.append(p)

    # Paginator
    paginator = Paginator(posts, 10) # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get already liked posts
    try:
        liked = Likes.objects.filter(user=request.user)

        likedPosts = []
        for l in liked:
            likedPosts.append(l.post)
    except:
        likedPosts=[]

    # Get all posts with their like count
    posts_with_like_count = Posts.objects.annotate(like_count=Count('liked_post'))

    return render(request, "network/index.html", {
        "posts": posts,
        "page_obj": page_obj,
        "header": "Following",
        "likedPosts": likedPosts,
        "posts_with_like_count": posts_with_like_count,
})

@csrf_exempt
def edit(request, postID):
    
    # Query for requested post
    try:
        post = Posts.objects.get(pk=postID)
    except Posts.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)
    
    # Save the change in post content
    if request.method == "POST":
        data = json.loads(request.body)
        post.content = data["newContent"]
        post.save()
        return JsonResponse({"message": "Saved sucessfully", "data": data["newContent"]})
    
    return JsonResponse({
        "User": post.user.username,
        "Content": post.content,
        "time": post.time
        })


def like(request, postID):
    post = Posts.objects.get(pk=postID)
    try:
        # Remove like
        like = Likes.objects.get(user=request.user, post=post)
        like.delete()
        return JsonResponse({"message": "Unliked"})
    except:
        # Add like
        l = Likes(
            user = request.user,
            post = post
        )
        l.save()
        return JsonResponse({"message": "Liked"})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
