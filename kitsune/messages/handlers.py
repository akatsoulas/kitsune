from django.contrib.auth.models import User

from kitsune.users.handlers import UserDeletionListener


class MessageListener(UserDeletionListener):
    """Handles message cleanup when a user is deleted."""

    def on_user_deletion(self, user: User) -> None:
        """
        When a user is deleted:
        - Delete their outbox messages
        - Keep inbox messages for other users
        """
        user.outbox.all().delete()
        user.inbox.all().delete()
