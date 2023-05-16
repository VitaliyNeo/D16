from django.http import request, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Article, Comment, User, UserProfile
from .forms import PostForm, EditForm, CommentForm
from .filters import PostFilter
from .tasks import subscribe_confirmation_message


class ArticleList(ListView):
    model = Article
    template_name = 'home.html'
    ordering = ['-post_date']

    def get_context_data(self, *args, **kwargs):
        ''' Getting menue list of all post's categories for dropdown menue "Categories" in navbar '''
        cat_menu = Article.get_categories()
        context = super(ArticleList, self).get_context_data(*args, **kwargs)
        context['cat_menu'] = cat_menu
        return context


def CategoryView(request, cats):
    ''' List of all posts/articles by choosen category '''
    category_posts = Article.objects.filter(category=cats.replace('-', ' ')).order_by('-post_date')
    cat_menu = Article.get_categories()
    return render(request, 'categories.html',
                  {'cats': cats.title().replace('-', ' '), 'category_posts': category_posts, 'cat_menu': cat_menu})


class DashboardView(LoginRequiredMixin, ListView):
    ''' List of all posts posted by current User - author of posts '''
    ''' Also applied filter - search responses/comments by author's posts '''
    model = Article
    template_name = 'dashboard.html'
    context_object_name = 'author_posts'
    ordering = ['-post_date']

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user).order_by('-post_date')

    def get_context_data(self,
                         **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.request.user
        author_posts = Article.objects.filter(author=author).order_by('-post_date')
        cat_menu = Article.get_categories()
        context['cat_menu'] = cat_menu
        context['author_posts'] = author_posts
        context['filter'] = PostFilter(self.request.GET,
                                       queryset=self.get_queryset())
        return context


class ArticleDetailView(DetailView):
    ''' Show article/post with comments/responses'''
    model = Article
    template_name = 'article_details.html'

    def get_context_data(self, *args, **kwargs):
        cat_menu = Article.get_categories()
        context = super(DetailView, self).get_context_data(*args, **kwargs)

        current_post = get_object_or_404(Article, id=self.kwargs['pk'])
        post_comments = current_post.comments.order_by('-date_added')
        post_comments_count = current_post.comments.count()

        context['post_comments_count'] = post_comments_count
        context['post_comments'] = post_comments
        context['cat_menu'] = cat_menu
        return context


class AddPostView(LoginRequiredMixin, CreateView):
    ''' Creation of a new post by logged-in user '''
    model = Article
    form_class = PostForm
    template_name = 'add_post.html'

    def form_valid(self, form):
        ''' Autosaving current logged-in user as author after creating new post '''
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        ''' Getting menue list of all post's categories for dropdown menue "Categories" in navbar '''
        cat_menu = Article.get_categories()
        context = super(CreateView, self).get_context_data(*args, **kwargs)
        context['cat_menu'] = cat_menu
        return context


class AddCommentView(LoginRequiredMixin, CreateView):
    ''' Creation of a new response/comment by logged-in user '''
    model = Comment
    form_class = CommentForm
    template_name = 'add_comment.html'

    def form_valid(self, form):
        ''' Autosaving current logged in user as comment's author after creating this new comment '''
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        ''' Getting menue list of all post's categories for dropdown menue "Categories" in navbar '''
        cat_menu = Article.get_categories()
        context = super(CreateView, self).get_context_data(*args, **kwargs)
        context['cat_menu'] = cat_menu
        return context

    def get_success_url(self):
        return reverse_lazy('article-detail', kwargs={'pk': self.kwargs['pk']})


class UpdatePostView(LoginRequiredMixin, UpdateView):
    ''' Post/article editing by author '''
    model = Article
    template_name = 'update_post.html'
    form_class = EditForm

    def get_context_data(self, *args, **kwargs):
        ''' Getting menue list of all post's categories for dropdown menue "Categories" in navbar '''
        cat_menu = Article.get_categories()
        context = super(UpdateView, self).get_context_data(*args, **kwargs)
        context['cat_menu'] = cat_menu
        return context


class DeletePostView(LoginRequiredMixin, DeleteView):
    ''' Post/article deleting by author '''
    model = Article
    template_name = 'delete_post.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *args, **kwargs):
        ''' Getting menue list of all post's categories for dropdown menue "Categories" in navbar '''
        cat_menu = Article.get_categories()
        context = super(DeleteView, self).get_context_data(*args, **kwargs)
        context['cat_menu'] = cat_menu
        return context

@login_required
def comment_approve(request, pk):
    ''' Accept response - Button on 'article-detail' and 'dashboard' pages'''
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('article-detail', pk=comment.post.pk)


@login_required
def comment_disapprove(request, pk):
    ''' Unaccept response and remove approvement - Button on 'article-detail' and 'dashboard' pages'''
    comment = get_object_or_404(Comment, pk=pk)
    comment.disapprove()
    return redirect('article-detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    ''' Delete comment - Button on 'article-detail' and 'dashboard' pages'''
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('article-detail', pk=comment.post.pk)


@login_required
def news_subscribe(request, pk):
    ''' Weekly news and digest subscription - Button in Footer ('main.html' page) '''
    userprofile = get_object_or_404(UserProfile, user_id=request.user.id)
    userprofile.subscribe()
    user_name = request.user.username
    email = request.user.email
    subscribe_confirmation_message.delay(user_name, email)
    return redirect('home')


