from django.db import models
from django.contrib.auth.models import User

# Create your models here.



class BlogPost(models.Model):
    body = models.TextField(null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    img_url = models.ImageField(upload_to='blog/img')
    subtitle = models.CharField(max_length=500)
    title = models.CharField(max_length=500, unique=True)
    author = models.ForeignKey(User, related_name='author', on_delete=models.CASCADE, verbose_name='Blog Author')
    

    class Meta:
        db_table = 'BlogPost'


class Comment(models.Model):
    comment_author = models.ForeignKey(User, related_name='commenter', verbose_name='Comment Author', on_delete=models.CASCADE)
    comment_text = models.CharField(max_length=500, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    blog_post = models.ForeignKey(
        BlogPost, related_name='comments', on_delete=models.CASCADE, verbose_name='Related Blog Post'
    )

    class Meta:
        db_table = 'Comment'
    

