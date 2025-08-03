from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django import forms
from decimal import Decimal
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
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you! Your message has been sent successfully. We will contact you soon.')
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})


def estimate_calculator(request):
    base_prices = {
        'gypsum': {'basic': 180, 'standard': 220, 'premium': 280},
        'pop': {'basic': 150, 'standard': 200, 'premium': 250},
        'pvc': {'basic': 120, 'standard': 160, 'premium': 200},
        'wooden': {'basic': 300, 'standard': 400, 'premium': 550},
        'metal': {'basic': 200, 'standard': 250, 'premium': 320},
    }
    
    lighting_cost_per_sqft = 50  # Cost per sqft for lighting
    
    if request.method == 'POST':
        form = EstimateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            length = data['length']
            width = data['width']
            ceiling_type = data['ceiling_type']
            quality = data['quality']
            include_lights = data['include_lights']
            
            # Calculate area and costs
            area = length * width
            price_per_sqft = Decimal(base_prices[ceiling_type][quality])
            material_cost = area * price_per_sqft
            labor_cost = material_cost * Decimal('0.4')  # 40% of material cost
            lighting_cost = area * Decimal(lighting_cost_per_sqft) if include_lights else Decimal('0')
            total_cost = material_cost + labor_cost + lighting_cost
            
            # Prepare estimate breakdown
            estimate_data = {
                'length': length,
                'width': width,
                'area': round(float(area), 2),
                'ceiling_type': dict(form.fields['ceiling_type'].choices).get(ceiling_type),
                'quality': dict(form.fields['quality'].choices).get(quality),
                'include_lights': include_lights,
                'price_per_sqft': float(price_per_sqft),
                'material_cost': round(float(material_cost), 2),
                'labor_cost': round(float(labor_cost), 2),
                'lighting_cost': round(float(lighting_cost), 2),
                'total_cost': round(float(total_cost), 2),
                'base_prices': base_prices,
                'lighting_cost_per_sqft': lighting_cost_per_sqft,
            }
            
            # Save estimate if contact info provided
            if data.get('full_name') or data.get('phone'):
                EstimateRequest.objects.create(
                    full_name=data.get('full_name', ''),
                    phone=data.get('phone', ''),
                    length=length,
                    width=width,
                    ceiling_type=ceiling_type,
                    quality=quality,
                    include_lights=include_lights,
                    location=data.get('location', ''),
                    estimated_cost=total_cost
                )
                messages.success(request, 'Your estimate request has been saved! We will contact you soon.')
            
            return render(request, 'estimate_calculator.html', {
                'estimate': estimate_data,
                'form': form,
                'show_results': True
            })
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EstimateForm()
    
    return render(request, 'estimate_calculator.html', {
        'form': form,
        'base_prices': base_prices,
        'lighting_cost_per_sqft': lighting_cost_per_sqft,
        'show_results': False
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


