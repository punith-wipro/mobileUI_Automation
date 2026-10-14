"""Login screen behaviour."""

from mobile_qa.pages.base_page import BasePage


class LoginPage(BasePage):
    def is_open(self, timeout: int = 3) -> bool:
        return self.exists("username", timeout=timeout) and self.exists("password", timeout=timeout)

    def sign_in(self, username: str, password: str) -> None:
        self.enter_text("username", username)
        self.enter_text("password", password)
        self.tap("login_button")

    def has_error(self) -> bool:
        return self.exists("login_error", timeout=5)
