import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import User, Posts, Followers, Likes


def index(request):

    # get all posts
    postss = Posts.objects.order_by("-date").all()

    # get all posts user liked
    try:
        likes = Likes.objects.filter(user=request.user).values_list('post_id', flat=True)
    except TypeError:
        likes = None
    
    # Paintor
    paginator = Paginator(postss, 10)  # Show 10 contacts per page.

    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # render index page with data
    return render(request, "network/index.html", {
        "posts": posts,
        "likes": likes,
    })


def post(request):
    
    # make sure request method post
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # check if user logged in
    if request.user.is_authenticated is False:
        return JsonResponse({"error": "Must Log In"}, status=400)

    # check if there's text
    data = json.loads(request.body)
    posts = [post.strip() for post in data.get("text").split(",")]

    # if it's empty return error
    if posts == [""]:
        return JsonResponse({"error": "Must Provide Post Text"}, status=400)

    # get data from user
    text = data.get("text", "")

    # add data to db
    post = Posts(poster=request.user, text=text)
    post.save()

    # return success message
    return JsonResponse({"success": "Posted Successfully", "post": post.serialize()}, status=201, safe=False)


def users(request, user_name):

    # check if existed
    try:
        user = User.objects.get(username=user_name)
    except ObjectDoesNotExist:
        return render(request, "network/error.html", {
            "error": "User does not exist"
        })

    # get follower and following and user posts from db
    followers = Followers.objects.filter(user=user).count()
    following = Followers.objects.filter(follower=user).count()
    user_postss = Posts.objects.filter(poster=user)

    # get all posts user liked
    try:
        likes = Likes.objects.filter(user=request.user).values_list('post_id', flat=True)
    except TypeError:
        likes = None

    # Paintor
    paginator = Paginator(user_postss, 10)  # Show 10 contacts per page.

    page_number = request.GET.get('page')
    user_posts = paginator.get_page(page_number)

    # if user not logged in show the page with out follow form
    if request.user.is_authenticated is False:
        return render(request, "network/user.html", {
            "user_data": user,
            "followers": followers,
            "following": following,
            "user_posts": user_posts,
            "likes": likes,
        })

    # check if user follow the user
    try:
        check = Followers.objects.get(user=user, follower=request.user)
        check = "true"
    except ObjectDoesNotExist:
        check = "false"

    # render page with user data
    return render(request, "network/user.html", {
        "user_data": user,
        "followers": followers,
        "following": following,
        "user_posts": user_posts,
        "check": check,
    })


def follow(request):

    # make sure request method post
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # check if user logged in
    if request.user.is_authenticated is False:
        return JsonResponse({"error": "Must Log In"}, status=400)

    # check if there's data
    data = json.loads(request.body)
    userr = [post.strip() for post in data.get("user_f").split(",")]
    followw = [post.strip() for post in data.get("follow").split(",")]

    # if it's empty return error
    if userr == [""] or followw == [""]:
        return JsonResponse({"error": "Error no data passed"}, status=400)

    #get the user want to follow or unfollow
    user = User.objects.get(pk=data.get("user_f", ""))
    
    # if follow false follow the user
    if data.get("follow", "") == "false":

        # check if user already followed
        try:
            f = Followers.objects.get(user=user, follower=request.user)
            return JsonResponse({"error": "User already followed"}, status=400)
        except ObjectDoesNotExist:
            pass
        
        # follow the user
        follow = Followers(user=user, follower=request.user)
        follow.save()

        # get new followers number
        followers = Followers.objects.filter(user=user).count()

        # return success
        return JsonResponse({"success": "followed", "count": followers}, status=201)

    elif data.get("follow", "") == "true":

        # unfollow the user
        try:
            follow = Followers.objects.get(user=user, follower=request.user)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "User is not followed"}, status=400)
        follow.delete()

        # get new followers number
        followers = Followers.objects.filter(user=user).count()

        # return success
        return JsonResponse({"success": "unfollowed", "count": followers}, status=201)

    else:
        return JsonResponse({"error": "something went wrong"}, status=400)


@login_required(login_url='/login')
def following(request):

    # get posts of users the user follows
    following_users = Followers.objects.filter(follower=request.user).values_list('user_id', flat=True)
    following_postss = Posts.objects.filter(poster__in=following_users).order_by("-date")

    # get all posts user liked
    try:
        likes = Likes.objects.filter(user=request.user).values_list('post_id', flat=True)
    except TypeError:
        likes = None

    # Paintor
    paginator = Paginator(following_postss, 10)  # Show 10 contacts per page.

    page_number = request.GET.get('page')
    following_posts = paginator.get_page(page_number)

    # return page with posts
    return render(request, "network/following.html", {
        "following_posts": following_posts,
        "likes": likes,
    })


def edit_post(request):

    # make sure request method post
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # check if there's data
    data = json.loads(request.body)
    postt = [post.strip() for post in data.get("post").split(",")]
    textt = [post.strip() for post in data.get("text").split(",")]

    # if it's empty return error
    if postt == [""] or textt == [""]:
        return JsonResponse({"error": "Must Provide Post Text"}, status=400)

    # get the post and check if there is post
    try:
        post = Posts.objects.get(pk=data.get("post", ""))
    except ObjectDoesNotExist:
        return JsonResponse({"error": "post doesn't exist"}, status=400)

    # make sure user is the poster
    if request.user != post.poster:
        return JsonResponse({"error": "This is not your post"}, status=400)

    # edit the post
    post.text = data.get("text", "")
    post.save()

    # return success message
    return JsonResponse({"success": "Edited successfully"}, status=201)


def like(request):

    # make sure request method post
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # check if user logged in
    if request.user.is_authenticated is False:
        return JsonResponse({"error": "Must Log In"}, status=400)

    # check if there's data
    data = json.loads(request.body)
    postt = [post.strip() for post in data.get("post").split(",")]
    likee = [post.strip() for post in data.get("like").split(",")]

    # if it's empty return error
    if postt == [""] or likee == [""]:
        return JsonResponse({"error": "Error no data passed"}, status=400)

    # get the post
    try:
        post = Posts.objects.get(pk=data.get('post', ""))
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Post doesn't exist "}, status=400)

    # if like is false like the post
    if data.get("like", "") == "false":

        # check if user already liked the post
        try:
            l = Likes.objects.get(user=request.user, post=post)
            return JsonResponse({"error": "Post already liked"}, status=400)
        except ObjectDoesNotExist:
            pass

        # like the post
        like = Likes(user=request.user, post=post)
        post.likes += 1
        like.save()
        post.save()

        # return success
        return JsonResponse({"success": "liked"}, status=201)

    # if like is true unlike the post
    elif data.get("like", "") == "true":

        # unlike the post
        try:
            like = Likes.objects.get(user=request.user, post=post)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "post is not liked"}, status=400)
        post.likes -= 1
        like.delete()
        post.save()

        # return success
        return JsonResponse({"success": "unliked"}, status=201)

    else:
        return JsonResponse({"error": "something went wrong"}, status=400)


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
