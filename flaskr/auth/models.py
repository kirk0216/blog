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
