from Conversation import Request
from Input import InputAdapter


class InputFromAndroid(InputAdapter):
    """
        A simple adapter that allows Bot to
        communicate through the terminal.
        """

    def process_input(self, text):
        """
        Read the user's input from android.
        """
        request=Request(text)
        return request
