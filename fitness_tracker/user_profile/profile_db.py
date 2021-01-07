import os
import sys
import psycopg2
from psycopg2 import sql
import sqlite3
from common.units_conversion import kg_to_pounds, pounds_to_kg

path = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.sep.join([*path.split(os.path.sep)[:-2], "db", "profile.db"])

db_info = {"host": "fitnesstracker.cc7s2r4sjjv6.eu-west-3.rds.amazonaws.com", "port": 5432,
           "database": "postgres", "user": "admin", "password": "admin"}

def fetch_table_name(path=db_path):
  with sqlite3.connect(path) as conn:
    cursor = conn.cursor()
    get_table_name = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    cursor.execute(get_table_name)
    return cursor.fetchone()[0]

def fetch_local_user_data():
  table_name = fetch_table_name()
  with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    get_user_data = "SELECT * FROM '{table}'"
    cursor.execute(get_user_data.format(table=table_name))
    return cursor.fetchone()[2:]

def fetch_units(path=db_path):
  table_name = fetch_table_name(path)
  with sqlite3.connect(path) as conn:
    cursor = conn.cursor()
    fetch_current_units = "SELECT units FROM '{table}'"
    cursor.execute(fetch_current_units.format(table=table_name))
    return cursor.fetchone()[0]

def fetch_email(path=db_path):
  table_name = fetch_table_name(path)
  with sqlite3.connect(path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM '{table}'".format(table=table_name))
    return cursor.fetchone()[0]

def fetch_user_weight():
  table_name = fetch_table_name()
  with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT weight FROM '{table}'".format(table=table_name))
    return cursor.fetchone()[0]

def fetch_age():
  table_name = fetch_table_name()
  with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT age FROM '{table}'".format(table=table_name))
    return cursor.fetchone()[0]

def fetch_gender():
  table_name = fetch_table_name()
  with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT gender FROM '{table}'".format(table=table_name))
    return cursor.fetchone()[0]

def fetch_height():
  table_name = fetch_table_name()
  with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT height FROM '{table}'".format(table=table_name))
    return cursor.fetchone()[0]

def fetch_goal_weight():
  table_name = fetch_table_name()
  with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT goalweight FROM '{table}'".format(table=table_name))
    return cursor.fetchone()[0]

def fetch_goal_params():
  table_name = fetch_table_name()
  with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT goalparams FROM '{table}'".format(table=table_name))
    return cursor.fetchone()[0]

def fetch_goal():
  table_name = fetch_table_name()
  with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT goal FROM '{table}'".format(table=table_name))
    return cursor.fetchone()[0]

def set_weight(user_data):
  # 4th column of user table is currently weight
  weight = user_data[4]
  if "metric" in user_data: return " ".join([str(weight), "kg"])
  elif "imperial" in user_data: return " ".join([str(weight), "lb"])
  
def convert_weight(current_units, weight):
  if current_units == "metric":
    return kg_to_pounds(float(weight))
  elif current_units == "imperial":
    return pounds_to_kg(float(weight))

def update_weight(weight):
  email = fetch_email()
  table_name = fetch_table_name()
  with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    update = "UPDATE '{table}' SET weight='%s'" % str(weight)
    cursor.execute(update.format(table=table_name))
  
  with psycopg2.connect(host=db_info["host"], port=db_info["port"], database=db_info["database"],
                        user=db_info["user"], password=db_info["password"]) as conn:
    with conn.cursor() as cursor:
      update = "UPDATE users SET weight=%s WHERE email='%s'" % (weight, email)
      cursor.execute(sql.SQL(update).format(table=sql.Identifier(table_name)))

def update_goal(goal):
  email = fetch_email()
  table_name = fetch_table_name()
  with psycopg2.connect(host=db_info["host"], port=db_info["port"], database=db_info["database"],
                        user=db_info["user"], password=db_info["password"]) as conn:
    with conn.cursor() as cursor:
      update = "UPDATE users SET goal='%s' WHERE email='%s'" % (goal, email)
      cursor.execute(update)

  with sqlite3.connect(db_path) as conn: 
    cursor = conn.cursor()
    update = "UPDATE '{table}' SET goal='%s'" % goal
    cursor.execute(update.format(table=table_name))

def update_goal_parameters(goal_params):
  email = fetch_email()
  table_name = fetch_table_name()
  with psycopg2.connect(host=db_info["host"], port=db_info["port"], database=db_info["database"],
                        user=db_info["user"], password=db_info["password"]) as conn:
    with conn.cursor() as cursor:
      update = "UPDATE users SET goalparams='%s' WHERE email='%s'" % (goal_params, email)
      cursor.execute(update)

  with sqlite3.connect(db_path) as conn: 
    cursor = conn.cursor()
    update = "UPDATE '{table}' SET goalparams='%s'" % goal_params
    cursor.execute(update.format(table=table_name))

def update_goal_weight(goal_weight):
  email = fetch_email()
  table_name = fetch_table_name()
  with psycopg2.connect(host=db_info["host"], port=db_info["port"], database=db_info["database"],
                        user=db_info["user"], password=db_info["password"]) as conn:
    with conn.cursor() as cursor:
      update = "UPDATE users SET goalweight='%s' WHERE email='%s'" % (goal_weight, email)
      cursor.execute(update)

  with sqlite3.connect(db_path) as conn: 
    cursor = conn.cursor()
    update = "UPDATE '{table}' SET goalweight='%s'" % goal_weight
    cursor.execute(update.format(table=table_name))

def update_calorie_goal(calorie_goal):
  email = fetch_email()
  table_name = fetch_table_name()
  with psycopg2.connect(host=db_info["host"], port=db_info["port"], database=db_info["database"],
                        user=db_info["user"], password=db_info["password"]) as conn:
    with conn.cursor() as cursor:
      update = "UPDATE nutrition SET calorie_goal='%s' WHERE email='%s'" % (calorie_goal, email)
      cursor.execute(update)

  with sqlite3.connect(db_path) as conn: 
    cursor = conn.cursor()
    update = "UPDATE nutrition SET calorie_goal='%s'" % calorie_goal
    cursor.execute()

def update_units():
  email = fetch_email()
  table_name = fetch_table_name()
  current_units = None
  with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor() 
    set_units_imperial = "UPDATE '{table}' SET units='imperial'"
    set_units_metric = "UPDATE '{table}' SET units='metric'"
    fetch_current_units = "SELECT units FROM '{table}'"
    cursor.execute(fetch_current_units.format(table=table_name))
    current_units = cursor.fetchone()[0]
    update_units = set_units_imperial if current_units == "metric" else set_units_metric
    cursor.execute(update_units.format(table=table_name))
 
  with psycopg2.connect(host=db_info["host"], port=db_info["port"], database=db_info["database"],
                        user=db_info["user"], password=db_info["password"]) as conn:
    with conn.cursor() as cursor:
      set_units_imperial = "UPDATE users SET units='imperial' WHERE email=%s"
      set_units_metric = "UPDATE users SET units='metric' WHERE email=%s"
      update_units = set_units_imperial if current_units == "metric" else set_units_metric
      cursor.execute(update_units, (email,))