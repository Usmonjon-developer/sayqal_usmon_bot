from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from . import services


def login_required_decorator(func):
    return login_required(func, login_url='login_page')


# --- AUTH ---
@login_required_decorator
def logout_page(request):
    logout(request)
    return redirect("login_page")


def login_page(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home_page")
    return render(request, 'login.html')


@login_required_decorator
def home_page(request):
    categories = services.get_categories()
    products = services.get_products()
    users = services.get_users()
    suggestions = services.get_suggestions()
    ctx = {
        'counts': {
            'categories': len(categories),
            'products': len(products),
            'users': len(users),
            'suggestions': len(suggestions),
        }
    }
    return render(request, 'index.html', ctx)


# --- CATEGORY CRUD ---
@login_required_decorator
def category_list(request):
    categories = services.get_categories()
    ctx = {"categories": categories}
    return render(request, "category/list.html", ctx)


@login_required_decorator
def category_create(request):
    model = Category()
    form = CategoryForm(request.POST or None, request.FILES or None, instance=model)
    if request.POST and form.is_valid():
        form.save()
        return redirect("category_list")
    return render(request, "category/form.html", {"form": form})


@login_required_decorator
def category_edit(request, pk):
    model = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, request.FILES or None, instance=model)
    if request.POST and form.is_valid():
        form.save()
        return redirect("category_list")
    return render(request, "category/form.html", {"form": form, "model": model})


@login_required_decorator
def category_delete(request, pk):
    model = get_object_or_404(Category, pk=pk)
    model.delete()
    return redirect("category_list")


# --- PRODUCT CRUD ---
@login_required_decorator
def product_list(request):
    products = services.get_products()
    ctx = {"products": products}
    return render(request, "product/list.html", ctx)


@login_required_decorator
def product_create(request):
    model = Product()
    form = ProductForm(request.POST or None, request.FILES or None, instance=model)
    if request.POST and form.is_valid():
        form.save()
        return redirect("product_list")
    return render(request, "product/form.html", {"form": form})


@login_required_decorator
def product_edit(request, pk):
    model = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=model)
    if request.POST and form.is_valid():
        form.save()
        return redirect("product_list")
    return render(request, "product/form.html", {"form": form, "model": model})


@login_required_decorator
def product_delete(request, pk):
    model = get_object_or_404(Product, pk=pk)
    model.delete()
    return redirect("product_list")

# --- USER CRUD ---
@login_required_decorator
def user_list(request):
    users = services.get_users()
    ctx = {"users": users}
    return render(request, "user/list.html", ctx)

@login_required_decorator
def user_create(request):
    model = User()
    form = UserForm(request.POST or None, request.FILES or None, instance=model)
    if request.POST and form.is_valid():
        form.save()
        return redirect("user_list")
    return render(request, "user/form.html", {"form": form})


@login_required_decorator
def user_edit(request, pk):
    model = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, request.FILES or None, instance=model)
    if request.POST and form.is_valid():
        form.save()
        return redirect("user_list")
    return render(request, "user/form.html", {"form": form, "model": model})


@login_required_decorator
def user_delete(request, pk):
    model = get_object_or_404(User, pk=pk)
    model.delete()
    return redirect("user_list")

@login_required_decorator
def suggestion_list(request):
    suggestions = services.get_suggestions()
    ctx = {"suggestions": suggestions}
    return render(request, "suggestion/list.html", ctx)

@login_required_decorator
def suggestion_delete(request, pk):
    model = get_object_or_404(Suggestion, pk=pk)
    model.delete()
    return redirect("suggestion_list")