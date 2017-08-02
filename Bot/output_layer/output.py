from output_layer import OutputAdapter


class Output(OutputAdapter):


    def convert_to_output_object(self, request, session_id=None):
        """
               Reads the response text and converts to an object.
               """
        output_obj=OutputObject(request.text)
        return output_obj




class OutputObject(object):

    def __init__(self, text, **kwargs):
        self.text = text
        self.occurrence = kwargs.get('occurrence', 1)

    def __str__(self):
        return self.text

    def __repr__(self):
        return '<Response text:%s>' % (self.text)

    def __hash__(self):
        return hash(self.text)

    def __eq__(self, other):
        if not other:
            return False

        if isinstance(other, OutputObject):
            return self.text == other.text

        return self.text == other

    def serialize(self):
        data = {}

        data['text'] = self.text
        data['occurrence'] = self.occurrence

        return data
