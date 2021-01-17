import unittest
import sqlite3
import os
from fitness_tracker.signup.signup_helpers import create_user, create_user_info_after_signup, create_user_table
from signup_test_helpers import *

class TestSignup(unittest.TestCase):
  def setUp(self):
    create_test_user("test.db")

  def tearDown(self):
    delete_test_user()
    os.remove("test.db")

  def test_create_user(self):
    name_and_password = fetch_name_and_password()
    self.assertEqual(tuple([test_user["email"], test_user["password"]]), name_and_password)

  def test_create_user_table(self):
    table_columns = fetch_test_table_columns()
    table_data = fetch_test_table_data()[0:2]

    self.assertEqual(table_columns, tuple(test_user.keys()))
    self.assertEqual(table_data, tuple([test_user["email"], test_user["password"]]))
    
  def test_create_user_info_after_signup(self):
    os.remove("test.db")
    create_user_table(test_user["email"], "testpassword123", "test.db")
    user_info = {key: value for key, value in test_user.items() if not key  == "email" and not key == "password"}
    create_user_info_after_signup(test_user, test_user["email"], "test.db")
    fetch_info = fetch_user_info()[0][:-1]
    self.assertEqual(fetch_info, tuple(test_user.values()))

if __name__ == "__main__":
  unittest.main()