from __future__ import unicode_literals

from hidden_layer.adapters import Adapter


class InputAdapter(Adapter):
    """
    This is an abstract class that represents the
    interface that all input adapters should implement.
    """

    def covert_to_input_object(self, *args, **kwargs):
        """
        Returns a input object based on the input source.
        """
        raise self.AdapterMethodNotImplementedError()

    def process_input_statement(self, *args, **kwargs):
        """
        Return an existing statement object (if one exists).
        """
        input_object = self.covert_to_input_object(*args, **kwargs)

        self.logger.info('Recieved input statement: {}'.format(input_object.text))

        existing_statement = self.bot.storage.find(input_object.text) #none or known

        if existing_statement:
            self.logger.info('"{}" is a known statement'.format(input_object.text))
            input_object = existing_statement
        else:
            self.logger.info('"{}" is not a known statement'.format(input_object.text))

        return input_object
