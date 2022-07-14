from article_tgbot.src.model.data_layer import DataLayer


def is_admin(user_id):
    dl = DataLayer()
    return dl.is_user_admin(user_id)
