class AuthenticationService:

    def __init__(self, users):
        self.users = users
        self.current_user = None

    def login(self, username, password):
        if not username or not password:
            return None

        for user in self.users:
            if (
                user["username"] == username
                and user["password"] == password
            ):
                self.current_user = user
                return user

        self.current_user = None
        return None

    def logout(self):
        self.current_user = None