import os
import datetime
from services.data_service import DataService


class StudentService:

    @staticmethod
    def request_thesis(student_id):
        courses = DataService.load_data('courses')
        available_courses = [c for c in courses if c['capacity'] > 0]

        if not available_courses:
            print("درسی با ظرفیت خالی برای اخذ پایان نامه موجود نیست.")
            return

        print("دروس پایان نامه با ظرفیت خالی:")
        for i, course in enumerate(available_courses):
            prof_name = DataService.get_user_name('professor', course['professor_id'])
            print(f"{i + 1}. {course['title']} - استاد: {prof_name} - ظرفیت: {course['capacity']}")

        try:
            choice = int(input("شماره درس مورد نظر را انتخاب کنید: ")) - 1
            if 0 <= choice < len(available_courses):
                selected_course = available_courses[choice]

                theses = DataService.load_data('theses')
                if any(t['student_id'] == student_id and t['status'] in ['در انتظار تأیید استاد', 'تأیید شده'] for t in
                       theses):
                    print("شما قبلاً درخواست پایان نامه ثبت کرده‌اید یا پایان نامه تأیید شده دارید.")
                    return

                new_thesis = {
                    "id": str(len(theses) + 1),
                    "student_id": student_id,
                    "course_id": selected_course['id'],
                    "professor_id": selected_course['professor_id'],
                    "status": "در انتظار تأیید استاد",
                    "request_date": datetime.date.today().isoformat()
                }
                theses.append(new_thesis)
                DataService.save_data(theses, 'theses')
                print("درخواست اخذ پایان نامه با موفقیت ثبت و برای استاد ارسال شد.")
            else:
                print("انتخاب نامعتبر.")
        except ValueError:
            print("ورودی نامعتبر است.")

    @staticmethod
    def view_thesis_status(student_id):
        theses = DataService.load_data('theses')
        student_thesis = [t for t in theses if t['student_id'] == student_id]

        if not student_thesis:
            print("شما هیچ درخواست پایان نامه‌ای ثبت نکرده‌اید.")
            return

        for thesis in student_thesis:
            prof_name = DataService.get_user_name('professor', thesis.get('professor_id', ''))
            print(f"وضعیت پایان نامه: {thesis.get('status', 'نامشخص')}")
            if thesis.get('status') == 'تأیید شده':
                print(f"استاد راهنما: {prof_name}")
                print(f"تاریخ تأیید: {thesis.get('approval_date')}")

    @staticmethod
    def request_defense(student_id):
        theses = DataService.load_data('theses')
        student_thesis = next((t for t in theses if t['student_id'] == student_id and t['status'] == 'تأیید شده'), None)

        if not student_thesis:
            print("شما پایان نامه تأیید شده‌ای برای درخواست دفاع ندارید.")
            return

        approval_date_str = student_thesis.get('approval_date')
        if not approval_date_str:
            print("تاریخ تایید پایان نامه موجود نیست.")
            return

        try:
            approval_date = datetime.datetime.fromisoformat(approval_date_str)
            three_months_ago = datetime.datetime.now() - datetime.timedelta(days=90)

            if approval_date > three_months_ago:
                print("برای درخواست دفاع، حداقل ۳ ماه از تاریخ تایید پایان نامه باید گذشته باشد.")
                return
        except ValueError:
            print("فرمت تاریخ تایید پایان نامه نامعتبر است.")
            return

        title = input("عنوان پایان نامه: ")
        abstract = input("چکیده: ")
        keywords = input("کلمات کلیدی (با کاما جدا کنید): ").split(',')

        print("لطفا فایل‌ها را در پوشه 'data/files' قرار دهید.")
        pdf_path = input("مسیر فایل PDF پایان نامه (مثال: data/files/thesis.pdf): ")

        if not os.path.exists(pdf_path):
            print("فایل PDF وارد شده یافت نشد. درخواست دفاع ثبت نشد.")
            return

        student_thesis['title'] = title
        student_thesis['abstract'] = abstract
        student_thesis['keywords'] = [k.strip() for k in keywords if k.strip()]
        student_thesis['pdf_path'] = pdf_path
        student_thesis['defense_request_date'] = datetime.date.today().isoformat()
        student_thesis['status'] = 'در انتظار تأیید دفاع'

        DataService.save_data(theses, 'theses')
        print("درخواست دفاع با موفقیت ثبت و برای استاد ارسال شد.")

    @staticmethod
    def search_theses_archive(query):
        theses = DataService.load_data('theses')
        courses = DataService.load_data('courses')
        defended_theses = [t for t in theses if t.get('status') == 'دفاع شده']
        results = []

        for thesis in defended_theses:
            searchable_text = []
            searchable_text.append(thesis.get('title', '').lower())
            searchable_text.append(thesis.get('abstract', '').lower())
            searchable_text.extend([k.lower() for k in thesis.get('keywords', [])])

            prof_name = DataService.get_user_name('professor', thesis.get('professor_id', '')).lower()
            searchable_text.append(prof_name)

            stud_name = DataService.get_user_name('student', thesis.get('student_id', '')).lower()
            searchable_text.append(stud_name)

            searchable_text.append(thesis.get('defense_date', '').lower())

            course_info = next((c for c in courses if c['id'] == thesis['course_id']), None)
            if course_info:
                searchable_text.append(str(course_info.get('year', '')).lower())
                searchable_text.append(course_info.get('semester', '').lower())

            referee_names = [DataService.get_user_name('professor', r).lower() for r in thesis.get('referees', [])]
            searchable_text.extend(referee_names)

            if any(query.lower() in text for text in searchable_text):
                results.append(thesis)

        return results