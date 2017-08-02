from hidden_layer.adapters import Adapter


class OutputAdapter(Adapter):
    """
    A generic class that can be overridden by a subclass to provide extended
    functionality, such as delivering a response to an API endpoint.
    """

    def convert_to_output_object(self, response, session_id=None):

        return response
