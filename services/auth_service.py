from services.data_service import DataService

class AuthService:

    @staticmethod
    def login(user_type, user_id, password):
        if user_type == 'student':
            data = DataService.load_data('students')
            users = data.get('students', [])
            for user in users:
                if user['student_id'] == user_id and user['password'] == password:
                    return user
        elif user_type == 'professor':
            data = DataService.load_data('professors')
            users = data.get('professors', [])
            for user in users:
                if user['professor_id'] == user_id and user['password'] == password:
                    return user
        return None

    @staticmethod
    def change_password(user_type, user_id, new_password):
        if user_type == 'student':
            data = DataService.load_data('students')
            users = data.get('students', [])
            for user in users:
                if user['student_id'] == user_id:
                    user['password'] = new_password
                    data['students'] = users
                    DataService.save_data(data, 'students')
                    print("رمز عبور با موفقیت تغییر کرد.")
                    return True
        elif user_type == 'professor':
            data = DataService.load_data('professors')
            users = data.get('professors', [])
            for user in users:
                if user['professor_id'] == user_id:
                    user['password'] = new_password
                    data['professors'] = users
                    DataService.save_data(data, 'professors')
                    print("رمز عبور با موفقیت تغییر کرد.")
                    return True
        print("کاربر یافت نشد.")
        return False