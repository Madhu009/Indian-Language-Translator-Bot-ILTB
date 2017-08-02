from output_layer import OutputObject
from data_layer.storage import StorageAdapter

class MongoDatabase(StorageAdapter):


    def __init__(self, **kwargs):
        super(MongoDatabase, self).__init__(**kwargs)
        from pymongo import MongoClient
        self.i=0
        self.database_name = self.kwargs.get(
            'database', 'botdb'
        )
        #if runs locally
        self.database_uri_local = self.kwargs.get(
            'database_uri_local', 'mongodb://localhost:27017/'
        )
        self.database_uri = self.kwargs.get(
            'database_uri', 'mongodb://iltbot:iltbot@ds149132.mlab.com:49132/botdb'
        )

        # Use the default host and port
        self.client = MongoClient(self.database_uri_local)

        # Specify the name of the database
        self.database = self.client[self.database_name]

        # The mongo collection of statement documents
        self.collections = self.database['collections']

        # Set a requirement for the text attribute to be unique
        self.collections.create_index('text', unique=True)

        self.base_query = Query()

    def count(self):
        return self.collections.count()

    def find(self, statement_text):
        query = self.base_query.statement_text_equals(statement_text)

        #checking if the text is present in the DB
        values = self.collections.find_one(query.value())

        if not values:
            return None

        del values['text']

        # Build the objects for the response list
        values['in_translate_to'] = self.deserialize_responses(
            values.get('in_translate_to', [])
        )

        return self.Statement(statement_text, **values)

    def deserialize_responses(self, response_list):
        """
        Takes the list of response items and returns
        the list converted to Response objects.
        """
        proxy_statement = self.Statement('')

        for response in response_list:
            text = response['text']
            del response['text']

            proxy_statement.add_response(
                OutputObject (text, **response)
            )

        return proxy_statement.in_translate_to

    def mongo_to_object(self, statement_data):
        """
        Return Statement object when given data
        returned from Mongo DB.
        """
        statement_text = statement_data['text']
        del statement_data['text']

        statement_data['in_translate_to'] = self.deserialize_responses(
            statement_data.get('in_translate_to', [])
        )

        return self.Statement(statement_text, **statement_data)

    def mongo_to_object_match(self, statement_data):
        """
        Return Statement object when given data
        returned from Mongo DB.
        """
        statement_text = statement_data['text']
        del statement_data['text']

        statement_data['in_translate_to'] = self.deserialize_responses(
            statement_data.get('in_translate_to', [])
        )
        #if statement_data['image'] and not statement_data['image'].isspace():
            #statement_img = statement_data['image']
            #print(statement_img)

        return self.Statement(statement_text, **statement_data)

    def filter(self, **kwargs):
        """
        Returns a list of statements in the database
        that match the parameters specified.
        """
        import pymongo

        query = self.base_query

        order_by = kwargs.pop('order_by', None)



        # Convert Response objects to data
        if 'in_translate_to' in kwargs:
            serialized_responses = []
            for response in kwargs['in_translate_to']:
                serialized_responses.append({'text': response})

            query = query.statement_response_list_equals(serialized_responses)
            del kwargs['in_translate_to']

        if 'in_response_to__contains' in kwargs:
            query = query.statement_response_list_contains(
                kwargs['in_response_to__contains']
            )
            del kwargs['in_response_to__contains']

        query = query.raw(kwargs)
        #print(query.value())
        matches = self.collections.find(query.value())

        if order_by:

            direction = pymongo.ASCENDING

            # Sort so that newer datetimes appear first
            if order_by == 'created_at':
                direction = pymongo.DESCENDING

            matches = matches.sort(order_by, direction)

        results = []

        for match in list(matches):
            #print(match)
            results.append(self.mongo_to_object_match(match))

        return results

    def update(self, statement):
        from pymongo import UpdateOne
        from pymongo.errors import BulkWriteError

        data = statement.serialize()

        operations = []

        update_operation = UpdateOne(
            {'text': statement.text},
            {'$set': data},
            upsert=True
        )
        operations.append(update_operation)

        # Make sure that an entry for each response is saved
        for response_dict in data.get('in_translate_to', []):
            response_text = response_dict.get('text')

            # $setOnInsert does nothing if the document is not created
            update_operation = UpdateOne(
                {'text': response_text},
                {'$set': response_dict},
                upsert=True
            )
            operations.append(update_operation)

        try:
            self.collections.bulk_write(operations, ordered=False)
        except BulkWriteError as bwe:
            # Log the details of a bulk write error
            self.logger.error(str(bwe.details))

        return statement

    def get_random(self):
        """
        Returns a random statement from the database
        """
        from random import randint

        count = self.count()

        if count < 1:
            raise self.EmptyDatabaseException()

        random_integer = randint(0, count - 1)

        statements = self.collections.find().limit(1).skip(random_integer)

        return self.mongo_to_object(list(statements)[0])

    def remove(self, statement_text):
        """
        Removes the statement that matches the input text.
        Removes any responses from statements if the response text matches the
        input text.
        """
        for statement in self.filter(in_response_to__contains=statement_text):
            statement.remove_response(statement_text)
            self.update(statement)

        self.collections.delete_one({'text': statement_text})

    def get_response_statements(self):
        """
        Return only statements that are in response to another statement.
        A statement must exist which lists the closest matching statement in the
        in_response_to field. Otherwise, the logic adapter may find a closest
        matching statement that does not have a known response.
        """
        response_query = self.collections.distinct('in_translate_to.text')

        #you get only values
        _statement_query = {
            'text': {
                '$in': response_query
            }
        }


        _statement_query.update(self.base_query.value())

        statement_query = self.collections.find(_statement_query)
        #you get the whole text

        statement_objects = []

        for statement in list(statement_query):
            statement_objects.append(self.mongo_to_object(statement))

        return statement_objects

    def drop(self):
        """
        Remove the database.
        """
        self.client.drop_database(self.database_name)



class Query(object):

    def __init__(self, query={}):
        self.query = query

    def value(self):
        return self.query.copy()

    def raw(self, data):
        query = self.query.copy()

        query.update(data)

        return Query(query)

    def statement_text_equals(self, statement_text):
        query = self.query.copy()
        query['text'] = statement_text
        return Query(query)

    def statement_text_not_in(self, statements):
        query = self.query.copy()

        if 'text' not in query:
            query['text'] = {}

        if '$nin' not in query['text']:
            query['text']['$nin'] = []

        query['text']['$nin'].extend(statements)

        return Query(query)

    def statement_response_list_contains(self, statement_text):
        query = self.query.copy()

        if 'in_translate_to' not in query:
            query['in_translate_to'] = {}

        if '$elemMatch' not in query['in_translate_to']:
            query['in_translate_to']['$elemMatch'] = {}

        query['in_translate_to']['$elemMatch']['text'] = statement_text

        return Query(query)

    def statement_response_list_equals(self, response_list):
        query = self.query.copy()

        query['in_translate_to'] = response_list

        return Query(query)

