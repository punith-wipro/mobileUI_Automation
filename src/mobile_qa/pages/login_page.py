"""Login screen behaviour."""

from mobile_qa.pages.base_page import BasePage


class LoginPage(BasePage):
    def is_open(self) -> bool:
        return self.exists("username") and self.exists("password")

    def sign_in(self, username: str, password: str) -> None:
        self.enter_text("username", username)
        self.enter_text("password", password)
        self.tap("login_button")

    def has_error(self) -> bool:
        return self.exists("login_error", timeout=5)
