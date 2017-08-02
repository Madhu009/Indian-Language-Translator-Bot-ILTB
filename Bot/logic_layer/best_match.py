from logic_layer.logic_adapter import LogicAdapter


class BestMatch(LogicAdapter):
    """
    A logic adater that returns a response based on known responses to
    the closest matches to the input statement.
    """

    def get(self,input_object):
        """
        Takes a statement string and a list of statement strings.
        Returns the closest matching statement from the list.
        """
        statement_list = self.bot.storage.get_response_statements()

        if not statement_list:
            if self.bot.storage.count():
                # Use a randomly picked statement
                self.logger.info(
                    'No statements have known responses. ' +
                    'Choosing a random response to return.'
                )
                random_response = self.bot.storage.get_random()
                random_response.confidence = 0
                return random_response
            else:
                raise self.EmptyDatasetException()

        closest_match=input_object
        closest_match.confidence=0

        for statement in statement_list:
            confidence=self.compare_statements(input_object,statement)

            if confidence>closest_match.confidence:
                closest_match=statement
                closest_match.confidence=confidence

        return closest_match


    def can_process(self, statement):
        """
        Check that the chatbot's storage adapter is available to the logic
        adapter and there is at least one statement in the database.
        """
        return self.bot.storage.count()

    def process(self, input_object):

        closest_match=self.get(input_object)
        self.logger.info('Using "{}" as a close match to "{}"'.format(
            input_object.text, closest_match.text
        ))

        # Get all statements that are in response to the closest match
        response_list = self.bot.storage.filter(
            in_response_to__contains=closest_match.text
        )

        if response_list:
            self.logger.info(
                'Selecting response from {} optimal responses.'.format(
                    len(response_list)
                )
            )

            response=self.select_response(input_object,response_list)
            response.confidence = closest_match.confidence
            self.logger.info('Response selected. Using "{}"'.format(response.text))

        else:
            response = self.bot.storage.get_random()
            self.logger.info(
                'No response to "{}" found. Selecting a random response.'.format(
                    closest_match.text
                )
            )

            # Set confidence to zero because a random response is selected
            response.confidence = 0

        return response




