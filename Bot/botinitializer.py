
from Input import InputAdapter

from Output.output_adapter import OutputAdapter
from Storage.storage_adapter import StorageAdapter
from Util.utils import nltk_download_corpus
from Util import utils
import logging

class BotInitializer(object):
    """
        A conversational dialog bot.
        """
    def __init__(self,name,**kwargs):
        from Conversation.session import ConversationSessionManager
        from Logic.multi_adapter import MultiLogicAdapter
        self.name=name
        kwargs['name']=name

        #set the all adapters

        #setting the storage (Mongo DB)
        storage_adapter=kwargs.get('storage_adapter','Storage.MongoDatabase')

        #setting input (Android ,FB Bot and etc...)
        input_adapter=kwargs.get('input_adapter','Input.InputFromAndroid')

        #setting the output (Android ,FB Bot and etc...)
        output_adapter = kwargs.get('output_adapter', 'Output.OutputToAndroid')

        #Setting the matching algorithm
        logic_adapters = kwargs.get('logic_adapters', [
            'Logic.BestMatch'
        ]) #has to be changed

        #check the object type same or not
        utils.validate_adapter_class(storage_adapter, StorageAdapter) # storage = MongoDatabase()
        utils.validate_adapter_class(input_adapter, InputAdapter)
        utils.validate_adapter_class(output_adapter, OutputAdapter)

        #importing the modules and storing classes
        self.storage = utils.initialize_class(storage_adapter, **kwargs)
        self.input = utils.initialize_class(input_adapter, **kwargs)
        self.output = utils.initialize_class(output_adapter, **kwargs)
        self.logic = MultiLogicAdapter(**kwargs)

        filters = kwargs.get('filters', tuple())

        self.filters = tuple([utils.import_module(F)() for F in filters])

        # Add required system logic adapter
        self.logic.system_adapters.append(
            utils.initialize_class('Logic.NoKnowledgeAdapter', **kwargs)
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
                'preprocessors.clean_whitespace'
            ])
        self.preprocessors = []
        for preprocessor in preprocessors:
            self.preprocessors.append(utils.import_module(preprocessor))

        # Use specified trainer or fall back to the default
        trainer = kwargs.get('trainer', 'trainers.Trainer')
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
                :rtype: Statement
                """
        if not session_id:
            session_id=str(self.default_session.uuid)

        input_request= self.input.process_input_statement(input_text)

        # Preprocess the input statement
        for preprocessor in self.preprocessors:
            input_request = preprocessor(self, input_request)

        request,response=self.generate_response(input_request,session_id)

        self.conversation_sessions.update(session_id, (request, response,))

        return self.output.process_response(response, session_id)

    def generate_response(self, input_request, session_id):
        """
               Return a response based on a given input statement.
               """
        self.storage.generate_base_query(self, session_id)

        response = self.logic.process(input_request)
        return input_request,response

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

