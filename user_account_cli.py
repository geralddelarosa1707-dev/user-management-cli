from logger import logger
import json
import hashlib

menu = {
  "CREATE": "Create Account",
  "LOGIN": "Login",
  "CHANGE_USERNAME": "Change Username",
  "CHANGE_PASSWORD": "Change Password",
  "VIEW": "View Profile",
  "LOGOUT": "Logout",
  "DELETE": "Delete Account"
}

def show_menu(menu):
  print("\n----------MENU----------")
  for key, info in menu.items():
    print(f"{key}: {info}")
  print("------------------------")
  
def validate_password(password):
  if not password:
    return False, "\nPlease enter a password."
  elif len(password) < 8:
    return False, "\nPassword must be at least 8 characters."
  elif not any(char.isalpha() for char in password):
    return False, "\nPassword must contain at least one letter."
  elif not any(char.isdigit() for char in password):
    return False, "\nPassword must contain at least one digit."
  elif not any(not char.isalnum() for char in password):
    return False, "\nPassword must contain at least one special character."
    
  return True, None
  
def hash_password(password):
  return hashlib.sha256(password.encode()).hexdigest()
  
class User:
  def __init__(self, name, password, email, age):
    self.name = name
    self.password = password
    self.email = email
    self.age = age
    
  def check_password(self, user_password):
    return self.password == hash_password(user_password)
    
  def display_info(self):
    return (
      f"\nUsername: '{self.name}'"
      f"\nEmail: '{self.email}'"
      f"\nAge: '{self.age}'"
      )
      
  def to_dict(self):
    return {
      "name": self.name,
      "password": self.password,
      "email": self.email,
      "age": self.age
    }
  
class Session:
  def __init__(self):
    self.current_user = None
  
class UserManager:
  def __init__(self):
    self.users = {}
    
  def does_username_exist(self, username):
    return username in self.users
    
  def create_user(self, username, password, email, age):
    username_exist = self.does_username_exist(username)
        
    if username_exist:
      return False, None, "USERNAME_ALREADY_EXIST", "\nUsername already exist. Try another one."
      
    is_password_valid, error = validate_password(password)
      
    if not is_password_valid:
      return False, None, None, error
      
    hashed_password = hash_password(password)
      
    if "@" not in email or "." not in email.split("@")[-1]:
      return False, None, "INVALID_EMAIL", "\nPlease enter a valid email."
      
    if age < 0:
      return False, None, "INVALID_AGE", "\nAge must be greater than 0."
      
    user = User(username, hashed_password, email, age)
      
    self.users[username] = user
    
    return True, user, None, "\nAccount created successfully!"
    
  def login_user(self, username, password):
    matched_user = self.users.get(username)
            
    if matched_user is None:
      return False, None, "INVALID_CREDENTIALS", "\nInvalid username or password."
        
    if not matched_user.check_password(password):
      return False, None, "INVALID_CREDENTIALS", "\nInvalid username or password."
    
    return True, matched_user, None, "\nLog-in successfully!"
    
  def change_username(self, new_username, app):
    curr_user = app.session.current_user
    
    if curr_user is None:
      return False, None, "NOT_LOGGED_IN", "\nLogin to change username"
      
    if new_username == curr_user.name:
      return False, None, "SAME_USERNAME", "\nNew username cannot be old username."
      
    username_exist = self.does_username_exist(new_username)
        
    if username_exist:
      return False, None, "USERNAME_ALREADY_EXIST", "\nUsername already exist. Try another one."
      
    old_username = curr_user.name
      
    user = self.users.pop(old_username, None)
      
    if user is None:
      return False, None, "USER_NOT_FOUND", "\nUser not found."
      
    curr_user.name = new_username
    self.users[new_username] = user
      
    return True, None, None, "\nUsername changed successfully!"
    
  def change_password(self, old_password, new_password, confirm_new_password, app):
    curr_user = app.session.current_user
    
    if curr_user is None:
      return False, None, "NOT_LOGGED_IN", "\nLogin to change password"
      
    if curr_user.check_password(old_password):
      is_password_valid, error = validate_password(new_password)
      
      if not is_password_valid:
        return False, None, "PASSWORD_NOT_VALID", error
        
      new_hashed = hash_password(new_password)
        
      if new_hashed == curr_user.password:
        return False, None, "SAME_PASSWORD", "\nNew password cannot be old password."
          
      if new_password == confirm_new_password:
        
        return True, new_hashed, None, "\nPassword changed successfully!"
        
      else:
        return False, None, "PASSWORD_NOT_MATCHED", "\nPasswords do not match."
    else:
      return False, None, "INCORRECT_PASSWORD", "\nOld password is incorrect."
      
  def logout(self, confirm, app):
    if app.session.current_user is None:
      return False, None, "NOT_LOGGED_IN", "\nNo account signed in yet."
      
    if confirm != "y":
      return False, None, "LOGOUT_CANCELLED", "\nLogout cancelled."
      
    app.session.current_user = None
    
    return True, None, None, "\nLogout successfully!"
    
  def delete_user(self, password, confirm, app):
    curr_user = app.session.current_user
    
    if curr_user is None:
      return False, None, "NOT_LOGGED_IN", "\nNo account signed in."
    
    is_password_correct = curr_user.check_password(password)
    
    if not is_password_correct:
      return False, None, "INCORRECT_PASSWORD", "\nIncorrect password."
    
    if confirm != "y":
      return False, None, "DELETING_CANCELLED", "\nDeleting cancelled."
      
    username = app.session.current_user.name
      
    return True, username, None, "\nAccount deleted successfully!"
    
class App:
  def __init__(self):
    self.session = Session()
    self.user_manager = UserManager()
    
app = App()
  
def load_from_file(app):
  try:
    with open("users.json", "r") as file:
      data = json.load(file)
      
      if not isinstance(data, dict):
        logger.error("INVALID_FILE_FORMAT")
        print("\nWarning: Invalid file format.")
        return
      
      app.user_manager.users = {}
      
      for username, info in data.get("personal_info", {}).items():
        if not isinstance(info, dict):
          continue
        
        user = User(
          info["name"],
          info["password"],
          info["email"],
          info["age"]
          )
        app.user_manager.users[username] = user
        
      current_username = data.get("current_user")
      
      app.session.current_user = app.user_manager.users.get(current_username)
      
  except FileNotFoundError:
    pass
    
  except json.JSONDecodeError:
    logger.error("FILE_CORRUPTED")
    print("\nWarning: File corrupted. Resetting data.")
  
def save_to_file(app):
  with open("users.json", "w") as file:
    users_dict = {
      username: user.to_dict() for username, user in app.user_manager.users.items()
    }
    
    data = {
      "current_user": app.session.current_user.name if app.session.current_user else None,
      "personal_info": users_dict
    }
    
    json.dump(data, file, indent=4)

def open_program(app):
  while True:
    show_menu(menu)
    
    option = input("\nWhat would you like to do: ").strip().upper()
    
    if option == "CREATE":
      username = input("\nEnter Username: ")
      
      if not username:
        print("\nPlease enter a username.")
        continue
      
      password = input("\nEnter Password (8 Characters): ").strip()
      
      confirm_password = input("\nConfirm password: ").strip()
      
      if not confirm_password:
        print("\nPlease confirm the password.")
        continue
      
      if password != confirm_password:
        print("\nPasswords do not match.")
        continue
      
      email = input("\nEnter Email: ").strip()
      
      if not email:
        print("\nPlease enter email.")
        continue
      
      try:
        age = int(input("\nEnter Age: "))
      except ValueError:
        logger.warning(f"INVALID_AGE | USER={username}")
        print("\nPlease enter only a number.")
        continue
      
      success, user, reason, message = app.user_manager.create_user(username, password, email, age)
      
      if not success:
        logger.warning(f"ACCOUNT_CREATE_FAILED | USER={username} | REASON={reason}")
        print(message)
        continue
      
      logger.info(f"ACCOUNT_CREATE_SUCCESS | USER={username}")
      print(message)
      print(user.display_info())
      
      save_to_file(app)
      
      input("\nPress Enter to continue...")
      
    elif option == "LOGIN":
      attempts = 3
      
      while attempts > 0:
        username = input("\nEnter Username: ")
      
        if not username:
          print("\nPlease enter a username.")
          attempts -= 1
          print(f"\nAttempts remaining: {attempts}")
          continue
      
        password = input("\nEnter Password: ")
      
        if not password:
          print("\nPlease enter a password.")
          attempts -= 1
          print(f"\nAttempts remaining: {attempts}")
          continue
      
        success, user, reason, message = app.user_manager.login_user(username, password)
        
        if not success:
          attempts -= 1
          logger.warning(f"LOGIN_FAILED | USER={username} | REASON={reason}")
          print(message)
          print(f"\nAttempts remaining: {attempts}")
          continue
          
        else:
          app.session.current_user = user
          logger.info(f"LOGIN_SUCCESS | USER={username}")
          print(message)
          print(user.display_info())
          save_to_file(app)
          break
      
      if attempts == 0:
        print("\nToo many attempts, please try again later.")
      
      input("\nPress Enter to continue...")
      
    elif option == "CHANGE_USERNAME":
      curr_user = app.session.current_user
      users_info = app.user_manager
      
      if curr_user is None:
        print("\nLogin to change username")
        continue
      
      new_username = input("\nEnter new Username: ")
      
      if not new_username:
        print("\nPlease enter a username")
        continue
      
      success, _, reason, message = users_info.change_username(new_username, app)
      
      user = curr_user.name if curr_user else "UNKNOWN"
      
      if not success:
        logger.warning(f"CHANGE_USERNAME_FAILED | USER={user} | REASON={reason}")
        print(message)
        continue
      
      logger.info(f"CHANGE_USERNAME_SUCCESS | USER={new_username}")
      print(message)
      save_to_file(app)
      
      input("\nPress Enter to continue...")
      
    elif option == "CHANGE_PASSWORD":
      curr_user = app.session.current_user
    
      if curr_user is None:
        print("\nLogin to change password.")
        continue
      
      old_password = input("\nEnter old password: ")
      
      if not old_password:
        print("\nPlease enter a password.")
        continue
      
      new_password = input("\nEnter new password: ")
      
      if not new_password:
        print("\nPlease enter a password.")
        continue
      
      confirm_new_password = input("\nConfirm new password: ")
      
      if not confirm_new_password:
        print("\nPlease enter a password.")
        continue
      
      success, changed_password, reason, message = app.user_manager.change_password(
        old_password,
        new_password,
        confirm_new_password, 
        app
        )
      
      if not success:
        logger.warning(f"CHANGE_PASSWORD_FAILED | USER={curr_user.name} | REASON={reason}")
        print(message)
        continue
      
      app.session.current_user.password = changed_password
        
      logger.info(f"CHANGE_PASSWORD_SUCCESS | USER={curr_user.name}")
      save_to_file(app)
      
      input("\nPress Enter to continue...")
        
    elif option == "VIEW":
      if app.session.current_user is None:
        print("\nLogin to see profile.")
        continue
      
      print(app.session.current_user.display_info())
      
      input("\nPress Enter to continue...")
      
    elif option == "LOGOUT":
      curr_user = app.session.current_user
      
      if curr_user is None:
        print("\nNo account signed in.")
        continue
      
      confirm = input("\nLogout of your account (y/n): ").strip().lower()
      
      success, _, reason, message = app.user_manager.logout(confirm, app)
      
      if not success:
        logger.warning(f"LOGOUT_FAILED | USER={curr_user.name} | REASON={reason}")
        print(message)
        continue
      
      logger.info(f"LOGOUT_SUCCESS | USER={curr_user.name}")
      print(message)
      save_to_file(app)
      
      input("\nPress Enter to continue...")
      
    elif option == "DELETE":
      curr_user = app.session.current_user
      
      if curr_user is None:
        print("\nNo account signed in.")
        continue
      
      password = input("\nEnter password: ").strip()
      
      confirm = input("\nAre you sure you want to delete the account (y/n): ").strip().lower()
      
      success, username, reason, message = app.user_manager.delete_user(password, confirm, app)
      
      if not success:
        logger.warning(f"DELETE_ACCOUNT_FAILED | USER={curr_user.name} | REASON={reason}")
        print(message)
        continue
      
      logger.info(f"DELETE_ACCOUNT_SUCCESS | USER={curr_user.name}")
      print(message)
      app.user_manager.users.pop(username, None)
      app.session.current_user = None
      
      save_to_file(app)
      
    else:
      print("\nPlease enter a valid option.")
      
if __name__ == "__main__":
  load_from_file(app)
  open_program(app)