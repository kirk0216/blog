GROUPS = {
    'DEFAULT': [],
    'READER': ['CAN_COMMENT'],
    'AUTHOR': ['CAN_COMMENT', 'CAN_POST'],
    'ADMIN': ['CAN_COMMENT', 'CAN_POST', 'ADMIN']
}


class User:
    id: int = None
    username: str = None

    permissions: list[str] = None

    def __init__(self, db_obj):
        self.id = db_obj['id']
        self.username = db_obj['username']

        self.permissions = GROUPS[db_obj['group']]
