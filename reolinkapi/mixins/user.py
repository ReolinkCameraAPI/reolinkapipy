from typing import Dict


class UserAPIMixin:
    """User-related API calls."""
    def get_online_user(self) -> Dict:
        """
        Return a list of current logged-in users in json format
        See examples/response/GetOnline.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetOnline", "action": 1, "param": {}}]
        return self._execute_command('GetOnline', body)

    def get_users(self) -> Dict:
        """
        Return a list of user accounts from the camera in json format.
        See examples/response/GetUser.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetUser", "action": 1, "param": {}}]
        return self._execute_command('GetUser', body)

    def add_user(self, username: str, password: str, level: str = "guest") -> bool:
        """
        Add a new user account to the camera
        :param username: The user's username
        :param password: The user's password
        :param level: The privilege level 'guest' or 'admin'. Default is 'guest'
        :return: whether the user was added successfully
        """
        body = [{"cmd": "AddUser", "action": 0,
                 "param": {"User": {"userName": username, "password": password, "level": level}}}]
        r_data = self._execute_command('AddUser', body)[0]
        if r_data["value"]["rspCode"] == 200:
            return True
        print("Could not add user. Camera responded with:", r_data["value"])
        return False

    def modify_user(self, username: str, password: str) -> bool:
        """
        Modify the user's password by specifying their username
        :param username: The user which would want to be modified
        :param password: The new password
        :return: whether the user was modified successfully
        """
        body = [{"cmd": "ModifyUser", "action": 0, "param": {"User": {"userName": username, "password": password}}}]
        r_data = self._execute_command('ModifyUser', body)[0]
        if r_data["value"]["rspCode"] == 200:
            return True
        print(f"Could not modify user: {username}\nCamera responded with: {r_data['value']}")
        return False

    def delete_user(self, username: str) -> bool:
        """
        Delete a user by specifying their username
        :param username: The user which would want to be deleted
        :return: whether the user was deleted successfully
        """
        body = [{"cmd": "DelUser", "action": 0, "param": {"User": {"userName": username}}}]
        r_data = self._execute_command('DelUser', body)[0]
        if r_data["value"]["rspCode"] == 200:
            return True
        print(f"Could not delete user: {username}\nCamera responded with: {r_data['value']}")
        return False
