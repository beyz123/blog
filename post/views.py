import json

from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect, redirect, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView

import post
from .models import Post
from .forms import PostForm, CommentForm
from django.contrib import messages
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse


@csrf_exempt
def post_like(request):
    pk = request.POST.get('post_id')
    post = get_object_or_404(Post, id=pk)
    message = ""
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        message = "Postu Beğenmekten Vazgeçtiniz ! :("
    else:
        post.likes.add(request.user)
        message = "Postu Beğendiniz ! :)"

    return HttpResponse(json.dumps({"detail": message}), status=200)


class PostDetailView(DetailView):
    model = Post
    template_name = "post/detail.html"

    def total_likes_received(self):
        total_likes_received = post_like.objects.filter(post__author=post.author).count()
        return total_likes_received

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        total_likes_received = Post.objects.filter(post__author=self.request.user).count()
        context['total_likes_received'] = self.total_likes_received()
        return context


def post_index(request):
    post_list = Post.objects.all()

    query = request.GET.get('q')
    if query:
        post_list = post_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        ).distinct()

    paginator = Paginator(post_list, 5)  # Show 25 contacts per page

    page = request.GET.get('sayfa')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        posts = paginator.page(paginator.num_pages)

    return render(request, 'post/index.html', {'posts': posts})


def my_posts(request):
    if request.user.is_authenticated:
        post_list = Post.objects.filter(user=request.user)

    paginator = Paginator(post_list, 5)

    page = request.GET.get('sayfa')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        posts = paginator.page(paginator.num_pages)

    return render(request, 'post/index.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        return HttpResponseRedirect(post.get_absolute_url())

    context = {
        'post': post,
        'form': form,
    }
    return render(request, 'post/detail.html', context)


def post_create(request):
    if not request.user.is_authenticated:
        return Http404()
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.user = request.user
        post.save()
        messages.success(request, 'Başarılı bir şekilde oluşturdunuz.', extra_tags='mesaj-basarili')
        return HttpResponseRedirect(post.get_absolute_url())

    context = {'form': form}

    return render(request, 'post/form.html', context)


def post_update(request, slug):
    if not request.user.is_authenticated:
        return Http404()
    post = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        post = form.save()
        post.save()
        messages.success(request, 'Başarılı bir şekilde kaydedildi.', extra_tags='mesaj basarili')
        return HttpResponseRedirect(post.get_absolute_url())

    context = {
        'form': form,
    }
    return render(request, 'post/form.html', context)


def post_delete(request, slug):
    if not request.user.is_authenticated:
        return Http404()

    post = get_object_or_404(Post, slug=slug)
    post.delete()

    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save()
        messages.success(request, 'Başarılı bir şekilde sildiniz.', extra_tags='mesaj-basarili')
        return HttpResponseRedirect(post.get_absolute_url())

    return redirect('post:index')
