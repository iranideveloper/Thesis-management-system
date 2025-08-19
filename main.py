import os
import datetime
from services.auth_service import AuthService
from services.student_service import StudentService
from services.professor_service import ProfessorService
from services.data_service import DataService


class ThesisApp:
    def __init__(self):
        print("سامانه مدیریت پایان‌نامه‌ها")

    def run(self):
        while True:
            print("\n--- منوی اصلی ---")
            user_type = input("آیا دانشجو هستید یا استاد؟ (د/ا): ")

            if user_type == 'د':
                student_id = input("کد دانشجویی: ")
                password = input("رمز عبور: ")
                user = AuthService.login('student', student_id, password)
                if user:
                    full_name = DataService.get_user_name('student', student_id)
                    print(f"ورود با موفقیت انجام شد. خوش آمدید، {full_name}!")
                    self.student_menu(student_id)
                else:
                    print("ورود ناموفق. کد دانشجویی یا رمز عبور اشتباه است.")
            elif user_type == 'ا':
                professor_id = input("کد استادی: ")
                password = input("رمز عبور: ")
                user = AuthService.login('professor', professor_id, password)
                if user:
                    full_name = DataService.get_user_name('professor', professor_id)
                    print(f"ورود با موفقیت انجام شد. خوش آمدید، استاد {full_name}!")
                    self.professor_menu(professor_id)
                else:
                    print("ورود ناموفق. کد استادی یا رمز عبور اشتباه است.")
            else:
                print("انتخاب نامعتبر. لطفاً 'د' یا 'ا' را وارد کنید.")

    def student_menu(self, student_id):
        while True:
            print("\n--- منوی دانشجو ---")
            print("1. درخواست اخذ پایان نامه")
            print("2. مشاهده وضعیت پایان نامه")
            print("3. درخواست دفاع")
            print("4. جستجو در آرشیو پایان نامه‌ها")
            print("5. تغییر رمز عبور")
            print("6. خروج")

            choice = input("انتخاب: ")
            if choice == '1':
                StudentService.request_thesis(student_id)
            elif choice == '2':
                StudentService.view_thesis_status(student_id)
            elif choice == '3':
                StudentService.request_defense(student_id)
            elif choice == '4':
                search_query = input("عبارت جستجو را وارد کنید: ")
                results = StudentService.search_theses_archive(search_query)

                if results:
                    print("\nنتایج یافت شده:")
                    for r in results:
                        prof_name = DataService.get_user_name('professor', r.get('professor_id', ''))
                        stud_name = DataService.get_user_name('student', r.get('student_id', ''))
                        course_info = next((c for c in DataService.load_data('courses') if c['id'] == r['course_id']), None)
                        year_semester = ""
                        if course_info:
                            year_semester = f"{course_info.get('year', '')} / {course_info.get('semester', '')}"

                        referee_names = [DataService.get_user_name('professor', ref_id) for ref_id in r.get('referees', [])]
                        grade = r.get('grade', 'نامشخص')

                        print("-" * 30)
                        print(f"عنوان: {r.get('title', 'نامشخص')}")
                        print(f"چکیده: {r.get('abstract', 'نامشخص')}")
                        print("متن: برای مشاهده متن کامل، فایل PDF را دانلود کنید.")
                        print(f"کلمات کلیدی: {', '.join(r.get('keywords', []))}")
                        print(f"نویسنده: {stud_name}")
                        print(f"سال/نیمسال: {year_semester}")
                        print(f"داوران: {', '.join(referee_names)}")
                        print(f"استاد راهنما: {prof_name}")
                        print(f"لینک دانلود فایل: {r.get('pdf_path', 'نامشخص')}")
                        print(f"نمره: {r.get('final_score', 'نامشخص')} ({grade})")
                    print("-" * 30)
                else:
                    print("نتیجه‌ای یافت نشد.")

            elif choice == '5':
                new_pass = input("رمز عبور جدید را وارد کنید: ")
                AuthService.change_password('student', student_id, new_pass)
            elif choice == '6':
                print("خروج از سامانه.")
                break
            else:
                print("انتخاب نامعتبر.")

    def professor_menu(self, professor_id):
        while True:
            print("\n--- منوی استاد ---")
            print("1. مدیریت درخواست‌های پایان نامه")
            print("2. مدیریت درخواست‌های دفاع")
            print("3. ثبت نمره (به عنوان داور)")
            print("4. جستجو در آرشیو پایان نامه‌ها")
            print("5. تغییر رمز عبور")
            print("6. خروج")

            choice = input("انتخاب: ")
            if choice == '1':
                ProfessorService.manage_thesis_requests(professor_id)
            elif choice == '2':
                ProfessorService.manage_defense_requests(professor_id)
            elif choice == '3':
                ProfessorService.record_score(professor_id)
            elif choice == '4':
                search_query = input("عبارت جستجو را وارد کنید: ")
                results = StudentService.search_theses_archive(search_query)

                if results:
                    print("\nنتایج یافت شده:")
                    for r in results:
                        prof_name = DataService.get_user_name('professor', r.get('professor_id', ''))
                        stud_name = DataService.get_user_name('student', r.get('student_id', ''))
                        course_info = next((c for c in DataService.load_data('courses') if c['id'] == r['course_id']), None)
                        year_semester = ""
                        if course_info:
                            year_semester = f"{course_info.get('year', '')} / {course_info.get('semester', '')}"

                        referee_names = [DataService.get_user_name('professor', ref_id) for ref_id in r.get('referees', [])]
                        grade = r.get('grade', 'نامشخص')

                        print("-" * 30)
                        print(f"عنوان: {r.get('title', 'نامشخص')}")
                        print(f"چکیده: {r.get('abstract', 'نامشخص')}")
                        print("متن: برای مشاهده متن کامل، فایل PDF را دانلود کنید.")
                        print(f"کلمات کلیدی: {', '.join(r.get('keywords', []))}")
                        print(f"نویسنده: {stud_name}")
                        print(f"سال/نیمسال: {year_semester}")
                        print(f"داوران: {', '.join(referee_names)}")
                        print(f"استاد راهنما: {prof_name}")
                        print(f"لینک دانلود فایل: {r.get('pdf_path', 'نامشخص')}")
                        print(f"نمره: {r.get('final_score', 'نامشخص')} ({grade})")
                    print("-" * 30)
                else:
                    print("نتیجه‌ای یافت نشد.")

            elif choice == '5':
                new_pass = input("رمز عبور جدید را وارد کنید: ")
                AuthService.change_password('professor', professor_id, new_pass)
            elif choice == '6':
                print("خروج از سامانه.")
                break
            else:
                print("انتخاب نامعتبر.")


if __name__ == "__main__":
    app = ThesisApp()
    app.run()