from selenium import selenium
import unittest, time, re

class test_simple_login(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()

    def test_test_simple_login(self):
        sel = self.selenium
        sel.open("admin/logout/")
        sel.open("admin/")
        sel.type("id_username", "admin")
        sel.type("id_password", "test")
        sel.click("//input[@value='Log in']")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Site administration"))
        except AssertionError, e: self.verificationErrors.append(str(e))

    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
