import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import datetime
from services import auth_service, student_service, professor_service
from services.data_service import get_user_name, load_data, save_data

# Define some styles and colors for a modern look
BG_COLOR = "#f0f0f0"
PRIMARY_COLOR = "#0d47a1"  # Dark blue
BUTTON_TEXT_COLOR = "white"
FONT_BOLD = ("Arial", 12, "bold")
FONT_NORMAL = ("Arial", 10)


class ThesisManagementGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("سامانه مدیریت پایان‌نامه‌ها")
        self.geometry("600x450")
        self.config(bg=BG_COLOR)
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=BG_COLOR)
        self.style.configure('TLabel', background=BG_COLOR, font=FONT_NORMAL)
        self.style.configure('TButton', background=PRIMARY_COLOR, foreground=BUTTON_TEXT_COLOR, font=FONT_BOLD)

        self.user_id = None
        self.user_type = None

        self.show_login_page()

    def show_login_page(self):
        self.clear_frame()
        login_page = LoginPage(self)
        login_page.pack(fill="both", expand=True)

    def show_student_menu(self):
        self.clear_frame()
        student_menu_page = StudentMenuPage(self)
        student_menu_page.pack(fill="both", expand=True)

    def show_professor_menu(self):
        self.clear_frame()
        professor_menu_page = ProfessorMenuPage(self)
        professor_menu_page.pack(fill="both", expand=True)

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()


class LoginPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        container = ttk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(container, text="ورود به سامانه", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2,
                                                                                     pady=20)

        # User Type
        ttk.Label(container, text="نوع کاربر:").grid(row=1, column=1, pady=5, padx=5, sticky="e")
        self.user_type_var = tk.StringVar(self)
        self.user_type_var.set("دانشجو")
        user_type_option = ttk.OptionMenu(container, self.user_type_var, "دانشجو", "استاد")
        user_type_option.grid(row=1, column=0, pady=5, padx=5, sticky="w")

        # ID Entry
        ttk.Label(container, text="کد کاربری:").grid(row=2, column=1, pady=5, padx=5, sticky="e")
        self.id_entry = ttk.Entry(container)
        self.id_entry.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        # Password Entry
        ttk.Label(container, text="رمز عبور:").grid(row=3, column=1, pady=5, padx=5, sticky="e")
        self.password_entry = ttk.Entry(container, show="*")
        self.password_entry.grid(row=3, column=0, pady=5, padx=5, sticky="w")

        # Login Button
        login_button = ttk.Button(container, text="ورود", command=self.login, style='TButton')
        login_button.grid(row=4, column=0, columnspan=2, pady=20)

    def login(self):
        user_type = self.user_type_var.get()
        user_id = self.id_entry.get()
        password = self.password_entry.get()

        if user_type == "دانشجو":
            self.parent.user_type = 'student'
            logged_in_user = auth_service.login('student', user_id, password)
        else:
            self.parent.user_type = 'professor'
            logged_in_user = auth_service.login('professor', user_id, password)

        if logged_in_user:
            self.parent.user_id = user_id
            messagebox.showinfo("ورود موفق", "ورود با موفقیت انجام شد.")
            if self.parent.user_type == 'student':
                self.parent.show_student_menu()
            else:
                self.parent.show_professor_menu()
        else:
            messagebox.showerror("ورود ناموفق", "کد کاربری یا رمز عبور اشتباه است.")


class StudentMenuPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        container = ttk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        full_name = get_user_name('student', self.parent.user_id)
        ttk.Label(container, text=f"پنل دانشجو: {full_name}", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=20,
                                                                                               columnspan=2)

        buttons = [
            ("درخواست اخذ پایان نامه", self.request_thesis_gui),
            ("مشاهده وضعیت پایان نامه", self.view_thesis_status_gui),
            ("درخواست دفاع", self.request_defense_gui),
            ("جستجو در آرشیو پایان نامه‌ها", self.search_theses_archive_gui),
            ("تغییر رمز عبور", self.change_password_gui),
            ("خروج", self.logout)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(container, text=text, command=command, style='TButton')
            btn.grid(row=i + 1, column=0, pady=5, padx=10, sticky="ew")

    def request_thesis_gui(self):
        courses = load_data('courses')
        available_courses = [c for c in courses if c['capacity'] > 0]

        if not available_courses:
            messagebox.showinfo("اطلاعات", "درسی با ظرفیت خالی برای اخذ پایان نامه موجود نیست.")
            return

        request_window = tk.Toplevel(self.parent)
        request_window.title("درخواست اخذ پایان نامه")
        request_window.geometry("500x400")

        title_label = ttk.Label(request_window, text="دروس پایان نامه با ظرفیت خالی:", font=FONT_BOLD)
        title_label.pack(pady=10)

        listbox_frame = ttk.Frame(request_window)
        listbox_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)

        for i, course in enumerate(available_courses):
            prof_name = get_user_name('professor', course['professor_id'])
            listbox.insert(tk.END, f"{i + 1}. {course['title']} - استاد: {prof_name} - ظرفیت: {course['capacity']}")

        def select_course():
            try:
                selection = listbox.curselection()
                if selection:
                    choice = selection[0]
                    selected_course = available_courses[choice]
                    success = student_service.request_thesis_from_gui(self.parent.user_id, selected_course)
                    if success:
                        messagebox.showinfo("موفقیت", "درخواست اخذ پایان نامه با موفقیت ثبت شد.")
                    else:
                        messagebox.showerror("خطا",
                                             "شما قبلاً درخواست پایان نامه ثبت کرده‌اید یا پایان نامه تأیید شده دارید.")
                    request_window.destroy()
            except Exception as e:
                messagebox.showerror("خطا", str(e))

        select_button = ttk.Button(request_window, text="انتخاب درس", command=select_course)
        select_button.pack(pady=10)

    def view_thesis_status_gui(self):
        status_window = tk.Toplevel(self.parent)
        status_window.title("وضعیت پایان نامه")
        status_window.geometry("500x300")

        theses = load_data('theses')
        student_thesis = [t for t in theses if t['student_id'] == self.parent.user_id]

        if not student_thesis:
            ttk.Label(status_window, text="شما هیچ درخواست پایان نامه‌ای ثبت نکرده‌اید.").pack(pady=20)
            return

        for thesis in student_thesis:
            status = thesis.get('status', 'نامشخص')
            status_text = f"وضعیت پایان نامه: {status}"

            if status == 'تأیید شده':
                prof_name = get_user_name('professor', thesis.get('professor_id', ''))
                status_text += f"\nاستاد راهنما: {prof_name}"
                status_text += f"\nتاریخ تأیید: {thesis.get('approval_date')}"

            ttk.Label(status_window, text=status_text, justify=tk.RIGHT).pack(pady=10, padx=10)

    def request_defense_gui(self):
        theses = load_data('theses')
        student_thesis = next(
            (t for t in theses if t['student_id'] == self.parent.user_id and t['status'] == 'تأیید شده'), None)

        if not student_thesis:
            messagebox.showinfo("اطلاعات", "شما پایان نامه تأیید شده‌ای برای درخواست دفاع ندارید.")
            return

        if student_thesis.get('defense_request_date'):
            messagebox.showinfo("اطلاعات", "شما قبلاً درخواست دفاع خود را ثبت کرده‌اید و در انتظار تأیید استاد هستید.")
            return

        defense_window = tk.Toplevel(self.parent)
        defense_window.title("درخواست دفاع")
        defense_window.geometry("400x400")

        fields_frame = ttk.Frame(defense_window, padding=10)
        fields_frame.pack()

        ttk.Label(fields_frame, text="عنوان پایان نامه:").grid(row=0, column=0, sticky="e", pady=5)
        title_entry = ttk.Entry(fields_frame, width=40)
        title_entry.grid(row=0, column=1, sticky="w", pady=5)

        ttk.Label(fields_frame, text="چکیده:").grid(row=1, column=0, sticky="e", pady=5)
        abstract_text = tk.Text(fields_frame, height=5, width=40)
        abstract_text.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(fields_frame, text="کلمات کلیدی (جدا شده با کاما):").grid(row=2, column=0, sticky="e", pady=5)
        keywords_entry = ttk.Entry(fields_frame, width=40)
        keywords_entry.grid(row=2, column=1, sticky="w", pady=5)

        ttk.Label(fields_frame, text="مسیر فایل PDF:").grid(row=3, column=0, sticky="e", pady=5)
        pdf_entry = ttk.Entry(fields_frame, width=40)
        pdf_entry.grid(row=3, column=1, sticky="w", pady=5)

        def submit_defense_request():
            title = title_entry.get()
            abstract = abstract_text.get("1.0", tk.END).strip()
            keywords = [k.strip() for k in keywords_entry.get().split(',') if k.strip()]
            pdf_path = pdf_entry.get()

            success = student_service.request_defense_from_gui(self.parent.user_id, title, abstract, keywords, pdf_path)
            if success:
                messagebox.showinfo("موفقیت", "درخواست دفاع با موفقیت ثبت شد.")
                defense_window.destroy()
            else:
                messagebox.showerror("خطا", "فایل‌های وارد شده یافت نشدند.")

        submit_btn = ttk.Button(defense_window, text="ثبت درخواست دفاع", command=submit_defense_request)
        submit_btn.pack(pady=20)

    def search_theses_archive_gui(self):
        search_window = tk.Toplevel(self.parent)
        search_window.title("جستجو در آرشیو")
        search_window.geometry("600x500")

        search_frame = ttk.Frame(search_window, padding=10)
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="جستجو:").pack(side=tk.RIGHT)
        query_entry = ttk.Entry(search_frame, width=50)
        query_entry.pack(side=tk.RIGHT, padx=5)

        results_frame = ttk.Frame(search_window, padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(results_frame)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)

        def perform_search():
            query = query_entry.get().strip().lower()
            theses = load_data('theses')
            courses = load_data('courses')
            defended_theses = [t for t in theses if t.get('status') == 'دفاع شده']
            results = []

            for thesis in defended_theses:
                # Create a single searchable string from all relevant fields
                searchable_text = []
                [cite_start]
                searchable_text.append(thesis.get('title', '').lower())[cite: 64]
                [cite_start]
                searchable_text.append(thesis.get('abstract', '').lower())[cite: 64]
                [cite_start]
                searchable_text.extend([k.lower() for k in thesis.get('keywords', [])])[cite: 67]

                [cite_start]
                prof_name = get_user_name('professor', thesis.get('professor_id', '')).lower()[cite: 72]
                searchable_text.append(prof_name)

                [cite_start]
                stud_name = get_user_name('student', thesis.get('student_id', '')).lower()[cite: 68]
                searchable_text.append(stud_name)

                searchable_text.append(thesis.get('defense_date', '').lower())

                course_info = next((c for c in courses if c['id'] == thesis['course_id']), None)
                if course_info:
                    searchable_text.append(str(course_info.get('year', '')).lower())
                    searchable_text.append(course_info.get('semester', '').lower())

                [cite_start]
                referee_names = [get_user_name('professor', r).lower() for r in thesis.get('referees', [])][cite: 71]
                searchable_text.extend(referee_names)

                # Check if the query is in any of the searchable text fields
                if any(query in text for text in searchable_text):
                    results.append(thesis)

            listbox.delete(0, tk.END)
            if results:
                for r in results:
                    prof_name = get_user_name('professor', r.get('professor_id', ''))
                    stud_name = get_user_name('student', r.get('student_id', ''))

                    course_info = next((c for c in courses if c['id'] == r['course_id']), None)
                    year_semester = ""
                    if course_info:
                        [cite_start]
                        year_semester = f"{course_info.get('year', '')} / {course_info.get('semester', '')}"[cite: 69]

                    referee_names = [get_user_name('professor', ref_id) for ref_id in r.get('referees', [])]

                    # Determine score grade
                    [cite_start]
                    grade = r.get('grade', 'نامشخص')[cite: 74]

                    [cite_start]
                    listbox.insert(tk.END, f"عنوان: {r.get('title', 'نامشخص')}")[cite: 64]
                    [cite_start]
                    listbox.insert(tk.END, f"چکیده: {r.get('abstract', 'نامشخص')}")[cite: 64]
                    [cite_start]
                    listbox.insert(tk.END, f"متن: برای مشاهده متن کامل، فایل PDF را دانلود کنید.")[cite: 65]
                    [cite_start]
                    listbox.insert(tk.END, f"کلمات کلیدی: {', '.join(r.get('keywords', []))}")[cite: 67]
                    [cite_start]
                    listbox.insert(tk.END, f"نویسنده: {stud_name}")[cite: 68]
                    [cite_start]
                    listbox.insert(tk.END, f"سال/نیمسال: {year_semester}")[cite: 69]
                    [cite_start]
                    listbox.insert(tk.END, f"داوران: {', '.join(referee_names)}")[cite: 71]
                    [cite_start]
                    listbox.insert(tk.END, f"استاد راهنما: {prof_name}")[cite: 72]
                    [cite_start]
                    listbox.insert(tk.END, f"لینک دانلود فایل: {r.get('pdf_path', 'نامشخص')}")[cite: 73]
                    [cite_start]
                    listbox.insert(tk.END, f"نمره: {r.get('final_score', 'نامشخص')} ({grade})")[cite: 74]
                    listbox.insert(tk.END, "---" * 20)
            else:
                listbox.insert(tk.END, "نتیجه‌ای یافت نشد.")

        search_button = ttk.Button(search_frame, text="جستجو", command=perform_search)
        search_button.pack(side=tk.RIGHT, padx=5)

    def change_password_gui(self):
        new_password = simpledialog.askstring("تغییر رمز عبور", "رمز عبور جدید را وارد کنید:")
        if new_password:
            auth_service.change_password('student', self.parent.user_id, new_password)
            messagebox.showinfo("موفقیت", "رمز عبور با موفقیت تغییر یافت.")

    def logout(self):
        self.parent.user_id = None
        self.parent.user_type = None
        messagebox.showinfo("خروج", "شما از سامانه خارج شدید.")
        self.parent.show_login_page()


class ProfessorMenuPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        container = ttk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")
        full_name = get_user_name('professor', self.parent.user_id)
        ttk.Label(container, text=f"پنل استاد: {full_name}", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=20,
                                                                                              columnspan=2)

        buttons = [
            ("مدیریت درخواست‌های پایان نامه", self.manage_thesis_requests_gui),
            ("مدیریت درخواست‌های دفاع", self.manage_defense_requests_gui),
            ("ثبت نمره (به عنوان داور)", self.record_score_gui),
            ("جستجو در آرشیو پایان نامه‌ها", self.search_theses_archive_gui),
            ("تغییر رمز عبور", self.change_password_gui),
            ("خروج", self.logout)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(container, text=text, command=command, style='TButton')
            btn.grid(row=i + 1, column=0, pady=5, padx=10, sticky="ew")

    def manage_thesis_requests_gui(self):
        requests_window = tk.Toplevel(self.parent)
        requests_window.title("مدیریت درخواست‌های پایان نامه")
        requests_window.geometry("500x400")

        pending_requests = professor_service.get_pending_thesis_requests(self.parent.user_id)

        if not pending_requests:
            ttk.Label(requests_window, text="درخواست جدیدی برای استاد راهنما شدن ندارید.").pack(pady=20)
            return

        listbox_frame = ttk.Frame(requests_window, padding=10)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)

        for i, req in enumerate(pending_requests):
            stud_name = get_user_name('student', req['student_id'])
            listbox.insert(tk.END, f"{i + 1}. دانشجوی: {stud_name}")

        def approve_request():
            try:
                selection = listbox.curselection()
                if selection:
                    req_index = selection[0]
                    professor_service.process_thesis_request(self.parent.user_id, pending_requests[req_index], "تأیید")
                    messagebox.showinfo("موفقیت", "درخواست دانشجو با موفقیت تأیید شد.")
                    requests_window.destroy()
            except Exception as e:
                messagebox.showerror("خطا", str(e))

        def reject_request():
            try:
                selection = listbox.curselection()
                if selection:
                    req_index = selection[0]
                    professor_service.process_thesis_request(self.parent.user_id, pending_requests[req_index], "رد")
                    messagebox.showinfo("موفقیت", "درخواست دانشجو رد شد.")
                    requests_window.destroy()
            except Exception as e:
                messagebox.showerror("خطا", str(e))

        approve_btn = ttk.Button(requests_window, text="تأیید", command=approve_request)
        approve_btn.pack(side=tk.LEFT, padx=10, pady=10)
        reject_btn = ttk.Button(requests_window, text="رد", command=reject_request)
        reject_btn.pack(side=tk.RIGHT, padx=10, pady=10)

    def manage_defense_requests_gui(self):
        defense_requests_window = tk.Toplevel(self.parent)
        defense_requests_window.title("مدیریت درخواست‌های دفاع")
        defense_requests_window.geometry("500x400")

        pending_defense = professor_service.get_pending_defense_requests(self.parent.user_id)

        if not pending_defense:
            ttk.Label(defense_requests_window, text="درخواست دفاع جدیدی ندارید.").pack(pady=20)
            return

        listbox_frame = ttk.Frame(defense_requests_window, padding=10)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)

        for i, req in enumerate(pending_defense):
            stud_name = get_user_name('student', req['student_id'])
            listbox.insert(tk.END, f"{i + 1}. عنوان: {req.get('title', '')} - دانشجوی: {stud_name}")

        def approve_defense_request():
            selection = listbox.curselection()
            if not selection:
                return

            req_index = selection[0]
            selected_thesis = pending_defense[req_index]

            details_window = tk.Toplevel(defense_requests_window)
            details_window.title("تأیید دفاع")
            details_window.geometry("300x200")

            ttk.Label(details_window, text="تاریخ دفاع (YYYY-MM-DD):").pack(pady=5)
            defense_date_entry = ttk.Entry(details_window)
            defense_date_entry.pack(pady=5)

            ttk.Label(details_window, text="کد استادی داور داخلی:").pack(pady=5)
            internal_referee_entry = ttk.Entry(details_window)
            internal_referee_entry.pack(pady=5)

            ttk.Label(details_window, text="کد استادی داور خارجی:").pack(pady=5)
            external_referee_entry = ttk.Entry(details_window)
            external_referee_entry.pack(pady=5)

            def submit_details():
                defense_date = defense_date_entry.get()
                internal_referee = internal_referee_entry.get()
                external_referee = external_referee_entry.get()

                if professor_service.process_defense_request(self.parent.user_id, selected_thesis, "تأیید",
                                                             defense_date, internal_referee, external_referee):
                    messagebox.showinfo("موفقیت", "درخواست دفاع تأیید شد. تاریخ و داوران ثبت شدند.")
                    details_window.destroy()
                    defense_requests_window.destroy()
                else:
                    messagebox.showerror("خطا", "اطلاعات وارد شده نامعتبر است.")

            submit_btn = ttk.Button(details_window, text="ثبت", command=submit_details)
            submit_btn.pack(pady=10)

        def reject_defense_request():
            selection = listbox.curselection()
            if not selection:
                return
            req_index = selection[0]
            selected_thesis = pending_defense[req_index]
            professor_service.process_defense_request(self.parent.user_id, selected_thesis, "رد")
            messagebox.showinfo("موفقیت", "درخواست دفاع رد شد.")
            defense_requests_window.destroy()

        approve_btn = ttk.Button(defense_requests_window, text="تأیید", command=approve_defense_request)
        approve_btn.pack(side=tk.LEFT, padx=10, pady=10)
        reject_btn = ttk.Button(defense_requests_window, text="رد", command=reject_defense_request)
        reject_btn.pack(side=tk.RIGHT, padx=10, pady=10)

    def record_score_gui(self):
        score_window = tk.Toplevel(self.parent)
        score_window.title("ثبت نمره")
        score_window.geometry("500x400")

        professor_theses = professor_service.get_theses_for_scoring(self.parent.user_id)

        if not professor_theses:
            ttk.Label(score_window, text="شما پایان نامه ای برای نمره دهی ندارید.").pack(pady=20)
            return

        listbox_frame = ttk.Frame(score_window, padding=10)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)

        for i, thesis in enumerate(professor_theses):
            stud_name = get_user_name('student', thesis['student_id'])
            listbox.insert(tk.END, f"{i + 1}. عنوان: {thesis.get('title')} - دانشجوی: {stud_name}")

        def submit_score():
            selection = listbox.curselection()
            if not selection:
                return

            thesis_index = selection[0]
            selected_thesis = professor_theses[thesis_index]

            score_str = simpledialog.askstring("ثبت نمره", "نمره نهایی را وارد کنید (۰-۲۰):")
            try:
                score = float(score_str)
                if professor_service.record_thesis_score(self.parent.user_id, selected_thesis, score):
                    messagebox.showinfo("موفقیت", f"نمره {score} با موفقیت ثبت شد.")
                    score_window.destroy()
                else:
                    messagebox.showerror("خطا", "نمره وارد شده معتبر نیست.")
            except (ValueError, TypeError):
                messagebox.showerror("خطا", "نمره وارد شده معتبر نیست.")

        submit_btn = ttk.Button(score_window, text="ثبت نمره", command=submit_score)
        submit_btn.pack(pady=10)

    def search_theses_archive_gui(self):
        search_window = tk.Toplevel(self.parent)
        search_window.title("جستجو در آرشیو")
        search_window.geometry("600x500")

        search_frame = ttk.Frame(search_window, padding=10)
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="جستجو:").pack(side=tk.RIGHT)
        query_entry = ttk.Entry(search_frame, width=50)
        query_entry.pack(side=tk.RIGHT, padx=5)

        results_frame = ttk.Frame(search_window, padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(results_frame)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)

        def perform_search():
            query = query_entry.get().strip().lower()
            theses = load_data('theses')
            courses = load_data('courses')
            [cite_start]
            defended_theses = [t for t in theses if t.get('status') == 'دفاع شده'][cite: 58]
            results = []

            for thesis in defended_theses:
                searchable_text = []
                [cite_start]
                searchable_text.append(thesis.get('title', '').lower())[cite: 64]
                [cite_start]
                searchable_text.append(thesis.get('abstract', '').lower())[cite: 64]
                [cite_start]
                searchable_text.extend([k.lower() for k in thesis.get('keywords', [])])[cite: 67]

                [cite_start]
                prof_name = get_user_name('professor', thesis.get('professor_id', '')).lower()[cite: 72]
                searchable_text.append(prof_name)

                [cite_start]
                stud_name = get_user_name('student', thesis.get('student_id', '')).lower()[cite: 68]
                searchable_text.append(stud_name)

                searchable_text.append(thesis.get('defense_date', '').lower())

                course_info = next((c for c in courses if c['id'] == thesis['course_id']), None)
                if course_info:
                    searchable_text.append(str(course_info.get('year', '')).lower())
                    searchable_text.append(course_info.get('semester', '').lower())

                [cite_start]
                referee_names = [get_user_name('professor', r).lower() for r in thesis.get('referees', [])][cite: 71]
                searchable_text.extend(referee_names)

                if any(query in text for text in searchable_text):
                    results.append(thesis)

            listbox.delete(0, tk.END)
            if results:
                for r in results:
                    prof_name = get_user_name('professor', r.get('professor_id', ''))
                    stud_name = get_user_name('student', r.get('student_id', ''))

                    course_info = next((c for c in courses if c['id'] == r['course_id']), None)
                    year_semester = ""
                    if course_info:
                        [cite_start]
                        year_semester = f"{course_info.get('year', '')} / {course_info.get('semester', '')}"[cite: 69]

                    referee_names = [get_user_name('professor', ref_id) for ref_id in r.get('referees', [])]

                    # Determine score grade
                    [cite_start]
                    grade = r.get('grade', 'نامشخص')[cite: 74]

                    [cite_start]
                    listbox.insert(tk.END, f"عنوان: {r.get('title', 'نامشخص')}")[cite: 64]
                    [cite_start]
                    listbox.insert(tk.END, f"چکیده: {r.get('abstract', 'نامشخص')}")[cite: 64]
                    [cite_start]
                    listbox.insert(tk.END, f"متن: برای مشاهده متن کامل، فایل PDF را دانلود کنید.")[cite: 65]
                    [cite_start]
                    listbox.insert(tk.END, f"کلمات کلیدی: {', '.join(r.get('keywords', []))}")[cite: 67]
                    [cite_start]
                    listbox.insert(tk.END, f"نویسنده: {stud_name}")[cite: 68]
                    [cite_start]
                    listbox.insert(tk.END, f"سال/نیمسال: {year_semester}")[cite: 69]
                    [cite_start]
                    listbox.insert(tk.END, f"داوران: {', '.join(referee_names)}")[cite: 71]
                    [cite_start]
                    listbox.insert(tk.END, f"استاد راهنما: {prof_name}")[cite: 72]
                    [cite_start]
                    listbox.insert(tk.END, f"لینک دانلود فایل: {r.get('pdf_path', 'نامشخص')}")[cite: 73]
                    [cite_start]
                    listbox.insert(tk.END, f"نمره: {r.get('final_score', 'نامشخص')} ({grade})")[cite: 74]
                    listbox.insert(tk.END, "---" * 20)
            else:
                listbox.insert(tk.END, "نتیجه‌ای یافت نشد.")

        search_button = ttk.Button(search_frame, text="جستجو", command=perform_search)
        search_button.pack(side=tk.RIGHT, padx=5)

    def change_password_gui(self):
        new_password = simpledialog.askstring("تغییر رمز عبور", "رمز عبور جدید را وارد کنید:")
        if new_password:
            auth_service.change_password('professor', self.parent.user_id, new_password)
            messagebox.showinfo("موفقیت", "رمز عبور با موفقیت تغییر یافت.")

    def logout(self):
        self.parent.user_id = None
        self.parent.user_type = None
        messagebox.showinfo("خروج", "شما از سامانه خارج شدید.")
        self.parent.show_login_page()


if __name__ == "__main__":
    app = ThesisManagementGUI()
    app.mainloop()