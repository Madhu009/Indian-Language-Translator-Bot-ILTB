from Output.output_adapter import OutputAdapter


class OutputToAndroid(OutputAdapter):


    def process_response(self, request, session_id=None):
        """
        Print the response to the user's input.
        """


        return request.text