class LoginPage:
    def __init__(self, page):
        self.page = page
        self.username_input = "#name"
        self.password_input = "#password"

    def login(self, username, password):
        self.page.locator(self.username_input).fill(username)
        self.page.locator(self.password_input).fill(password)
