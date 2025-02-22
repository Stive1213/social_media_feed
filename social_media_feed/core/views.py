from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post, Comment, Like
from .forms import PostForm, CommentForm, UsernameChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.db.models import Q



# signup view

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = UserCreationForm()
    return render(request, "signup.html", {'form':form})

#lgon view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('feed')

    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form':form})    

#logout view

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# view for logged in user feed and logged out user feed
def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    if request.user.is_authenticated:
        return render(request, 'feed.html', {'posts':posts})
    else:
        return render(request, 'guest_feed.html', {'posts':posts})
    
# view for creating a post
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.post)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'post_create.html', {'form':form})
    
# view for deleting a post
@login_required
def post_delete(request, pk):
    post= get_object_or_404(post, pk=pk, user=request.user)
    post.delete()
    return redirect('feed')

#view for commenting on post
@login_required
def comment_create(request,pk):
    post = get_object_or_404(post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user=request.user
            comment.post=post
            comment.save()
            return redirect('feed')
    else:
        form = CommentForm()
    return render(request, 'comment_create.html', {'form':form, 'post':post})
#view for deleting a comment

@login_required
def comment_delete(request,pk):
    comment = get_object_or_404(comment, pk=pk, user=request.user)
    comment.delete()
    return redirect('feed')
#view for liking a post
@login_required
def like(request,pk):
    post = get_object_or_404(post, pk=pk)
    like_obj, created = like.object.get_or_create(user=request.user, post=post)
    if not created:
        like_obj.delete()
    like_count = like.objects.get_or_create(user=request.user, post=post)
    return redirect('feed')

# view for showing user's profile

def user_profile(request, username):
    user = get_object_or_404(user, username=username)
    posts = posts.objects.filter(user=user)
    likes = like.objects.filter(user=user)
    context = {
        'profile_user': user,
        'posts': posts,
        'likes': likes
    }
    return render(request, 'user_profile.html', context)

#view for showing other users profile for logged out users   

def guest_profile(request, username):
    user = get_object_or_404(user, username=username)
    posts = Post.objects.filter(user=user)
    return render(request, 'guest_profile.html', {'profile_user': user, 'posts':posts})

#view for changing a users username

@login_required
def change_username(request):
    if request.method == 'POST':
        form = UsernameChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

# update session to keep user logged iin 
            messages.success(request, 'your username has been updated.')
            return redirect('user_profile', user.username)
        else:
            form = UsernameChangeForm(instance=request.user)
        return render(request, 'change_username.html', {'form':form})
#view for searching user
def search_users(request):
    query = request.GET.get('q','')
    users = User.objects.filter(
        Q(username_icontains=query)|
        Q(first_name_icontains=query)|
        Q(last_name_icontains=query)
    )
    return render(request, 'search_users.html', {'users':users, 'query':query})



