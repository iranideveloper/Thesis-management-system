import json

class DataService:

    @staticmethod
    def load_data(file_name):
        try:
            with open(f'data/{file_name}.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def save_data(data, file_name):
        with open(f'data/{file_name}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def get_user_name(user_type, user_id):
        data = DataService.load_data(f'{user_type}s')
        users = data.get(f'{user_type}s', [])
        if user_type == 'student':
            user = next((u for u in users if u['student_id'] == user_id), None)
            return f"{user['first_name']} {user['last_name']}" if user else user_id
        elif user_type == 'professor':
            user = next((u for u in users if u['professor_id'] == user_id), None)
            return f"{user['first_name']} {user['last_name']}" if user else user_id
        return user_id