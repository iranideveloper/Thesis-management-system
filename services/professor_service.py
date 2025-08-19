import datetime
from services.data_service import DataService


class ProfessorService:

    @staticmethod
    def manage_thesis_requests(professor_id):
        theses = DataService.load_data('theses')
        professors_data = DataService.load_data('professors')
        professors = professors_data.get('professors', [])
        professor_data = next((p for p in professors if p['professor_id'] == professor_id), None)

        if not professor_data:
            print("اطلاعات استاد یافت نشد.")
            return

        pending_requests = [t for t in theses if
                            t['professor_id'] == professor_id and t['status'] == 'در انتظار تأیید استاد']

        if not pending_requests:
            print("درخواست جدیدی برای استاد راهنما شدن ندارید.")
            return

        print("درخواست‌های پایان نامه جدید:")
        for i, req in enumerate(pending_requests):
            stud_name = DataService.get_user_name('student', req['student_id'])
            print(f"{i + 1}. دانشجوی: {stud_name}")

        try:
            choice = int(input("شماره درخواست برای بررسی را انتخاب کنید (0 برای بازگشت): ")) - 1
            if choice == -1: return

            if 0 <= choice < len(pending_requests):
                selected_request = pending_requests[choice]

                if professor_data['supervision_capacity'] <= 0:
                    print("ظرفیت استاد برای استاد راهنمایی تکمیل است.")
                    return

                action = input("آیا درخواست را تأیید می‌کنید یا رد؟ (تأیید/رد): ")
                if action == 'تأیید':
                    selected_request['status'] = 'تأیید شده'
                    selected_request['approval_date'] = datetime.date.today().isoformat()
                    professor_data['supervision_capacity'] -= 1
                    print("درخواست دانشجو با موفقیت تأیید شد.")
                elif action == 'رد':
                    selected_request['status'] = 'رد شده'
                    print("درخواست دانشجو رد شد.")
                else:
                    print("عمل نامعتبر.")

                DataService.save_data(theses, 'theses')
                DataService.save_data(professors_data, 'professors')
            else:
                print("انتخاب نامعتبر.")
        except ValueError:
            print("ورودی نامعتبر است.")

    @staticmethod
    def manage_defense_requests(professor_id):
        theses = DataService.load_data('theses')
        pending_defense = [t for t in theses if t['professor_id'] == professor_id and t['status'] == 'در انتظار تأیید دفاع']

        if not pending_defense:
            print("درخواست دفاع جدیدی ندارید.")
            return

        print("درخواست‌های دفاع جدید:")
        for i, req in enumerate(pending_defense):
            stud_name = DataService.get_user_name('student', req['student_id'])
            print(f"{i + 1}. دانشجوی: {stud_name} - عنوان: {req.get('title', '')}")

        try:
            choice = int(input("شماره درخواست برای مدیریت را انتخاب کنید (0 برای بازگشت): ")) - 1
            if choice == -1: return

            if 0 <= choice < len(pending_defense):
                selected_thesis = pending_defense[choice]
                action = input("آیا دفاع را تأیید می‌کنید یا رد؟ (تأیید/رد): ")
                if action == 'تأیید':
                    defense_date = input("تاریخ دفاع را وارد کنید (YYYY-MM-DD): ")
                    internal_referee_id = input("کد استادی داور داخلی را وارد کنید: ")
                    external_referee_id = input("کد استادی داور خارجی را وارد کنید: ")

                    selected_thesis['status'] = 'در انتظار برگزاری دفاع'
                    selected_thesis['defense_date'] = defense_date
                    selected_thesis['referees'] = [internal_referee_id, external_referee_id]
                    print("درخواست دفاع تأیید شد. تاریخ و داوران ثبت شدند.")
                elif action == 'رد':
                    selected_thesis['status'] = 'رد دفاع'
                    print("درخواست دفاع رد شد.")
                else:
                    print("عمل نامعتبر.")

                DataService.save_data(theses, 'theses')
            else:
                print("انتخاب نامعتبر.")
        except ValueError:
            print("ورودی نامعتبر است.")

    @staticmethod
    def record_score(professor_id):
        theses = DataService.load_data('theses')
        professor_theses = [t for t in theses if t.get('referees') and professor_id in t['referees'] and t.get(
            'status') == 'در انتظار برگزاری دفاع']

        if not professor_theses:
            print("شما پایان نامه ای برای نمره دهی ندارید.")
            return

        print("پایان نامه‌های نیازمند نمره دهی:")
        for i, thesis in enumerate(professor_theses):
            stud_name = DataService.get_user_name('student', thesis['student_id'])
            print(f"{i + 1}. عنوان: {thesis.get('title')} - دانشجوی: {stud_name}")

        try:
            choice = int(input("شماره پایان نامه برای ثبت نمره را انتخاب کنید (0 برای بازگشت): ")) - 1
            if choice == -1: return

            if 0 <= choice < len(professor_theses):
                selected_thesis = professor_theses[choice]
                score = float(input("نمره نهایی را وارد کنید (۰-۲۰): "))

                if 17 <= score <= 20:
                    grade = 'الف'
                elif 13 <= score < 17:
                    grade = 'ب'
                elif 10 <= score < 13:
                    grade = 'ج'
                else:
                    grade = 'د'

                selected_thesis['final_score'] = score
                selected_thesis['grade'] = grade
                selected_thesis['status'] = 'دفاع شده'

                professors_data = DataService.load_data('professors')
                professors = professors_data.get('professors', [])
                professor_data = next((p for p in professors if p['professor_id'] == professor_id), None)
                if professor_data:
                    professor_data['referee_capacity'] += 1
                    DataService.save_data(professors_data, 'professors')

                DataService.save_data(theses, 'theses')
                print(f"نمره {score} با موفقیت ثبت شد. نتیجه دفاع: {grade}")
            else:
                print("انتخاب نامعتبر.")
        except ValueError:
            print("ورودی نامعتبر است.")