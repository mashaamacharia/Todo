from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import Task, Category
from .forms import TaskForm, CategoryForm, UserRegistrationForm


# Create your views here.
def home(request):
    """View for the home page"""
    return render(request, 'todo_app/home.html')

def register(request):
    """View for user registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    """View for user profile"""
    tasks = Task.objects.filter(user=request.user)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    pending_tasks = total_tasks - completed_tasks

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
    }
    return render(request, 'registration/profile.html', context)


class TaskListView(LoginRequiredMixin, ListView):
    """View for listing all tasks for the logged-in user"""
    model = Task
    template_name = 'todo_app/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        """Filter tasks to show only those belonging to the current user"""
        queryset = Task.objects.filter(user=self.request.user)

        # Filter by category if specified
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        # Filter by completion status if specified
        status = self.request.GET.get('status')
        if status == 'completed':
            queryset = queryset.filter(completed=True)
        elif status == 'pending':
            queryset = queryset.filter(completed=False)

        return queryset

    def get_context_data(self, **kwargs):
        """Add categories to context for filtering"""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(user=self.request.user)
        return context


class TaskDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View for viewing a specific task"""
    model = Task
    template_name = 'todo_app/task_detail.html'

    def test_func(self):
        """Ensure users can only view their own tasks"""
        task = self.get_object()
        return task.user == self.request.user


class TaskCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new task"""
    model = Task
    form_class = TaskForm
    template_name = 'todo_app/task_form.html'
    success_url = reverse_lazy('task-list')

    def form_valid(self, form):
        """Set the current user as the task's owner"""
        form.instance.user = self.request.user
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        """Pass the current user to the form"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating an existing task"""
    model = Task
    form_class = TaskForm
    template_name = 'todo_app/task_form.html'
    success_url = reverse_lazy('task-list')

    def form_valid(self, form):
        """Ensure task owner remains the same"""
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)

    def test_func(self):
        """Ensure users can only edit their own tasks"""
        task = self.get_object()
        return task.user == self.request.user

    def get_form_kwargs(self):
        """Pass the current user to the form"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting a task"""
    model = Task
    template_name = 'todo_app/task_confirm_delete.html'
    success_url = reverse_lazy('task-list')

    def test_func(self):
        """Ensure users can only delete their own tasks"""
        task = self.get_object()
        return task.user == self.request.user

    def delete(self, request, *args, **kwargs):
        """Add success message on delete"""
        messages.success(self.request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)


@login_required
def toggle_task_completion(request, pk):
    """View for toggling task completion status"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('task-list')


@login_required
def category_create(request):
    """View for creating a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('task-list')
    else:
        form = CategoryForm()

    return render(request, 'todo_app/category_form.html', {'form': form})

