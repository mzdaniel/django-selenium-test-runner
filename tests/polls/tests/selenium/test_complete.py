from selenium import selenium
import unittest, time, re

class test_complete(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_test_complete(self):
        sel = self.selenium
        sel.open("admin/logout/")
        sel.open("admin/")
        sel.type("id_username", "admin")
        sel.type("id_password", "test")
        sel.click("//input[@value='Log in']")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Site administration"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.open("admin/polls/poll/")
        try: self.failUnless(sel.is_text_present("What's up?"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=exact:What's up?")
        time.sleep(1)
        try: self.assertEqual("Not much", sel.get_value("id_choice_set-0-choice"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.type("id_pub_date_0", "2009-10-19")
        sel.click("_save")
        time.sleep(1)
        try: self.assertEqual("Oct. 19, 2009, 3:40 p.m.", sel.get_table("//div[@id='changelist']/form/table.1.2"))
        except AssertionError, e: self.verificationErrors.append(str(e))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
