from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Service(models.Model):
    CATEGORY_CHOICES = [
        ('tile', 'Tile'),
        ('gypsum', 'Gypsum'),
        ('pvc', 'PVC'),
        ('partition', 'Partition'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField()
    image = models.ImageField(upload_to='services/')
    price_per_sqft = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)


class MyServices(models.Model):
    CATEGORIES = [
        ('tile', 'Tile'),
        ('gypsum', 'Gypsum'),
        ('partition', 'Partition'),
        ('pvc', 'PVC'),
        ('repairing', 'Repairing'),
        ('others', 'Others'),
    ]

    title = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to='myservices/')
    category = models.CharField(max_length=20, choices=CATEGORIES)
    price_per_sqft = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_featured = models.BooleanField(default=False)


    def __str__(self):
        return self.title  


class LocationPrice(models.Model):
    location = models.CharField(max_length=150, unique=True)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    # Example: 50.00 = add 50 units to base price

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.location} (+{self.additional_price})"



class Project(models.Model):
    CATEGORIES = [
        ('living_room', 'Living Room'),
        ('office', 'Office'),
        ('hall', 'Hall'),
        ('bedroom', 'Bedroom'),
        ('commercial', 'Commercial'),
    ]
    
    title = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/')
    category = models.CharField(max_length=20, choices=CATEGORIES)
    location = models.CharField(max_length=100)
    material_used = models.CharField(max_length=100)
    completed_date = models.DateField()
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    message = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    location = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='testimonials/', blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name} - {self.rating} stars"




class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
    @property
    def post_count(self):
        return self.blogpost_set.filter(is_published=True).count()


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_responded = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.full_name} - {self.subject}"

class EstimateRequest(models.Model):
    CEILING_TYPES = [
        ('gypsum', 'Gypsum Ceiling'),
        ('pop', 'POP Ceiling'),
        ('pvc', 'PVC Ceiling'),
        ('wooden', 'Wooden Ceiling'),
        ('metal', 'Metal Grid Ceiling'),
    ]
    
    QUALITY_LEVELS = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    
    full_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    length = models.DecimalField(max_digits=8, decimal_places=2)
    width = models.DecimalField(max_digits=8, decimal_places=2)
    ceiling_type = models.CharField(max_length=20, choices=CEILING_TYPES)
    quality = models.CharField(max_length=20, choices=QUALITY_LEVELS)
    include_lights = models.BooleanField(default=False)
    location = models.CharField(max_length=100, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Estimate - {self.ceiling_type} - Rs. {self.estimated_cost}"


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=300)

    image = models.ImageField(upload_to='blog/', blank=True, null=True)  # Renamed from featured_image
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']

    featured_image = models.ImageField(upload_to='blog/')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    
    def __str__(self):
        return self.title



class BlogTag(models.Model):
    name = models.CharField(max_length=50)
    posts = models.ManyToManyField(BlogPost, related_name='tags')
    
    def __str__(self):
        return self.name
    
# models.py
class Comment(models.Model):
    post = models.ForeignKey(BlogPost, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.name}"



class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):

        return self.question
    

class ContactSubmission(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=250)
    rooms = models.PositiveIntegerField(default=1) 
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    services = models.ManyToManyField(MyServices, through='ContactServiceSelection')

    def __str__(self):
        return f"{self.full_name} - {self.created_at.strftime('%Y-%m-%d')}"

class ContactServiceSelection(models.Model):
    submission = models.ForeignKey(ContactSubmission, on_delete=models.CASCADE)
    service = models.ForeignKey(MyServices, on_delete=models.CASCADE)
    width = models.FloatField()
    length = models.FloatField()

    def __str__(self):
        return f"{self.submission.full_name} - {self.service.title}"

        return self.question

