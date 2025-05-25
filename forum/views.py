from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post, Comment
from django.db.models import Case, When
from .forms import CommentForm
from django.core.cache import cache
from django.urls import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class PostListView(ListView):
    model = Post
    template_name = 'forum/forum.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = None
    def get_queryset(self):
        page = int(self.request.GET.get('page', 1))
        all_post_ids = cache.get('post_list_all_ids')
        if all_post_ids is None:
            all_post_ids = list(Post.objects.order_by('-date_posted').values_list('id', flat=True))
            cache.set('post_list_all_ids', all_post_ids, 60*5)

        if not all_post_ids:
            return Post.objects.none()

        paginator = Paginator(all_post_ids, 5)
        max_page = paginator.num_pages
        page = max(1, min(page, max_page))

        cache_key = f'post_list_page_{page}'
        cached_post_ids = cache.get(cache_key)
        if cached_post_ids is None:
            start = (page - 1) * 5
            end = start + 5
            current_page_ids = all_post_ids[start:end]
            if not current_page_ids:
                return Post.objects.none()
            cache.set(cache_key, current_page_ids, 60*5)
        else:
            current_page_ids = cached_post_ids

        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(current_page_ids)])
        queryset = Post.objects.filter(pk__in=current_page_ids).order_by(preserved)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_post_ids = cache.get('post_list_all_ids')
        if all_post_ids is None:
            all_post_ids = list(Post.objects.order_by('-date_posted').values_list('id', flat=True))
            cache.set('post_list_all_ids', all_post_ids, 60*5)

        if not all_post_ids:
            context['page_obj'] = None
            context['is_paginated'] = False
            context['paginator'] = None
            return context

        paginator = Paginator(all_post_ids, 5)
        page_number = self.request.GET.get('page', 1)
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 1
        page_number = max(1, min(page_number, paginator.num_pages))
        try:
            page_obj = paginator.page(page_number)
        except (EmptyPage, PageNotAnInteger):
            page_obj = paginator.page(1)

        context['page_obj'] = page_obj
        context['is_paginated'] = paginator.num_pages > 1
        context['paginator'] = paginator
        return context

class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(post=self.object).order_by('date_posted')
        context['form'] = CommentForm()
        return context

@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('forum:post-detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'forum/post_detail.html', {'form': form})

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        return response

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        return response

    def test_func(self):
        return self.request.user == self.get_object().author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('forum:forum')
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return response

    def test_func(self):
        return self.request.user == self.get_object().author
