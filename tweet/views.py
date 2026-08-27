from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
from .models import Tweet
from .forms import TweetForm, UserRegistrationForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login


def tweet_list(request):
    """Displays all tweets or filters them based on a search query."""
    query = request.GET.get('search')
    if query:
        tweets = Tweet.objects.filter(
            Q(text__icontains=query) | Q(user__username__icontains=query)
        ).order_by('-created_at')
    else:
        tweets = Tweet.objects.all().order_by('-created_at')

    return render(request, 'tweet/tweet_list.html', {'tweets': tweets})


@login_required
def tweet_create(request):
    """Handles tweet creation for logged-in users."""
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            messages.success(request, 'Tweet posted successfully!')
            return redirect('tweet_list')
    else:
        form = TweetForm()

    return render(request, 'tweet/tweet_form.html', {'form': form})


@login_required
def tweet_edit(request, tweet_id):
    """Allows a user to edit their own tweet."""
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            form.save()
            messages.info(request, 'Tweet updated successfully!')
            return redirect('tweet_list')
    else:
        form = TweetForm(instance=tweet)

    return render(request, 'tweet/tweet_form.html', {'form': form})


@login_required
def tweet_delete(request, tweet_id):
    """Allows a user to delete their own tweet."""
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == 'POST':
        tweet.delete()
        messages.warning(request, 'Tweet deleted.')
        return redirect('tweet_list')

    return render(request, 'tweet/tweet_confirm_delete.html', {'tweet': tweet})


@login_required
def tweet_like(request, tweet_id):
    """Toggles like/unlike on a tweet."""
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    if tweet.likes.filter(id=request.user.id).exists():
        tweet.likes.remove(request.user)
    else:
        tweet.likes.add(request.user)
    return redirect('tweet_list')


def register(request):
    """Handles new user registration and logs them in immediately."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Tweetbar, {user.username}!')
            return redirect('tweet_list')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Registration failed. Please check the requirements below.')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('tweet_list')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})