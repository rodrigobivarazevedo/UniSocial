from .models import Email
from network.models import User
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

@login_required
def mail(request):
    if request.user.is_authenticated:
        return render(request, "mail/inbox.html")
    else:
        return HttpResponseRedirect(reverse("login"))

@csrf_exempt
@login_required
def compose(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    usernames = [username.strip() for username in data.get("recipients").split(",")]
    if usernames == [""]:
        return JsonResponse({
            "error": "At least one recipient required."
        }, status=400)

    recipients = []
    for username in usernames:
        try:
            user = User.objects.get(username=username)
            recipients.append(user)
        except User.DoesNotExist:
            return JsonResponse({
                "error": f"User with username {username} does not exist."
            }, status=400)

    subject = data.get("subject", "")
    body = data.get("body", "")

    if body:
        users = set()
        users.add(request.user)
        users.update(recipients)
        for user in users:
            email = Email(
                user=user,
                sender=request.user,
                subject=subject,
                body=body,
                read=user == request.user
            )
            email.save()
            for recipient in recipients:
                email.recipients.add(recipient)
            email.save()

        messages.success(request, "Message sent successfully.") 
        request.session['messages'] = []

        return JsonResponse({"message": "Message sent successfully."}, status=201)
    else:
        messages.error(request, "Add a body content.") 
        request.session['messages'] = []

        return JsonResponse({"error": "Missing body content."}, status=400)

@login_required
def mailbox(request, mailbox):
    if mailbox == "inbox":
        emails = Email.objects.filter(
            user=request.user, recipients=request.user, archived=False
        )
    elif mailbox == "sent":
        emails = Email.objects.filter(
            user=request.user, sender=request.user, archived=False
        )
    elif mailbox == "archive":
        emails = Email.objects.filter(
            user=request.user, archived=True
        )
    else:
        return JsonResponse({"error": "Invalid mailbox."}, status=400)

    emails = emails.order_by("-timestamp").all()
    return JsonResponse([email.serialize() for email in emails], safe=False)

@login_required
def email(request, email_id):
    try:
        email = Email.objects.get(user=request.user, pk=email_id)
    except Email.DoesNotExist:
        return JsonResponse({"error": "Email not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(email.serialize())

    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("read") is not None:
            email.read = data["read"]
        if data.get("archived") is not None:
            email.archived = data["archived"]
        email.save()
        return HttpResponse(status=204)
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)





