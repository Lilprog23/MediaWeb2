from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.db.models import Sum
from django.db.models import Q
from django.http import JsonResponse
# import set password


def loginPage(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                request.session['user_id']=user.id
                return redirect('home')
            else:
                return render(request, 'main/login.html', {'error': 'Invalid password'})
        except User.DoesNotExist:
            return render(request, 'main/login.html', {'error': 'User not found'})
    else:
        return render(request, 'main/login.html')
    
def logout_view(request):
    request.session.flush()
    return redirect('login')
from django.contrib.auth.hashers import make_password

def registerPage(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken')
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already taken')
            return redirect('register')
        
        user = User.objects.create(username=username, email=email)
        user.password = make_password(password)
        user.save()
        Profile.objects.create(user=user)
        messages.success(request, 'Account created successfully!')
        return redirect('login')
    else:
        return render(request, 'main/register.html')
    



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Upload_post
from django.http import JsonResponse

def homePage(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = get_object_or_404(User, id=request.session['user_id'])
    profile = user.profile
    posts = Upload_post.objects.all().order_by('-created_at')
    notifications = Notification.objects.filter(post__user=user).exclude(user=user).order_by('-created_at')

    conversations = Conversation.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-timestamp')
    sent_friend_requests = SendFriendRequest.objects.filter(recipient=user)

    
    accepted_requests = Friend.objects.filter(user=user, status='accepted')
    rejected_requests = Friend.objects.filter(user=user, status='rejected')

    
    Friend.objects.filter(user=user, status='pending').update(status='accepted')

    
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image') 
        video = request.FILES.get('video') 
        
        if content or image or video:  
            post = Upload_post(
                user=user,
                content=content,
                image=image,
                video=video
            )
            post.save()
            messages.success(request, 'Post uploaded successfully!')
            return redirect('home')  
    return render(request, 'main/home.html', {
        'user': user,
        'profile': profile,
        'posts': posts,
        'notifications': notifications,
        'sent_friend_requests': sent_friend_requests,  
        'accepted_requests': accepted_requests,  
        'rejected_requests': rejected_requests,  
        'conversations': conversations,
    })




def upload_post(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user = get_object_or_404(User, id=request.session['user_id'])

    if request.method == 'POST':
        video = request.FILES.get('video')
        content = request.POST.get('content')

        if content or video:
            post = Upload_post(
                user=user,
                video=video,
                content=content
            )
            post.save()
            return redirect('home')
    return render(request, 'main/upload_post.html')


def delete_post(request, post_id):
    if 'user_id' not in request.session:
        return redirect
    ('login')
    user = get_object_or_404(User, id=request.session['user_id'])
    post = get_object_or_404(Upload_post, id=post_id)
    if post.user == user:
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('home')
    else:
        messages.error(request, 'You are not authorized to delete this post.')
        return redirect('home')




def comment(request, post_id):
    if 'user_id' not in request.session:
        return redirect('login')
    user = get_object_or_404(User, id=request.session['user_id'])
    post = get_object_or_404(Upload_post, id=post_id)
    post_comments = Comment.objects.filter(post=post)
    
    comment_form = CommentForm()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = user
            comment.save()

           
            if user != post.user:
                Notification.objects.create(
                    user=post.user,  
                    notification_type='comment',
                    post=post,
                    comment=comment,
                    follower=user,
                    message=f" {user.f_name} {user.l_name} commented on your post"
                )

            messages.success(request, 'Comment added successfully!')
            return redirect('comment', post_id=post.id)

    context = {
        'post': post,
        'comment_form': comment_form,
        'post_comments': post_comments,
        'session_user_id': request.session['user_id'],
    }
    return render(request, 'main/comment.html', context)

def delete_comment(request, comment_id):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = get_object_or_404(User, id=request.session['user_id'])
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user == user:
        post_id = comment.post.id  
        comment.delete()
        return redirect('comment', post_id=post_id)
    else:
        return redirect('home')



def ProfilePage(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user = get_object_or_404(User, id=request.session['user_id'])
    profile = user.profile
    posts = Upload_post.objects.filter(user=user).order_by('-created_at')
    user_form = EditUserForm(instance=user)
    profile_form = EditUserProfileForm(instance=profile)
    profile = user.profile
    if request.method == 'POST':
            profile_picture = request.FILES.get('profile_picture')
            cover_picture = request.FILES.get('cover_picture')

            if profile_picture:
                profile.profile_picture = profile_picture
            if cover_picture:
                profile.cover_picture = cover_picture
            profile.save()
            return redirect('profile')
    
    return render(request, 'main/profile.html', {'profile': profile, 'user': user, 'posts': posts, 'user_form': user_form, 'profile_form': profile_form})




def edit_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = get_object_or_404(User, id=request.session['user_id'])
    profile = user.profile

    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=user)
        profile_form = EditUserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profileview')  

       
        return render(request, 'main/profileview.html', {
            'user_form': user_form,
            'profile_form': profile_form,
            'modal_open': True
        })

    
    return redirect('profileview')

def update_profile_picture(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user = get_object_or_404(User, id=request.session['user_id'])
    profile = get_object_or_404(Profile, user=user)
    if request.method == 'POST':
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            profile.profile_picture = profile_picture
            profile.save()
            posts = Upload_post.objects.create(user=user, content=f"{user.f_name} has updated profile picture!", image=profile_picture)
        return redirect('profileview')
    return render(request, 'main/update_profile_picture.html', {'user': user, 'profile': profile})



def update_cover_picture(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user = get_object_or_404(User, id=request.session['user_id'])
    profile = get_object_or_404(Profile, user=user)
    if request.method == 'POST':
        cover_picture = request.FILES.get('cover_picture')
        if cover_picture:
            profile.cover_picture = cover_picture
            profile.save()
            posts = Upload_post.objects.create(user=user, content=f"{user.f_name} has updated cover picture!", image=cover_picture)
        return redirect('profileview')
    return render(request, 'main/update_cover_picture.html', {'user': user, 'profile': profile}) 



def AboutPage(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user = get_object_or_404(User, id=request.session['user_id'])
    profile = user.profile

    return render(request, 'main/about.html', {'user': user, 'profile': profile})

from django.contrib import messages

from django.contrib import messages


def like_post(request, post_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=request.session['user_id'])
        post = get_object_or_404(Upload_post, id=post_id)

        like = LikePost.objects.filter(post=post, user=user).first()
        
        if like:
            like.delete()
            post.no_of_likes -= 1
            liked = False
        else:
            LikePost.objects.create(post=post, user=user)
            post.no_of_likes += 1
            liked = True

            
            if user != post.user:
                Notification.objects.create(
                    user=post.user,  
                    notification_type='like',
                    post=post,
                    follower=user,
                    message=f"{user.f_name} {user.l_name} liked your post"
                )
        post.save()
        return JsonResponse({'likes': post.no_of_likes, 'liked': liked})




def UserProfilePage(request, user_id):
    if 'user_id' not in request.session:
        return redirect('login')

    profile_user = get_object_or_404(User, id=user_id)
    logged_in_user = get_object_or_404(User, id=request.session['user_id'])

    if profile_user.id == logged_in_user.id:
        return redirect('profileview')

    are_friends = Friend.objects.filter(
        user=logged_in_user, accepted_friend=profile_user, status='accepted'
    ).exists()
    posts = Upload_post.objects.filter(user=profile_user).order_by('-created_at')


    friendship = Friend.objects.filter(user=logged_in_user, accepted_friend=profile_user, status='accepted').exists()
    outgoing_request = SendFriendRequest.objects.filter(sender=logged_in_user, recipient=profile_user, status='pending').first()
    incoming_request = SendFriendRequest.objects.filter(sender=profile_user, recipient=logged_in_user, status='pending').first()

    return render(request, 'main/user_profile.html', {
        'profile': profile_user.profile,
        'user': profile_user,
        'posts': posts,
        'profile_user': profile_user,
        'friendship': friendship,
        'outgoing_request': outgoing_request,
        'incoming_request': incoming_request,
        'are_friends': are_friends,
    })




def send_message(request, recipient_id):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = get_object_or_404(User, id=request.session['user_id'])
    recipient = get_object_or_404(User, id=recipient_id)

    conversation = Conversation.get_or_create_conversation(user, recipient)
    
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            Message.objects.create(conversation=conversation, user=user, message=message_text)
            return redirect('conversation-detail', conversation_id=conversation.id)

    if conversation:
        return redirect('conversation-detail', conversation_id=conversation.id)
    
    return render(request, 'main/send_message.html', {
        'recipient': recipient,
        'conversation': conversation,
    })


def inbox(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user = get_object_or_404(User, id=request.session['user_id'])
    profile = get_object_or_404(Profile, user=user)
    conversations = Conversation.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-timestamp')
    return render(request, 'main/inbox.html', {'conversations': conversations, 'profile': profile})



def conversation_detail(request, conversation_id):
    if 'user_id' not in request.session:
        return redirect('login')
    user = get_object_or_404(User, id=request.session['user_id'])
    conversation = get_object_or_404(Conversation, id=conversation_id)
    messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        message = request.POST.get('message')
        Message.objects.create(conversation=conversation, user=user, message=message)
        return redirect('conversation-detail', conversation_id=conversation_id)
    
    return render(request, 'main/conversation_detail.html', {'conversation': conversation, 'messages': messages, 'profile': profile})

def delete_conversation(request, conversation_id):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = get_object_or_404(User, id=request.session['user_id'])
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if conversation.sender == user or conversation.recipient == user:
        conversation.delete()
        messages.success(request, 'Conversation deleted successfully!')
        return redirect('home')
    else:
        messages.error(request, 'You are not authorized to delete this conversation.')
        return redirect('home')

def dashboard(request):
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
    has_notifications = unread_notifications.exists()
    return render(request, 'home.html', {
        'has_notifications': has_notifications
    })



def send_friend_request(request, user_id):
    if 'user_id' not in request.session:
        return redirect('login')

    current_user = get_object_or_404(User, id=request.session['user_id'])
    recipient = get_object_or_404(User, id=user_id)

    if SendFriendRequest.objects.filter(sender=current_user, recipient=recipient, status='pending').exists():
        messages.info(request, f"You've already sent a friend request to {recipient.username}.")
        return redirect('view_profile', user_id=user_id)

    
    friend_request = SendFriendRequest.objects.create(sender=current_user, recipient=recipient)

   
    Notification.objects.create(
        user=recipient,  
        notification_type='friend_request',
        follower=current_user,
        message=f"{current_user.f_name} {current_user.l_name} sent you a friend request"
    )

    messages.success(request, f"You've sent a friend request to {recipient.username}.")
    return redirect('view_profile', user_id=user_id)
from django.views.decorators.csrf import csrf_exempt

def accept_friend_request(request, request_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated.'}, status=403)

    user = get_object_or_404(User, id=request.session['user_id'])  # Recipient (User1)
    friend_request = get_object_or_404(SendFriendRequest, id=request_id)

    if friend_request.recipient != user:
        return JsonResponse({'error': 'Unauthorized action.'}, status=403)

    if Friend.objects.filter(user=user, accepted_friend=friend_request.sender, status='accepted').exists():
        return JsonResponse({'message': 'You are already friends with this user.'}, status=200)

    
    Friend.objects.create(user=friend_request.sender, accepted_friend=user, status='accepted')
    Friend.objects.create(user=user, accepted_friend=friend_request.sender, status='accepted')

   
    Notification.objects.create(
        user=friend_request.sender, 
        notification_type='friend_accept',
        follower=user,  
        message=f"{user.f_name} accepted your friend request"
    )

    
    friend_request.delete()

    return JsonResponse({'message': f"You are now friends with {friend_request.sender.username}!"})


@csrf_exempt
def reject_friend_request(request, request_id):
    if 'user_id' not in request.session:
    
        return redirect('login')

    user = get_object_or_404(User, id=request.session['user_id'])

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

    friend_request = get_object_or_404(SendFriendRequest, id=request_id)

    if friend_request.recipient.id != request.session['user_id']:
        return JsonResponse({'error': 'Unauthorized.'}, status=403)

    friend_request.delete()
    return JsonResponse({'message': 'Friend request rejected successfully.'})


from datetime import timedelta

def friends_list(request):
    if 'user_id' not in request.session:
        return redirect('login')

    current_user = get_object_or_404(User, id=request.session['user_id'])

    sent_friendships = Friend.objects.filter(user=current_user, status='accepted').select_related('accepted_friend__profile')
    received_friendships = Friend.objects.filter(accepted_friend=current_user, status='accepted').select_related('user__profile')

    all_friends = set()
    for friendship in sent_friendships:
        friend = friendship.accepted_friend
        friend.online = is_online(friend.profile.last_activity)
        all_friends.add(friend)

    for friendship in received_friendships:
        friend = friendship.user
        friend.online = is_online(friend.profile.last_activity)
        all_friends.add(friend)

    context = {'friends': list(all_friends)}
    return render(request, 'main/friends_list.html', context)

def unfriend(request, user_id):
    if 'user_id' not in request.session:
        return redirect('login')

    current_user = get_object_or_404(User, id=request.session['user_id'])
    friend_to_remove = get_object_or_404(User, id=user_id)

    # Find and delete the friendship relationship in both directions
    friend_relationship = Friend.objects.filter(
        user=current_user, accepted_friend=friend_to_remove, status='accepted'
    ).first()

    reverse_friend_relationship = Friend.objects.filter(
        user=friend_to_remove, accepted_friend=current_user, status='accepted'
    ).first()

    if friend_relationship:
        friend_relationship.delete()
        messages.success(request, f"You are no longer friends with {friend_to_remove.username}.")

    if reverse_friend_relationship:
        reverse_friend_relationship.delete()

    return redirect('view_profile', user_id=user_id)


def view_profile(request, user_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    profile_user = get_object_or_404(User, id=user_id)
    logged_in_user = get_object_or_404(User, id=request.session['user_id'])
    if profile_user.id == logged_in_user.id:
        return redirect('profileview')

    return render(request, 'main/view_profile.html', {'user': user, 'profile': profile})


def edit_post_content(request, post_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = get_object_or_404(User, id=request.session['user_id'])
    post = get_object_or_404(Upload_post, id=post_id)

    if post.user != user:
        messages.error(request, 'You are not authorized to edit this post.')
        return redirect('home')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content.strip():
            post.content = content
            post.save()
            messages.success(request, 'Post content updated successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Content cannot be empty.')

    return render(request, 'main/edit_post_content.html', {'post': post})



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def edit_post_ajax(request, post_id):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False})

        try:
            user = User.objects.get(id=user_id)
            post = Upload_post.objects.get(id=post_id, user=user)
            data = json.loads(request.body)
            content = data.get('content')

            if content:
                post.content = content
                post.save()
                return JsonResponse({'success': True})
        except Exception as e:
            print("Error:", e)

    return JsonResponse({'success': False})

@csrf_exempt
def cancel_friend_request(request, request_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = get_object_or_404(User, id=request.session['user_id'])

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

    friend_request = get_object_or_404(SendFriendRequest, id=request_id)

    if friend_request.sender.id != request.session['user_id']:
        return JsonResponse({'error': 'Unauthorized.'}, status=403)

    friend_request.delete()

    return JsonResponse({'message': 'Friend request canceled successfully.'})


from datetime import timedelta
from django.utils import timezone

def is_online(last_activity):
    return timezone.now() - last_activity < timedelta(minutes=5)


def notification_view(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = get_object_or_404(User, id=request.session['user_id'])

    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    unread_notifications = notifications.filter(is_read=False)

    for notification in unread_notifications:
        notification.is_read = True
        notification.save()

    return render(request, 'main/Notification.html', {'notifications': notifications})