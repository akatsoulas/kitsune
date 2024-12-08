import json

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from kitsune.access.decorators import group_required, login_required, permission_required
from kitsune.flagit.models import FlaggedObject
from kitsune.products.models import Product, Topic
from kitsune.questions.events import QuestionReplyEvent
from kitsune.questions.models import Answer, Question
from kitsune.sumo.templatetags.jinja_helpers import urlparams
from kitsune.sumo.urlresolvers import reverse
from kitsune.tags.models import SumoTag


def get_flagged_objects(reason=None, exclude_reason=None, content_model=None, product_slug=None):
    """Retrieve pending flagged objects with optional filtering, eager loading related fields."""
    queryset = FlaggedObject.objects.pending().select_related("content_type", "creator")
    if exclude_reason:
        queryset = queryset.exclude(reason=exclude_reason)
    if reason:
        queryset = queryset.filter(reason=reason)
    if content_model:
        queryset = queryset.filter(content_type=content_model)
    if product_slug:
        matching_product_ids = [
            obj.id
            for obj in queryset
            if hasattr(obj.content_object, "product")
            and obj.content_object.product.slug == product_slug
        ]
        queryset = queryset.filter(id__in=matching_product_ids)
    return queryset


def set_form_action_for_objects(objects, reason=None, product_slug=None):
    """Generate form action URLs for flagged objects."""
    for obj in objects:
        base_url = reverse("flagit.update", args=[obj.id])
        obj.form_action = urlparams(base_url, reason=reason, product=product_slug)
    return objects


@require_POST
@login_required
def flag(request, content_type=None, model=None, object_id=None, **kwargs):
    if model:
        content_type = ContentType.objects.get_for_model(model).id
    content_type = content_type or request.POST.get("content_type")
    object_id = int(object_id or request.POST.get("object_id"))

    content_type = get_object_or_404(ContentType, id=int(content_type))
    content_object = get_object_or_404(content_type.model_class(), pk=object_id)

    reason = request.POST.get("reason")
    notes = request.POST.get("other", "")
    next = request.POST.get("next")

    moderation_flag_query = FlaggedObject.objects.filter(
        content_type=content_type,
        object_id=object_id,
        reason=FlaggedObject.REASON_CONTENT_MODERATION,
    ).exclude(status=FlaggedObject.FLAG_DUPLICATE)
    default_kwargs = {"content_object": content_object, "reason": reason, "notes": notes}
    if reason == FlaggedObject.REASON_CONTENT_MODERATION:
        moderation_flag_query.update(status=FlaggedObject.FLAG_PENDING)
        default_kwargs["status"] = FlaggedObject.FLAG_DUPLICATE
    else:
        moderation_flag_query.delete()

    # Check that this user hasn't already flagged the object
    _flagged, created = FlaggedObject.objects.get_or_create(
        content_type=content_type,
        object_id=object_id,
        creator=request.user,
        defaults=default_kwargs,
    )
    msg = (
        _("You already flagged this content.")
        if not created
        else _("You have flagged this content. A moderator will review your submission shortly.")
    )

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return HttpResponse(json.dumps({"message": msg}))
    elif next:
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(next)

    return HttpResponse(msg)


@login_required
@permission_required("flagit.can_moderate")
def flagged_queue(request):
    """Display the flagged queue with optimized queries."""
    reason = request.GET.get("reason")

    objects = (
        get_flagged_objects(reason=reason, exclude_reason=FlaggedObject.REASON_CONTENT_MODERATION)
        .select_related("content_type", "creator")
        .prefetch_related("content_object")
    )
    objects = set_form_action_for_objects(objects, reason=reason)

    return render(
        request,
        "flagit/queue.html",
        {
            "objects": objects,
            "locale": request.LANGUAGE_CODE,
            "reasons": FlaggedObject.REASONS,
            "selected_reason": reason,
        },
    )


def get_hierarchical_topics(topics, parent=None, level=0):
    """Recursively build hierarchical topics."""
    hierarchical = []
    for topic in topics.filter(parent=parent).order_by("title"):
        spaces = "&nbsp;" * (level * 4)
        hierarchical.append({"id": topic.id, "title": f"{spaces}{topic.title}"})
        hierarchical.extend(get_hierarchical_topics(topics, parent=topic, level=level + 1))
    return hierarchical


@group_required("Content Moderators")
def moderate_content(request):
    """Display flagged content that needs moderation."""
    product_slug = request.GET.get("product")

    content_type = ContentType.objects.get_for_model(Question)
    objects = (
        get_flagged_objects(
            reason=FlaggedObject.REASON_CONTENT_MODERATION,
            content_model=content_type,
            product_slug=product_slug,
        )
        .select_related("content_type", "creator")
        .prefetch_related("content_object__product")
    )
    objects = set_form_action_for_objects(
        objects, reason=FlaggedObject.REASON_CONTENT_MODERATION, product_slug=product_slug
    )
    available_tags = SumoTag.objects.segmentation_tags().values("id", "name")

    for obj in objects:
        question = obj.content_object
        all_topics = Topic.active.filter(is_archived=False, products=question.product)
        obj.available_topics = get_hierarchical_topics(all_topics)
        obj.available_tags = available_tags
        obj.saved_tags = question.tags.values_list("id", flat=True)
    return render(
        request,
        "flagit/content_moderation.html",
        {
            "objects": objects,
            "locale": request.LANGUAGE_CODE,
            "products": [
                (p.slug, p.title)
                for p in Product.active.filter(codename="", aaq_configs__is_active=True)
            ],
            "selected_product": product_slug,
        },
    )


@require_POST
@login_required
@permission_required("flagit.can_moderate")
def update(request, flagged_object_id):
    """Update the status of a flagged object."""
    flagged = get_object_or_404(FlaggedObject, pk=flagged_object_id)
    new_status = request.POST.get("status")
    reason = request.GET.get("reason")
    product = request.GET.get("product")
    ct = flagged.content_type

    if new_status:
        # If the object is an Answer let's fire a notification
        # if the flag is invalid
        if str(new_status) == str(FlaggedObject.FLAG_REJECTED) and ct.model_class() == Answer:
            answer = flagged.content_object
            QuestionReplyEvent(answer).fire(exclude=[answer.creator])

        flagged.status = new_status
        flagged.save()
    if flagged.reason == FlaggedObject.REASON_CONTENT_MODERATION:
        question = flagged.content_object
        question.moderation_timestamp = timezone.now()
        question.save()
        return HttpResponseRedirect(urlparams(reverse("flagit.moderate_content"), product=product))
    return HttpResponseRedirect(urlparams(reverse("flagit.flagged_queue"), reason=reason))
