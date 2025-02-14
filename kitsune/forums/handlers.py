from django.conf import settings
from django.contrib.auth.models import User

from kitsune.forums.models import Post, Thread
from kitsune.users.handlers import UserDeletionListener


class ThreadListener(UserDeletionListener):
    """Handles thread cleanup when a user is deleted."""

    def on_user_deletion(self, user: User) -> None:

        sumo_bot = User.objects.get(username=settings.SUMO_BOT_USERNAME)
        Thread.objects.filter(creator=user).update(creator=sumo_bot)


class PostListener(UserDeletionListener):
    """Handles post cleanup when a user is deleted."""

    def on_user_deletion(self, user: User) -> None:

        sumo_bot = User.objects.get(username=settings.SUMO_BOT_USERNAME)
        posts = Post.objects.filter(creator=user)

        posts.filter(
            id__in=FlaggedObject.objects.filter(
                content_type__model="post",
                object_id__in=posts.values_list("id", flat=True),
            ).values_list("object_id", flat=True)
        ).delete()

        posts.update(creator=sumo_bot)
