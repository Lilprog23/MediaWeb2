from django.db import models
from django.utils import timezone




class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    f_name = models.CharField(max_length=50,default='Unknown')
    l_name = models.CharField(max_length=50, default=' User')    
    m_name = models.CharField(max_length=50, null=True, blank=True, default='')

    def is_following(self, other_user):
        return self.following.filter(following=other_user).exists()


    def __str__(self):
        return self.username
    
class Profile(models.Model):
    GENDER_CHOICES = [ 
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    cover_picture = models.ImageField(upload_to='cover_pictures/', default='profile_pictures/cover.jpg', null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/pro.jpg', null=True, blank=True)
    bio = models.TextField(max_length=100, null=True, blank=True,default=" Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the")
    b_day = models.DateField(null=True, blank=True, default='2000-01-01')
    phone_number = models.CharField(max_length=20, null=True, blank=True, default='0000000000')
    address = models.CharField(max_length=200, null=True, blank=True, default='No Address')
    gender = models.CharField(max_length=10, null=True, blank=True , choices=GENDER_CHOICES, default='M')
    total_likes = models.IntegerField(default=0)
    last_activity = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return  self.user.f_name + " " + self.user.l_name + " Profile"
    


from django.utils.timesince import timesince

class Upload_post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.f_name} {self.user.l_name}'s post"

    def time_since_posted(self):
        seconds = (timezone.now() - self.created_at).total_seconds()
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 172800:
            return "Yesterday"
        else:
            return timesince(self.created_at).split(',')[0] + " ago"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Upload_post, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class LikePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Upload_post, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.f_name} {self.user.l_name} likes {self.post.content}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=[
        ('comment', 'Comment'),
        ('like', 'Like'),
        ('follow', 'Follow')
    ])
    post = models.ForeignKey(Upload_post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='follower_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.user.f_name} {self.user.l_name} {self.notification_type} {self.post} {self.comment}"


class Conversation(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_conversations')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_conversations')
    timestamp = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    class Meta:
        unique_together = ('sender', 'recipient')
        ordering = ['-timestamp']  

    def __str__(self):
        return f"Conversation between {self.sender.f_name} {self.sender.l_name} and {self.recipient.f_name} {self.recipient.l_name}"

    @staticmethod
    def get_or_create_conversation(user1, user2):

        if user1 == user2:
            return None  
        sender, recipient = sorted([user1, user2], key=lambda u: u.id)
        conversation, created = Conversation.objects.get_or_create(
            sender=sender,
            recipient=recipient
        )
        return conversation


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']  
    def __str__(self):
        return f"Message from {self.user.f_name} {self.user.l_name}: {self.message[:20]}"



class SendFriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.f_name} {self.sender.l_name} sent a friend request to {self.recipient.f_name} {self.recipient.l_name}"


class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships')
    accepted_friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends')
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def accept_friendship(self):
        self.status = 'accepted'
        self.save()
        
        # Create mutual friendship
        Friend.objects.get_or_create(user=self.accepted_friend, accepted_friend=self.user, status='accepted')

    def reject_friendship(self):
        self.status = 'rejected'
        self.save()

        # Update the reverse friendship status to 'rejected' (or delete if that's preferred)
        reverse_friend = Friend.objects.filter(user=self.accepted_friend, accepted_friend=self.user, status='pending').first()
        if reverse_friend:
            reverse_friend.status = 'rejected'
            reverse_friend.save()

    def __str__(self):
        return f"{self.user.f_name} {self.user.l_name} and {self.accepted_friend.f_name} {self.accepted_friend.l_name} ({self.status})"
    
    class Meta:
        unique_together = ('user', 'accepted_friend')
