from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django import forms
from decimal import Decimal
from app.models import Project, Testimonial, BlogPost, FAQ,MyServices,LocationPrice, ContactServiceSelection
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import ContactForm
from django.core.paginator import Paginator
from .models import BlogPost, BlogCategory, BlogTag, Comment
from django.db.models import Q




from app.models import Project, Testimonial, ContactMessage, EstimateRequest, BlogPost, FAQ,MyServices
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


# Forms for validation
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'email', 'phone', 'subject', 'message']

class EstimateForm(forms.Form):
    length = forms.DecimalField(min_value=0.1, max_digits=10, decimal_places=2)
    width = forms.DecimalField(min_value=0.1, max_digits=10, decimal_places=2)
    ceiling_type = forms.ChoiceField(choices=[
        ('gypsum', 'Gypsum'), ('pop', 'POP'), ('pvc', 'PVC'),
        ('wooden', 'Wooden'), ('metal', 'Metal')
    ])
    quality = forms.ChoiceField(choices=[
        ('basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')
    ])
    include_lights = forms.BooleanField(required=False)
    location = forms.CharField(max_length=200, required=False)
    full_name = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20, required=False)


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['name', 'rating', 'message']
    
    rating = forms.IntegerField(min_value=1, max_value=5)

def index(request):
    featured_services = MyServices.objects.filter(is_active=True)[:4]
    featured_projects = Project.objects.filter(is_featured=True).order_by('-completed_date')[:6]
    testimonials = Testimonial.objects.filter(is_approved=True).order_by('-id')[:3]
    
    context = {
         'featured_services': featured_services,
        'featured_projects': featured_projects,
        'testimonials': testimonials,
    }
    return render(request, 'index.html', context)
def about(request):
    return render(request, 'about.html')


from django.core.paginator import Paginator


def myservices(request):
    category = request.GET.get('category', 'all')
    myprojects = MyServices.objects.filter(is_active=True).order_by('-created_at')

    # Filter by valid category
    valid_categories = dict(MyServices.CATEGORIES)
    if category != 'all' and category in valid_categories:
        myprojects = myprojects.filter(category=category)

    # Pagination
    paginator = Paginator(myprojects, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    return render(request, 'myservices.html', {
        'projects': page_obj,
        'categories': MyServices.CATEGORIES,
        'selected_category': category,
       
    })

def portfolio(request):
    category = request.GET.get('category', 'all')
    projects = Project.objects.all().order_by('-completed_date')
    
    # Filter by category if valid
    if category != 'all' and category in dict(Project.CATEGORIES).keys():
        projects = projects.filter(category=category)
    
    # Add pagination
    paginator = Paginator(projects, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Fetch approved testimonials
    testimonials = Testimonial.objects.filter(is_approved=True).order_by('-created_at')
    
    categories = Project.CATEGORIES
    return render(request, 'portfolio.html', {
        'projects': page_obj,
        'categories': categories,
        'selected_category': category,
        'testimonials': testimonials  # Pass testimonials to the template
    })

def contact(request):
    # Fetch active services and categories
    services = MyServices.objects.filter(is_active=True).order_by('category', 'title')
    

    active_categories = services.values_list('category', flat=True).distinct()
    category_choices = [(cat[0], cat[1]) for cat in MyServices.CATEGORIES if cat[0] in active_categories]


    if request.method == 'POST':
        form = ContactForm(request.POST)
        service_ids = request.POST.getlist('service[]')
        widths = request.POST.getlist('width[]')
        lengths = request.POST.getlist('length[]')

        if form.is_valid():
            submission = form.save()  # Save main submission

            # Save each selected service with width & length
            for i, service_id in enumerate(service_ids):
                if service_id:
                    ContactServiceSelection.objects.create(
                        submission=submission,
                        service_id=int(service_id),
                        width=float(widths[i]),
                        length=float(lengths[i])
                    )
            return redirect('contact')  # Redirect to avoid resubmission

    else:
        form = ContactForm()

    context = {
        'form': form,
        'services': services,
        'category_choices': category_choices,  # Pass proper category choices
    }

    return render(request, 'contact.html', context)

def estimate_calculator(request):
    # Get all active services
    services = MyServices.objects.filter(is_active=True)

    # Build a category → services mapping
    categories = {}
    for service in services:
        if service.category not in categories:
            categories[service.category] = []
        categories[service.category].append(service)

    # Get all location multipliers
    locations = LocationPrice.objects.all()

    return render(request, "estimate_calculator.html", {
        "categories": categories,   # dict: {category: [services]}
        "locations": locations,
    })

def testimonials(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your testimonial! It will be published after review.')
            return redirect('testimonials')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TestimonialForm()
    
    testimonials = Testimonial.objects.filter(is_approved=True).order_by('-id')
    return render(request, 'testimonials.html', {'testimonials': testimonials, 'form': form})


def blog(request):
    # Get all published posts
    posts = BlogPost.objects.filter(is_published=True).select_related('category', 'author')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get('category', '')
    current_category = None
    if category_slug:
        current_category = get_object_or_404(BlogCategory, slug=category_slug)
        posts = posts.filter(category=current_category)
    
    # Tag filter
    tag_name = request.GET.get('tag', '')
    if tag_name:
        posts = posts.filter(tags__name=tag_name)
    
    # Get featured post
    featured_post = BlogPost.objects.filter(
        is_published=True, 
        is_featured=True
    ).first()
    
    # Pagination
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get categories
    categories = BlogCategory.objects.all()
    
    # Get recent posts (excluding featured)
    recent_posts_qs = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    if featured_post:
        recent_posts_qs = recent_posts_qs.exclude(id=featured_post.id)
    recent_posts = recent_posts_qs[:5]
    
    # Get popular tags
    popular_tags = BlogTag.objects.all()[:10]
    
    context = {
        'posts': page_obj,
        'featured_post': featured_post,
        'categories': categories,
        'current_category': current_category,
        'recent_posts': recent_posts,
        'popular_tags': popular_tags,
    }
    
    return render(request, 'blog.html', context)


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Increment view count
    post.views += 1
    post.save(update_fields=['views'])
    
    # Get comments for this post
    comments = post.comments.all().order_by('-created_at')
    
    # Get recent posts (excluding current)
    recent_posts = BlogPost.objects.filter(
        is_published=True
    ).exclude(id=post.id).order_by('-created_at')[:5]
    
    # Get related posts (same category)
    related_posts = BlogPost.objects.filter(
        is_published=True,
        category=post.category
    ).exclude(id=post.id)[:3] if post.category else []
    
    # Get all categories with post count
    categories = BlogCategory.objects.all()
    
    # Get previous and next posts
    previous_post = BlogPost.objects.filter(
        is_published=True,
        created_at__lt=post.created_at
    ).order_by('-created_at').first()
    
    next_post = BlogPost.objects.filter(
        is_published=True,
        created_at__gt=post.created_at
    ).order_by('created_at').first()
    
    context = {
        'post': post,
        'comments': comments,
        'recent_posts': recent_posts,
        'related_posts': related_posts,
        'categories': categories,
        'previous_post': previous_post,
        'next_post': next_post,
    }
    
    return render(request, 'blog_detail.html', context)

def add_comment(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        body = request.POST.get("body")

        if name and email and body:
            Comment.objects.create(
                post=post,
                name=name,
                email=email,
                body=body
            )

    return redirect("blog_detail", slug=post.slug)


def blog(request):
    posts = BlogPost.objects.filter(is_published=True).order_by('-id')
    if not posts.exists():
        messages.info(request, 'No blog posts available.')
    
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog.html', {'page_obj': page_obj})

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    recent_posts = BlogPost.objects.filter(is_published=True).exclude(id=post.id).order_by('-id')[:3]
    
    return render(request, 'blog_detail.html', {
        'post': post,
        'recent_posts': recent_posts
    })


def faq(request):
    faqs = FAQ.objects.filter(is_active=True).order_by('question')
    return render(request, 'faq.html', {'faqs': faqs})




# import openai
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json

# @csrf_exempt
# def chat_api(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         user_message = data.get('message', '')
        
#         # TODO: Replace with your OpenAI API key
#         openai.api_key = 'your-api-key-here'
        
#         try:
#             response = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are a helpful receptionist for False Ceiling Services in Dhangadhi, Nepal. Help customers with information about ceiling types, pricing, scheduling, and services."},
#                     {"role": "user", "content": user_message}
#                 ]
#             )
            
#             return JsonResponse({
#                 'response': response.choices[0].message.content
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'response': 'I apologize for the inconvenience. Please call us at +977-9822662207.'
#             }, status=500)
    
#     return JsonResponse({'error': 'Invalid request'}, status=400)











def tools_view(request):
    return render(request, 'tools.html')  # or any template

def tools_tile_view(request):
    return render(request, 'tools_tile.html')

def tools_gypsum_view(request):
    return render(request, 'tools_gypsum.html')

def tools_partition_view(request):
    return render(request, 'tools_partition.html')

def tools_pvc_view(request):
    return render(request, 'tools_pvc.html')



class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome, {user.username}!")
                
                # ✅ Custom redirect based on username
                if user.username == 'admin05932':
                    return redirect('Admin_index')
                else:
                    return redirect('user_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'Admin_index.html')

@login_required
def user_dashboard(request):
    return render(request, 'user_dashboard.html')

@login_required
def admindashboard(request):
    return render(request, 'admin_dashboard.html')



@login_required
def inventory(request): return render(request, 'inventory.html')

@login_required
def sales(request): return render(request, 'sales.html')

@login_required
def customers(request): return render(request, 'customers.html')

@login_required
def employees(request): return render(request, 'employees.html')

@login_required
def invoice(request): return render(request, 'invoice.html')

@login_required
def purchase(request): return render(request, 'purchase.html')

@login_required
def expense(request): return render(request, 'expense.html')

@login_required
def tasks(request): return render(request, 'tasks.html')

@login_required
def payments(request): return render(request, 'payments.html')

@login_required
def website(request): return render(request, 'website.html')

@login_required
def ledger(request): return render(request, 'ledger.html')

@login_required
def settings(request): return render(request, 'settings.html')

@login_required
def subscription(request): return render(request, 'subscription.html')


def stockbook(request):
    return render(request, 'stockbook.html')

def attendance(request):
    return render(request, 'attendance.html')


