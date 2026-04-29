from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message


@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user, is_draft=False)
    return render(request, 'inbox.html', {'messages': messages})


@login_required
def sent(request):
    messages = Message.objects.filter(sender=request.user, is_draft=False)
    return render(request, 'sent.html', {'messages': messages})


@login_required
def drafts(request):
    messages = Message.objects.filter(sender=request.user, is_draft=True)
    return render(request, 'drafts.html', {'messages': messages})


@login_required
def compose(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        subject = request.POST.get('subject')
        content = request.POST.get('content')

        receiver = User.objects.get(id=receiver_id)

        is_draft = 'draft' in request.POST

        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            subject=subject,
            content=content,
            is_draft=is_draft
        )

        return redirect('inbox')

    users = User.objects.exclude(id=request.user.id)
    return render(request, 'compose.html', {'users': users})



