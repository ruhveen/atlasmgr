import json

class JsonHelper():

    @classmethod
    def to_json(cls, obj):
        return json.dumps(obj)

    @classmethod
    def build_action_response(cls, obj, message):

        response = {}
        response['result'] = obj
        response['message'] = message

        return cls.to_json(response)