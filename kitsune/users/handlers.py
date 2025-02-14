from abc import ABC, abstractmethod
from dataclasses import dataclass

from kitsune.forums.handlers import PostListener, ThreadListener
from kitsune.kbforums.handlers import PostListener as KBPostListener
from kitsune.kbforums.handlers import ThreadListener as KBThreadListener
from kitsune.questions.handlers import AAQListener
from kitsune.users.models import User
from kitsune.wiki.handlers import DocumentListener


class UserDeletionListener(ABC):
    """
    Listener that is responsible for deleting a user.
    """

    @abstractmethod
    def on_user_deletion(self, user: User):
        pass


@dataclass
class UserDeletionPublisher:
    """
    Publisher that is responsible for publishing a user deletion event.
    """

    listeners: list[UserDeletionListener]

    def register_listener(self, listener: UserDeletionListener) -> None:
        self.listeners.append(listener)

    def publish(self, user: User):
        for listener in self.listeners:
            listener.on_user_deletion(user)


def delete_user_pipeline(user: User) -> None:
    """
    Deletes a user and all associated data.
    """

    publisher = UserDeletionPublisher()
    publisher.register_listener(ThreadListener())
    publisher.register_listener(PostListener())
    publisher.register_listener(KBThreadListener())
    publisher.register_listener(KBPostListener())
    publisher.register_listener(AAQListener())
    publisher.register_listener(DocumentListener())

    publisher.publish(user)

    # TODO: first check that all publishers have run successfully
    user.delete()
