from input_layer import InputAdapter
from output_layer import OutputAdapter
from data_layer.storage import StorageAdapter

from logic_layer.Util.utils import nltk_download_corpus
from logic_layer.Util import utils
import logging


class BotInitializer(object):


    def __init__(self,name,**kwargs):

        from session_layer.session import ConversationSessionManager
        from logic_layer.multi_adapter import MultiLogicAdapter

        self.name=name
        kwargs['name']=name

        #set the all adapters

        #setting the storage (Mongo DB)
        data_layer_storage=kwargs.get('data_layer_storage','data_layer.storage.MongoDatabase')

        #setting input
        input_layer=kwargs.get('input_layer','input_layer.Input')

        #setting the output (Android ,FB Bot and etc...)
        output_layer = kwargs.get('output_layer', 'output_layer.Output')

        #Setting the matching algorithm
        logic_adapters = kwargs.get('logic_adapters', [
            'logic_layer.NBLogicAdapter',
            'logic_layer.BestMatch'
        ]) #has to be changed

        #check the object type same or not
        utils.validate_adapter_class(data_layer_storage, StorageAdapter) # storage = MongoDatabase()
        utils.validate_adapter_class(input_layer, InputAdapter)
        utils.validate_adapter_class(output_layer, OutputAdapter)

        #importing the modules and storing classes
        self.storage = utils.initialize_class(data_layer_storage, **kwargs)
        self.input = utils.initialize_class(input_layer, **kwargs)
        self.output = utils.initialize_class(output_layer, **kwargs)
        self.logic = MultiLogicAdapter(**kwargs)

        filters = kwargs.get('filters', tuple())

        self.filters = tuple([utils.import_module(F)() for F in filters])

        # Add required system logic adapter
        self.logic.system_adapters.append(
            utils.initialize_class('logic_layer.NoKnowledgeAdapter', **kwargs)
        )

        for adapter in logic_adapters:
            self.logic.add_adapter(adapter, **kwargs)

            # Add the chatbot instance to each adapter to share information such as
            # the name, the current conversation, or other adapters
            self.logic.set_chatbot(self)
            self.input.set_chatbot(self)
            self.output.set_chatbot(self)

        preprocessors = kwargs.get(
            'preprocessors', [
                'hidden_layer.preprocessors.clean_whitespace'
            ])
        self.preprocessors = []
        for preprocessor in preprocessors:
            self.preprocessors.append(utils.import_module(preprocessor))

        # Use specified trainer or fall back to the default
        trainer = kwargs.get('trainer', 'hidden_layer.trainers.Trainer')

        TrainerClass = utils.import_module(trainer)
        self.trainer = TrainerClass(self.storage, **kwargs)

        self.training_data = kwargs.get('training_data')
        self.conversation_sessions = ConversationSessionManager()
        self.default_session = self.conversation_sessions.new()

        self.logger = kwargs.get('logger', logging.getLogger(__name__))

        # Allow the bot to save input it receives so that it can learn
        self.read_only = kwargs.get('read_only', False)

        if kwargs.get('initialize', True):
            self.initialize()
    def initialize(self):
        """
        Do any work that needs to be done before the responses can be returned.
        """
        # Download required NLTK corpora if they have not already been downloaded
        nltk_download_corpus('corpora/stopwords')
        nltk_download_corpus('corpora/wordnet')
        nltk_download_corpus('tokenizers/punkt')
        nltk_download_corpus('sentiment/vader_lexicon')

    def get_response(self,input_text,session_id=None):
        """
        Return the bot's response based on the input.

        :param input_item: An input value.
        :returns: A response to the input.
        :rtype: Output

        """
        if not session_id:
            session_id=str(self.default_session.uuid)

        input_object= self.input.process_input_statement(input_text)

        # Preprocess the input statement
        for preprocessor in self.preprocessors:
            input_object = preprocessor(self, input_object)

        request,response=self.generate_response(input_object,session_id)

        self.conversation_sessions.update(session_id, (request, response,))

        return self.output.convert_to_output_object(response, session_id),response.confidence

    def generate_response(self, input_object, session_id):
        """
        Return a response based on a given input object.
        """
        self.storage.generate_base_query(self, session_id)

        response = self.logic.process(input_object)

        return input_object,response

    def set_trainer(self, training_class, **kwargs):
        """
        Set the module used to train the chatbot.

        :param training_class: The training class to use for the chat bot.
        :type training_class: `Trainer`

        :param \**kwargs: Any parameters that should be passed to the training class.
        """
        self.trainer = training_class(self.storage, **kwargs)

    @property
    def train(self):
        """
        Proxy method to the chat bot's trainer class.
        """
        return self.trainer.train

    @classmethod
    def from_config(cls, config_file_path):
        """
        Create a new ChatBot instance from a JSON config file.
        """
        import json
        with open(config_file_path, 'r') as config_file:
            data = json.load(config_file)

        name = data.pop('name')

        return BotInitializer(name, **data)

