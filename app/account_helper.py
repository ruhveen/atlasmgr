from json_helper import JsonHelper


class AccountHelper():
    @classmethod
    def get_account_object(cls, account_id):
        return {"id": account_id}

    @classmethod
    def get_account_json(cls, account_id):
        return JsonHelper.to_json(cls.get_account_object(account_id))
