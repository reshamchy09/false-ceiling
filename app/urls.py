from django.urls import path
from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
   path('myservices/', views.myservices, name='myservices'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('contact/', views.contact, name='contact'),
    path('estimate-calculator/', views.estimate_calculator, name='estimate_calculator'), 
    path('testimonials/', views.testimonials, name='testimonials'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
<<<<<<< HEAD
     path("blog/<slug:slug>/comment/", views.add_comment, name="add_comment"),  
    path('faq/', views.faq, name='faq'),
   # path('api/chat/', views.chat_api, name='chat_api'),
=======
    path('faq/', views.faq, name='faq'),
>>>>>>> 31933a6aed56f036f217f6b67518393184056343


    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('Admin_index/', views.dashboard, name='Admin_index'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),



     path('inventory/', views.inventory, name='inventory'),
    path('sales/', views.sales, name='sales'),
    path('customers/', views.customers, name='customers'),
    path('employees/', views.employees, name='employees'),
    path('invoice/', views.invoice, name='invoice'),
    path('purchase/', views.purchase, name='purchase'),
    path('expense/', views.expense, name='expense'),
    path('tasks/', views.tasks, name='tasks'),
    path('payments/', views.payments, name='payments'),
    path('website/', views.website, name='website'),
    path('ledger/', views.ledger, name='ledger'),
    path('settings/', views.settings, name='settings'),
     path('subscription/', views.subscription, name='subscription'),
       path('admin_dashboard/', views.admindashboard, name='admin_dashboard'),
       path('stockbook/', views.stockbook, name='stockbook'),
    path('attendance/', views.attendance, name='attendance'),





 path('tools/', views.tools_view, name='tools'),
      path('tools_tile/', views.tools_tile_view, name='tools_tile'),
 path('tool_gypsum/', views.tools_gypsum_view, name='tools_gypsum'),
     path('tool_partition/', views.tools_partition_view, name='tools_partition'),
      path('tool_pvc/', views.tools_pvc_view, name='tools_pvc'),
]