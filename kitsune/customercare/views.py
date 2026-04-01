import json
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from kitsune.customercare.models import SupportTicket
from kitsune.customercare.utils import generate_classification_tags, sync_ticket_from_zendesk
from kitsune.products.models import Topic

log = logging.getLogger("k.customercare")


@login_required
def ticket_detail(request, username, ticket_id):
    ticket = get_object_or_404(
        SupportTicket.objects.select_related("product", "topic", "user"),
        id=ticket_id,
        user__username=username,
    )
    if not (ticket.user_id == request.user.id or request.user.has_perm("customercare.change_supportticket")):
        raise Http404

    if request.headers.get("HX-Request"):
        sync_error = False
        try:
            sync_ticket_from_zendesk(ticket)
        except Exception:
            log.exception("Failed to sync ticket %s from Zendesk", ticket.zendesk_ticket_id)
            sync_error = True
        return render(request, "customercare/includes/ticket_replies.html",
                      {"ticket": ticket, "sync_error": sync_error})

    threshold = timedelta(seconds=settings.ZENDESK_COMMENTS_SYNC_THRESHOLD)
    needs_sync = bool(ticket.zendesk_ticket_id) and (
        ticket.last_synced_at is None or ticket.last_synced_at < timezone.now() - threshold
    )
    return render(request, "customercare/ticket_detail.html", {
        "ticket": ticket,
        "needs_sync": needs_sync,
    })


@require_POST
@permission_required("customercare.change_supportticket")
def update_topic(request, ticket_id):
    """Update topic for a support ticket."""
    ticket = get_object_or_404(SupportTicket, pk=ticket_id)

    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"error": "AJAX required"}, status=400)

    data = json.loads(request.body)
    new_topic_id = data.get("topic")

    try:
        new_topic = Topic.objects.get(id=new_topic_id, products=ticket.product)
    except Topic.DoesNotExist:
        return JsonResponse({"error": "Topic not found"}, status=404)

    ticket.topic = new_topic
    ticket.save(update_fields=["topic"])

    # Regenerate tags from new topic
    system_tags = [
        tag for tag in ticket.zendesk_tags if tag in ["loginless_ticket", "stage", "other"]
    ]
    classification_tags = generate_classification_tags(
        ticket, {"topic_result": {"topic": new_topic.title}}
    )
    ticket.zendesk_tags = system_tags + classification_tags
    ticket.save(update_fields=["zendesk_tags"])

    return JsonResponse({"updated_topic": str(new_topic)})
