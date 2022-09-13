class UserGroup(object):
    ADMIN = False
    CAN_COMMENT = False
    CAN_POST = False


class Reader(UserGroup):
    CAN_COMMENT = True


class Author(UserGroup):
    CAN_COMMENT = True
    CAN_POST = True


class Admin(UserGroup):
    ADMIN = True
    CAN_COMMENT = True
    CAN_POST = True


GROUPS = {
    'DEFAULT': UserGroup,
    'READER': Reader,
    'AUTHOR': Author,
    'ADMIN': Admin
}


class User:
    id: int = None
    username: str = None

    permissions: UserGroup = UserGroup()

    def __init__(self, db_obj):
        self.id = db_obj['id']
        self.username = db_obj['username']

        self.permissions = GROUPS[db_obj['group']]
