from django.conf import settings
from django.contrib.auth.models import Group, User

from kitsune.sumo.anonymous import AnonymousIdentity
from kitsune.users.handlers import UserDeletionListener
from kitsune.users.models import Profile
from kitsune.wiki.models import Document, HelpfulVote, Revision


class DocumentListener(UserDeletionListener):
    """Listener for document-related tasks."""

    def on_user_deletion(self, user: User) -> None:
        """Handle the deletion of a user."""

        documents = Document.objects.filter(contributors=user)
        content_group = Group.objects.get(name=settings.SUMO_CONTENT_GROUP)
        for document in documents:
            if not document.contributors.exclude(id=user.id).exists():
                document.contributors.add(*content_group.user_set.all())
            document.contributors.remove(user)

        non_approved_revisions = Revision.objects.filter(creator=user, is_approved=False)

        docs_to_delete = Document.objects.filter(
            current_revision__isnull=True,
            revisions__creator=user,
        ).exclude(revisions__is_approved=True)

        docs_to_delete.delete()
        non_approved_revisions.delete()

        sumo_bot = Profile.get_sumo_bot()
        Revision.objects.filter(creator=user).update(creator=sumo_bot)
        Revision.objects.filter(reviewer=user).update(reviewer=sumo_bot)
        Revision.objects.filter(readied_for_localization_by=user).update(
            readied_for_localization_by=sumo_bot
        )
        # Anonymize any revision votes.
        HelpfulVote.objects.filter(creator=user).update(
            creator=None, anonymous_id=AnonymousIdentity().anonymous_id
        )
