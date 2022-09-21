import os
import re
import socket
import string
import threading
import time
import urllib
from datetime import datetime
from tkinter import *
from tkinter import messagebox, filedialog, simpledialog, font
from tkinter import ttk
from tkinter.ttk import Combobox

import PIL
import cv2
import numpy as np
import pandas as pd
import requests
from PIL import Image, ImageTk
from PIL.Image import fromarray
from bs4 import BeautifulSoup
from ttkwidgets import TickScale


def check_start():
    if not os.path.exists('images'):
        os.mkdir('images')
    if not os.path.exists('database'):
        os.mkdir('database')
    if not os.path.exists('database.csv'):
        pd.DataFrame(columns=df_columns).to_csv('database.csv', index=None)
    x = []
    [x.extend(value) for value in courses_dict.values()]
    for branch in x:
        if not os.path.exists(f'images/{branch}'):
            os.mkdir(f'images/{branch}')
            for year in ['I Year', 'II Year', 'III Year', 'IV Year', 'PhD']:
                os.mkdir(f'images/{branch}/{year}')
        if not os.path.exists(f'database/{branch}.xlsx'):
            df1 = pd.DataFrame(columns=save_columns)
            with pd.ExcelWriter(f'database/{branch}.xlsx') as writer:
                for i in range(1, 6):
                    df1.to_excel(writer, sheet_name=f'Sheet{i}', index=None)


class Conditions:
    def __init__(self):
        self.function = {'Register No.': self.reg_no,
                         'Name of the Student (In Capital Letters only eg. NANDHA KUMAR)': self.name,
                         'Parent\'s Name': self.name,
                         'Roll No.': self.roll_no,
                         'Date of Birth ': self.dob,
                         'Blood Group': self.blood_group,
                         'Pincode': self.pin_code,
                         # 'State': self.state,
                         'Mobile Number(Student)': lambda x: self.number(x, 'Student Contact Number'),
                         'Mobile Number(Parent)': lambda x: self.number(x, 'Parent Contact Number'),
                         'Gender': self.gender,
                         'Student\'s Initial': self.name
                         }

    def reg_no(self, reg_no):
        if reg_no == '' or reg_no == '######':
            return '######'
        # if reg_no[:2].isnumeric() and reg_no[2].isalpha() and reg_no[-3:].isnumeric():
        #     return reg_no.upper()
        if reg_no.isalnum():
            return reg_no.upper()
        messagebox.showerror(
            "Error", "Register Number format is wrong, please re-enter.")

    def name(self, name):
        name = re.sub(rf"[{string.punctuation}]", " ", name)
        name = re.sub(rf"\s\s+", " ", name)
        return name.upper().strip()

    def roll_no(self, roll_no):
        if roll_no.isalnum():
            return roll_no.upper()
        messagebox.showerror(
            "Error", "Register Number format is wrong, please re-enter.")

    def dob(self, dob):
        cleaned = re.sub(rf"[{string.punctuation}]", "/", dob)
        date, month, year = cleaned.split('/')
        if len(date) == 2 and len(month) == 2 and len(year) == 4:
            try:
                date, month, year = map(int, cleaned.split('/'))
                day_count_for_month = [0, 31, 28, 31,
                                       30, 31, 30, 31, 31, 30, 31, 30, 31]
                if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                    day_count_for_month[2] = 29
                if 1 <= month <= 12 and 1 <= date <= day_count_for_month[month] and year > 1800:
                    return cleaned
            except ValueError:
                pass
        messagebox.showerror(
            "Error", "DOB should be in dd-mm-yyyy format & Year > 1800, please re-enter.")

    def blood_group(self, blood_group):
        if blood_group in blood_groups:
            return blood_group
        messagebox.showerror(
            "Error", "Selected Blood Group is not valid, please select again.")

    def pin_code(self, pin_code):
        pin_code = pin_code.lstrip('0')
        if pin_code.isnumeric() and len(pin_code) == 6:
            return pin_code
        messagebox.showerror(
            "Error", "Pin Code should contain only 6 digits, please re-enter.")

    def state(self, state):
        if state in indian_states:
            return state
        messagebox.showerror(
            "Error", "Selected state is not valid, please select again.")

    def number(self, number, type_):
        if number.isnumeric() and len(number.lstrip('0')) == 10:
            if type_ == 'Parent Contact Number' and number == variables['Mobile Number(Student)'].get():
                messagebox.showerror(
                    "Error", "Student contact and parent contact must be different.")
                return
            return number
        messagebox.showerror(
            "Error", f"{type_} should contain only 10 digits, please re-enter.")

    def gender(self, gender):
        if gender in ['Male', 'Female', 'Transgender']:
            return gender
        messagebox.showerror("error", "Please select Valid Gender")

    def address_1(self):
        name = variables["Name of the Student (In Capital Letters only eg. NANDHA KUMAR)"].get(
        )
        parent = variables["Parent\'s Name"].get()
        if variables['Gender'].get() == 'Female':
            return f'D/o. {parent}'
        else:
            return f'S/o. {parent}'

    def test_case(self, test_type, test_var):
        return self.function.get(test_type, lambda x: x)(test_var)


IMAGE_EDITED_FLAG = False
flag = False
input_flag = False
camera_accessible = True
df_columns = ['Register No.', 'Name of the Student (In Capital Letters only eg. NANDHA KUMAR)', 'Student\'s Initial',
              'Roll No.', 'Date of Birth ', 'Course', 'Branch',
              'Blood Group', 'Gender', 'Parent\'s Name', 'Parent\'s Occupation', 'Address line2(Area/Landmark)',
              'Address line1(Door No. & Street Name)',
              'City/Town/Village', 'Pincode', 'State', 'Mobile Number(Student)', 'Mobile Number(Parent)', 'Year']

save_columns = ['Register No.', 'Name', 'Roll No.', 'Date of Birth', 'Course', 'Branch',
                'Blood Group', 'Gender', 'Address Line 1', 'Address Line 2', 'Address Line 3',
                'Address Line 4', 'Mobile Number(Student)', 'Mobile Number(Parent)']

indian_states = ['Tamil Nadu', 'Andaman and Nicobar (UT)', 'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar',
                 'Chandigarh (UT)', 'Chhattisgarh', 'Dadra and Nagar Haveli (UT)', 'Daman and Diu (UT)',
                 'Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Jharkhand',
                 'Karnataka', 'Kerala', 'Lakshadweep (UT)', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
                 'Meghalaya', 'Mizoram', 'Nagaland', 'Orissa', 'Puducherry (UT)', 'Punjab', 'Rajasthan',
                 'Sikkim', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
                 ]

blood_groups = ['O +ve', 'A +ve', 'B +ve', 'AB +ve', 'O -ve', 'A -ve', 'B -ve', 'AB -ve',
                'A1 +ve', 'A1 -ve', 'A2 +ve', 'A2 -ve', 'A1B +ve', 'A1B -ve', 'A2B +ve', 'A2B -ve']
defaults_ = {
    'Blood Group': 'Blood Group',
    'Gender': 'Gender',
    'Parent\'s Occupation': 'Parent Occupation',
    'State': 'State',
}

courses_dict = {
    'B.E.': ['Civil  Engg.', 'Mechanical  Engg.', 'Electrical and Electronics  Engg.',
             'Electronics & Commn  Engg.', 'Computer Science & Engg.', 'Mechatronics'],
    'B.Tech': ['Information Technology', 'Computer Sci & Business Systems'],
    'B.Arch': ['Architecture'],
    'M.E': ['Communication Systems', 'Structural Engg.', 'Computer Science & Engg.',
            'Environmental Engg.', 'Infrastructure Engg. & Management', 'Power System Engg.'],
    'M.Arch': ['Architecture'],
    'M.Sc.': ['Data Science'],
    'MCA': ['Master of Computer Appln.'],
    'PhD': ['Civil  Engg.', 'Mechanical  Engg.', 'Electrical and Electronics  Engg.',
            'Electronics & Commn  Engg.', 'Computer Science & Engg.', 'Mechatronics',
            'Information Technology', 'Architecture', 'Chemistry', 'Physics', 'Mathematics', 'English'],
}

year_dict = {
    1: 'I year',
    2: 'II year',
    3: 'III year',
    4: 'IV year',
    5: 'PhD'
}

img_formats = {
    0: '.jpg',
    1: '.bmp',
}

year_reverse_dict = {value: key for key, value in year_dict.items()}

width, height = 190, 170
for source_no in reversed(range(0, 5)):
    cap = cv2.VideoCapture(source_no, cv2.CAP_DSHOW)
    if cap.read()[1] is not None:
        break
    cap.release()
check_start()
main_file = pd.read_csv('database.csv', converters={i: str for i in range(0, 100)})
main_file['Roll No.'] = main_file['Roll No.'].apply(str)
captured_pic = False
captured_pic_edit = False
test = Conditions().test_case


def update_course_list():
    global entry8
    selected = variables['Course'].get()
    branches = courses_dict.get(selected, [])
    entry8['values'] = branches


def set_preview_frame(img):
    global preview_frame

    img = cv2.resize(img, (120, 170))
    img = fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGBA))
    imgtk = ImageTk.PhotoImage(image=img)
    preview_frame.imgtk = imgtk
    preview_frame.configure(image=imgtk)


def refresh(refresh_all=False):
    global captured_pic
    for var in list(variables.keys()):
        if not refresh_all and (var == 'Student\'s Initial' or
                                var == 'Roll No.' or var == 'Name of the Student (In Capital Letters only eg. NANDHA KUMAR)'):
            continue
        if var in defaults_:
            if variables[var].get() != defaults_[var]:
                variables[var].set(defaults_[var])
            continue
        variables[var].set('')
    if preview_frame.imgtk is not empty_image:
        preview_frame.imgtk = empty_image
        preview_frame.configure(image=empty_image)
    captured_pic = False


def create_new_branch(branch):
    if not os.path.exists(f'images/{branch}'):
        os.mkdir(f'images/{branch}')
        for year in ['I Year', 'II Year', 'III Year', 'IV Year', 'PhD']:
            os.mkdir(f'images/{branch}/{year}')
    if not os.path.exists(f'database/{branch}.xlsx'):
        df1 = pd.DataFrame(columns=save_columns)
        with pd.ExcelWriter(f'database/{branch}.xlsx') as writer:
            for i in range(1, 6):
                df1.to_excel(writer, sheet_name=f'Sheet{i}', index=None, engine='openpyxl')


def thread_bg():
    global entry0, IMAGE_EDITED_FLAG, captured_pic
    while True:
        update_course_list()
        entered = variables['Roll No.'].get()
        if len(entered) < 3:
            refresh()
        selected = sorted(
            [x for x in main_file['Roll No.'] if x.startswith(entered)])
        entry0['values'] = selected
        if cv2.getWindowProperty('sunset', cv2.WND_PROP_VISIBLE) < 1:
            if IMAGE_EDITED_FLAG:
                set_preview_frame(captured_pic_edit)
                IMAGE_EDITED_FLAG = False
                captured_pic = captured_pic_edit
        time.sleep(0.5)


def show_frame():
    global flag, captured_pic, camera_accessible
    _, frame = cap.read()
    # frame = cv2.flip(frame, 1)
    if not camera_accessible:
        return
    try:
        orig_frame = frame.copy()
    except:
        messagebox.showerror("Error",
                             "Unable to access Camera. Please attach camera/close the app in task manager and restart the app.")
        camera_accessible = False
        return
    frame = cv2.resize(frame, (width, height))
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    x, y, w, h = 45, 10, 100, 150
    shape = [(x, y), (x + w, y + h)]
    if flag:
        img = fromarray(cv2.resize(
            cv2image[y:y + h, x:x + w], (120, 170)))
        imgtk = ImageTk.PhotoImage(image=img)
        preview_frame.imgtk = imgtk
        preview_frame.configure(image=imgtk)
        frame_height, frame_width, _ = orig_frame.shape
        actual = list(map(int, [(x / width) * frame_width, ((x + w) / width) *
                                frame_width, (y / height) * frame_height, ((y + h) / height) * frame_height]))
        captured_pic = cv2.resize(
            orig_frame[actual[2]:actual[3], actual[0]:actual[1]], (480, 640))
        flag = False
    cv2.rectangle(cv2image, shape[0], shape[1], (220, 243, 0), 2)
    img = fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    video_frame.imgtk = imgtk
    video_frame.configure(image=imgtk)
    video_frame.after(10, show_frame)


def capture_pic():
    global flag
    flag = True


def register():
    global main_file
    data = {x: variables[x].get() for x in df_columns}

    # Add year data TODO: Refactor it
    data['Year'] = year_dict[setting_obj.year.get()]

    if data['Register No.'] == '':
        data['Register No.'] = '######'
    if not all(list(data.values())):
        messagebox.showerror("Error", "Please fill all the details.")
        return
    if not str(type(captured_pic)) == "<class 'numpy.ndarray'>":
        messagebox.showerror("Error", "Please capture picture.")
        return

    # print('data_before\n', data)
    for test_type in df_columns:
        data[test_type] = test(test_type, data[test_type])
        if not data[test_type]:
            return
    # print('Data After:\n', data)

    branch = variables['Branch'].get()
    selected = variables['Course'].get()
    branches = courses_dict.get(selected, [])
    if branch != '' and branch not in branches:
        create_new_branch(branch)

    department_file_path = f'database/{variables["Branch"].get()}.xlsx'
    sheet_name = f'Sheet{setting_obj.year.get()}'
    department_file = pd.read_excel(department_file_path, sheet_name=sheet_name, engine='openpyxl')
    department_file['Roll No.'] = department_file['Roll No.'].apply(str)
    department_file_format = {
        'Register No.': data['Register No.'],
        'Name': data['Student\'s Initial'] + '. ' + data[
            'Name of the Student (In Capital Letters only eg. NANDHA KUMAR)'],
        'Roll No.': data['Roll No.'],
        'Date of Birth': data['Date of Birth '],
        'Course': data['Course'],
        'Branch': data['Branch'],
        'Blood Group': data['Blood Group'],
        'Gender': data['Gender'],
        'Address Line 1': Conditions().address_1(),
        'Address Line 2': data['Address line1(Door No. & Street Name)'],
        'Address Line 3': data['Address line2(Area/Landmark)'],
        'Address Line 4': f"{data['City/Town/Village']} - {data['Pincode']}, {data['State']}",
        'Mobile Number(Student)': data['Mobile Number(Student)'],
        'Mobile Number(Parent)': data['Mobile Number(Parent)'],
    }

    # print("Department Save data:\n", department_file_format)
    main_file_temp = pd.read_csv('database.csv')
    main_file_temp['Roll No.'] = main_file_temp['Roll No.'].apply(str)
    # For Debugging
    # print(main_file_temp['Roll No.'] == variables['Roll No.'].get())
    # print(main_file_temp['Roll No.'], variables['Roll No.'].get())

    if any(main_file_temp['Roll No.'] == variables['Roll No.'].get()):
        main_file_temp.loc[main_file_temp['Roll No.'] == variables['Roll No.'].get()] = [data[x]
                                                                                         for x in df_columns]
        # TODO: If department changes we have to delete previous entry
        department_file.loc[department_file['Roll No.'] == variables['Roll No.'].get()] = [department_file_format[x] for
                                                                                           x in save_columns]
    else:
        reg_no_temp = variables['Register No.'].get()
        # If the register number already exists in database, it is wrong
        if any(department_file['Register No.'] == reg_no_temp) and [x for x in reg_no_temp if x in '1234567890']:
            messagebox.showerror("Error", "Register Number already exists in database. Please change.")
            return
        main_file_temp.loc[len(main_file_temp)] = [data[x] for x in df_columns]
        department_file.loc[len(department_file)] = [
            department_file_format[x] for x in save_columns]
    try:
        sheets = [pd.read_excel(department_file_path, sheet_name=f'Sheet{i}', engine='openpyxl') for i in range(1, 6)]
        sheets[setting_obj.year.get() - 1] = department_file
        with pd.ExcelWriter(department_file_path) as writer:
            for i, df_temp in zip(range(1, 6), sheets):
                df_temp.to_excel(writer, sheet_name=f'Sheet{i}', index=None)

    except PermissionError:
        messagebox.showerror(
            "Save Error", "Unable to write to file. Please close the excel sheet.")
        return
    main_file_temp.to_csv('database.csv', index=None)

    image_save_path = f'images/{variables["Branch"].get()}/{year_dict[setting_obj.year.get()]}/{variables["Roll No."].get()}'
    cv2.imwrite(image_save_path + img_formats[int(setting_obj.option.get())], captured_pic)
    messagebox.showinfo("Success", "Data Updated Successfully!")

    if not input_flag:
        main_file = pd.read_csv('database.csv')
        main_file['Roll No.'] = main_file['Roll No.'].apply(str)


def update_all_fields(something, query_type='Roll No.'):
    global captured_pic
    if not variables[query_type].get():
        return
    row = main_file[main_file[query_type] == variables[query_type].get()]
    for x in df_columns:
        # TODO: Refactor
        if x == 'Year':
            continue
        variables[x].set(row[x].values[0])

    # TODO: Refactor year setting
    setting_obj.year.set(year_reverse_dict[row['Year'].values[0]])

    image_save_path = f'images/{variables["Branch"].get()}/{year_dict[setting_obj.year.get()]}/{variables["Roll No."].get()}'

    captured_pic = cv2.imread(image_save_path + '.jpg')

    if captured_pic is None:
        captured_pic = cv2.imread(image_save_path + '.bmp')

    if captured_pic is None:
        return

    img = fromarray(captured_pic[..., ::-1])
    img = img.resize((120, 170))
    imgtk = ImageTk.PhotoImage(image=img)
    preview_frame.imgtk = imgtk
    preview_frame.configure(image=imgtk)


def fetch():
    roll_no = variables["Roll No."].get()
    name = variables["Name of the Student (In Capital Letters only eg. NANDHA KUMAR)"].get(
    )
    if roll_no:
        if roll_no in list(main_file['Roll No.']):
            update_all_fields('', query_type='Roll No.')
        elif name:
            if name not in list(main_file['Name of the Student (In Capital Letters only eg. NANDHA KUMAR)']):
                messagebox.showinfo(
                    "Not Found", "Name not found. Please register.")
                return
            update_all_fields(
                '', query_type='Name of the Student (In Capital Letters only eg. NANDHA KUMAR)')
        else:
            messagebox.showinfo(
                "Not Found", "Register number not found. Please register.")
            return


class Settings:
    def __init__(self):
        self.option = IntVar()
        self.option.set(0)
        self.year = IntVar()
        self.year.set(1)
        self.report_department = StringVar()

    def popup(self):
        win = Toplevel()
        win.geometry("420x281")
        win.configure(bg="#e1dfe1")
        win.wm_title("Options")
        canvas_settings = Canvas(
            win,
            bg="#e1dfe1",
            height=281,
            width=377,
            bd=0,
            highlightthickness=0,
            relief="ridge")
        canvas.place(x=0, y=0)
        img0 = PhotoImage(file=f"app_files/settings_img0.png")
        b0 = Button(
            win,
            image=img0,
            borderwidth=0,
            highlightthickness=0,
            command=self.select_file,
            relief="flat")

        b0.place(
            x=96, y=59,
            width=184,
            height=56)
        Label(win, text='Image Format: ').place(x=50, y=130)
        Radiobutton(win, text="jpg", variable=self.option,
                    value=0).place(x=160, y=130)
        Radiobutton(win, text="bmp", variable=self.option,
                    value=1).place(x=250, y=130)

        Label(win, text='Year: ').place(x=50, y=190)
        Radiobutton(win, text="I Year", variable=self.year,
                    value=1).place(x=160, y=180)
        Radiobutton(win, text="II Year", variable=self.year,
                    value=2).place(x=250, y=180)
        Radiobutton(win, text="III Year", variable=self.year,
                    value=3).place(x=160, y=210)
        Radiobutton(win, text="IV Year", variable=self.year,
                    value=4).place(x=250, y=210)
        Radiobutton(win, text="PhD", variable=self.year,
                    value=5).place(x=160, y=240)

        background_img = PhotoImage(file=f"app_files/settings_background.png")
        background = canvas.create_image(
            win,
            99.0, 50.0,
            image=background_img)

    # def generate_report(self):
    #     # TODO: GenerateReport
    #     required = main_file[main_file['Branch']
    #                          == self.report_department.get()]
    #     has_photo = []
    #     for row in required.iterrows():
    #         row = row[1]
    #         path_img = f"images/{row['Branch']}/{row['Roll No.']}.jpg"
    #         if os.path.exists(path_img) or os.path.exists(path_img.replace('jpg', 'bmp')):
    #             has_photo.append('Yes')
    #         else:
    #             has_photo.append('No')
    #     required['has_photo'] = has_photo
    #     if len(required):
    #         report_out_path = filedialog.asksaveasfilename()
    #         required.to_csv(report_out_path.rstrip(
    #             '.csv') + '.csv', index=None)
    #         messagebox.showinfo(
    #             f"{len(required)} entries Found", "Successfully exported.")
    #     else:
    #         messagebox.showinfo("No entries Found",
    #                             "No entries found for the selected branch.")

    def remove_decimal(self, val):
        try:
            return str(int(val))
        except ValueError:
            return str(val)

    def select_file(self):
        global main_file, input_flag
        input_path = filedialog.askopenfilename()
        data_ = pd.read_excel(input_path, engine='openpyxl')
        cols = list(data_.columns)

        # TODO: REFACTOR!!
        df_columns1 = df_columns[:]
        df_columns1.remove('Year')

        if not all([x in cols for x in df_columns1]):
            messagebox.showerror(
                "File Read Error",
                f"Column headers do not match the required format. Missing: {', '.join([x for x in df_columns if x not in cols])}")
            return
        main_file['Pincode'] = main_file['Pincode'].apply(self.remove_decimal)
        main_file['Mobile Number(Student)'] = main_file['Mobile Number(Student)'].apply(
            self.remove_decimal)
        main_file['Mobile Number(Parent)'] = main_file['Mobile Number(Parent)'].apply(
            self.remove_decimal)
        data_['Roll No.'] = data_['Roll No.'].apply(self.remove_decimal)
        data_['Date of Birth '] = data_['Date of Birth '].apply(str)
        data_ = data_.fillna('')
        data_['Date of Birth '] = data_['Date of Birth '].apply(
            lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"))
        main_file = data_
        input_flag = True
        messagebox.showinfo("Load Successful", "File Read Successfully!")


class GoogleSync:
    def __init__(self):
        self.top = Tk()
        self.listbox = Listbox(self.top)
        self.add_btn = Button(self.top, text="+", command=self.add_link, bg='#2194f3', fg='#FFFFFF')
        self.delete_btn = Button(self.top, text="-", command=self.delete_link, bg='#2194f3', fg='#FFFFFF')
        self.select_btn = Button(self.top, text="Select Sheet", command=lambda: self.select_link(sync=False),
                                 bg='#2194f3', fg='#FFFFFF')
        self.select_n_sync_btn = Button(self.top, text="Sync Sheet", command=self.select_link, bg='#2194f3',
                                        fg='#FFFFFF')

        self.adb_color = font.Font(family='Courier', size=30, weight='bold')
        self.select_color = font.Font(family='Courier', size=5, weight='bold')

        self.df_path = 'database/sync_links.csv'

        self.configure()
        self.df = pd.read_csv(self.df_path)

        self.start()

    def start(self):
        self.top.mainloop()

    def configure(self):
        if not os.path.exists('database/sync'):
            os.mkdir('database/sync')

        self.top.geometry("400x450")
        self.top.configure(bg='#e1dfe1')
        self.top.wm_title('Google Sheets')

        self.listbox.place(x=50, y=20, width=300, height=350)
        self.add_btn.place(x=360, y=100, width=30, height=30)
        self.delete_btn.place(x=360, y=200, width=30, height=30)
        self.select_btn.place(x=50, y=380, width=120, height=30)
        self.select_n_sync_btn.place(x=225, y=380, width=120, height=30)

        self.add_btn['font'] = self.adb_color
        self.delete_btn['font'] = self.adb_color
        self.select_btn['font'] = self.select_color
        self.select_n_sync_btn['font'] = self.select_color

        if not os.path.exists(self.df_path):
            pd.DataFrame(columns=['titles', 'links']).to_csv(self.df_path, index=False)

        self.update_listbox()

    def add_link(self):
        link = simpledialog.askstring(title="Add Sheet",
                                      prompt="Enter the Google Sheets Link.", parent=self.top)
        try:
            title = BeautifulSoup(requests.get(link).content, 'html.parser').title.text

            csv_link = link.replace('pubhtml', 'pub?output=csv')
            data = pd.read_csv(csv_link)

            title = title.replace('- Google Drive', '').strip()

            if title not in self.df['titles']:
                self.df.loc[len(self.df)] = [title, link]
                self.df.to_csv(self.df_path, index=False)
            data.to_csv(f'database/sync/{title}.csv', index=False)
            self.listbox.insert(self.listbox.size(), title)

        except requests.exceptions.MissingSchema:
            if not link:
                return
            messagebox.showerror('Enter Valid Link.')
        except pd.errors.ParserError:
            messagebox.showerror('Please publish to web and select webpage option.')
        except (urllib.error.URLError, socket.gaierror):
            messagebox.showerror("Couldn't connect to the Internet")

    def delete_link(self):
        self.df = self.df[self.df.titles != self.listbox.get(ANCHOR)]
        if os.path.exists(f'database/sync/{self.listbox.get(ANCHOR)}.csv'):
            os.remove(f'database/sync/{self.listbox.get(ANCHOR)}.csv')
        self.listbox.delete(ANCHOR)
        self.df.to_csv(self.df_path, index=False)

    def select_link(self, sync=True):
        title = self.listbox.get(ANCHOR)
        if sync:
            try:
                link = self.df[self.df.titles == title]['links'].values[0]
                csv_link = str(link).replace('pubhtml', 'pub?output=csv')
                data_ = pd.read_csv(csv_link, converters={i: str for i in range(0, 100)})
                data_.to_csv(f'database/sync/{title}.csv', index=False)
            except (urllib.error.URLError, socket.gaierror):
                messagebox.showerror("No Internet", "Couldn't connect to the Internet. Please check your connection.")
                self.top.destroy()
                return

        data_ = pd.read_csv(f'database/sync/{title}.csv', converters={i: str for i in range(0, 100)})

        global main_file, input_flag
        cols = list(data_.columns)

        # TODO: REFACTOR!!
        df_columns1 = df_columns[:]
        df_columns1.remove('Year')
        if not all([x in cols for x in df_columns1]):
            messagebox.showerror(
                "File Read Error",
                f"Column headers do not match the required format. Missing: {', '.join([x for x in df_columns if x not in cols])}")
            return
        data_['Pincode'] = data_['Pincode'].apply(self.remove_decimal)
        data_['Mobile Number(Student)'] = data_['Mobile Number(Student)'].apply(
            self.remove_decimal)
        data_['Mobile Number(Parent)'] = data_['Mobile Number(Parent)'].apply(
            self.remove_decimal)
        data_['Roll No.'] = data_['Roll No.'].apply(self.remove_decimal)
        data_['Date of Birth '] = data_['Date of Birth '].apply(str)
        data_ = data_.fillna('')
        data_['Date of Birth '] = data_['Date of Birth '].apply(
            lambda x: datetime.strptime(x, "%d/%m/%Y").strftime("%d/%m/%Y"))
        main_file = data_
        input_flag = True
        messagebox.showinfo("Load Successful", "File Read Successfully!")
        self.top.destroy()

    def remove_decimal(self, val):
        try:
            return str(int(val))
        except ValueError:
            return str(val)

    def update_listbox(self):
        self.df = pd.read_csv(self.df_path)
        for index, row in self.df.iterrows():
            self.listbox.insert(index, row['titles'])


# class EditImageWindow:
#     def __init__(self):
#         global STOP_EDIT_FLAG
#         STOP_EDIT_FLAG = False
#         self.t1 = threading.Thread(target=self.image_edit_thread)
#
#         self.top = Toplevel()
#
#         self.img_slider = PhotoImage('img_slider', width=30, height=15, master=self.top)
#         self.set_img_color(self.img_slider, "#ff0000")
#         self.img_slider_active = PhotoImage('img_slider_active', width=30, height=15, master=self.top)
#         self.set_img_color(self.img_slider_active, '#1065BF')
#
#         self.brightness_scale = self.create_tick_scale(35)
#         self.contrast_scale = self.create_tick_scale(35)
#         self.hue_scale = self.create_tick_scale(10)
#         self.sat_scale = self.create_tick_scale(35)
#         # self.image = cv2.resize(cv2.imread('pras.jpg'), (320, 240))
#         img_size = (240, 320)
#         self.image = cv2.resize(captured_pic, img_size[::-1])
#         im = ImageTk.PhotoImage(fromarray(self.image[..., ::-1]))
#         self.preview_frame = Label(self.top, image=im)
#         self.preview_frame.imgtk = im
#         self.preview_frame.place(x=125, y=270,
#                                  width=img_size[0],
#                                  height=img_size[1])
#
#         self.configure()
#         self.top.protocol("WM_DELETE_WINDOW", self.stop_edit)
#         self.top.mainloop()
#
#     def create_tick_scale(self, x):
#         scale = TickScale(self.top, from_=-x, to=x, tickinterval=x, orient="horizontal",
#                           style='custom.Horizontal.TScale', length=300)
#         scale.set(0)
#         return scale
#
#     def configure(self):
#         """
#         Source: https://stackoverflow.com/questions/59642558/how-to-set-tkinter-scale-sliders-color
#         """
#         self.top.geometry("450x600")
#         self.top.title('Image Adjustment')
#         self.top.configure(background='#f4f0ec')
#         self.t1.start()
#
#         style = ttk.Style(self.top)
#         style.theme_use('clam')
#         style.element_create('custom.Horizontal.Scale.slider', 'image', self.img_slider,
#                              ('active', self.img_slider_active))
#         style.layout('custom.Horizontal.TScale',
#                      [('Horizontal.Scale.trough',
#                        {'sticky': 'nswe',
#                         'children': [('custom.Horizontal.Scale.slider',
#                                       {'side': 'left', 'sticky': ''})]})])
#         style.configure('custom.Horizontal.TScale', background='#f4f0ec', foreground='#880000',
#                         troughcolor='#73B5FA')
#
#         Label(self.top, text='Brightness').place(x=10, y=20)
#         self.brightness_scale.place(x=100, y=0)
#
#         Label(self.top, text='Contrast').place(x=10, y=80)
#         self.contrast_scale.place(x=100, y=60)
#
#         Label(self.top, text='Hue').place(x=10, y=140)
#         self.hue_scale.place(x=100, y=120)
#
#         Label(self.top, text='Saturation').place(x=10, y=200)
#         self.sat_scale.place(x=100, y=180)
#
#     def adjust_all(self, image):
#         adjust = self.adjust_brightness(self.image, self.brightness)
#         adjust = self.adjust_contrast(adjust, self.contrast)
#         adjust = self.adjust_hue(adjust, self.hue)
#         adjust = self.adjust_sat(adjust, self.sat)
#         return adjust
#
#     def image_edit_thread(self):
#         brightness, contrast, hue, sat = [0] * 4
#         while True:
#             if STOP_EDIT_FLAG:
#                 print('THREAD TERMINATE SIG')
#                 break
#             if brightness != self.brightness or contrast != self.contrast or hue != self.hue or sat != self.sat:
#                 adjust = self.adjust_all(self.image)
#                 brightness = self.brightness
#                 contrast = self.contrast
#                 hue = self.hue
#                 sat = self.sat
#                 self.update_image(adjust)
#             time.sleep(0.5)
#
#     def update_image(self, image):
#         image = ImageTk.PhotoImage(fromarray(image[..., ::-1]))
#         self.preview_frame.imgtk = image
#         self.preview_frame.configure(image=image)
#
#     def stop_edit(self):
#         global STOP_EDIT_FLAG
#         STOP_EDIT_FLAG = True
#         self.t1.join()
#         self.top.destroy()
#
#     @staticmethod
#     def set_img_color(img, color):
#         pixel_line = "{" + " ".join(color for i in range(img.width())) + "}"
#         pixels = " ".join(pixel_line for i in range(img.height()))
#         img.put(pixels)
#
#     @staticmethod
#     def adjust_brightness(img, brightness):
#         brightness += 255
#         brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))
#         cal = img.copy()
#         if brightness != 0:
#             if brightness > 0:
#                 shadow = brightness
#                 max = 255
#             else:
#                 shadow = 0
#                 max = 255 + brightness
#             alpha = (max - shadow) / 255
#             gamma = shadow
#             cal = cv2.addWeighted(img, alpha,
#                                   img, 0, gamma)
#         return cal
#
#     @staticmethod
#     def adjust_contrast(img, contrast):
#         contrast += 127
#         contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127))
#         cal = img.copy()
#         if contrast != 0:
#             alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
#             gamma = 127 * (1 - alpha)
#             cal = cv2.addWeighted(cal, alpha, cal, 0, gamma)
#         return cal
#
#     @staticmethod
#     def adjust_hue(img, hue):
#         cal = img.copy()
#         cal = cv2.cvtColor(cal, cv2.COLOR_BGR2HSV)
#         h, s, i = cv2.split(cal)
#         h = h.astype(np.float64)
#         h = h + int(hue)
#         h[h < 0] += 180
#         h[h > 180] -= 180
#         h = h.astype(np.uint8)
#         cal = cv2.merge([h, s, i])
#         return cv2.cvtColor(cal, cv2.COLOR_HSV2BGR)
#
#     @staticmethod
#     def adjust_sat(img, sat):
#         cal = img.copy()
#         cal = cv2.cvtColor(cal, cv2.COLOR_BGR2HSV)
#         h, s, i = cv2.split(cal)
#         s = s.astype(np.float64)
#         # s = s + int(sat)
#         # s[s < 0] = 0
#         sat += 100
#         s_shift = (sat - 100) / 100.0
#         s = s + 255.0 * s_shift
#         s[s < 0] = 0
#         s[s > 255] = 255
#         s = s.astype(np.uint8)
#         cal = cv2.merge([h, s, i])
#         return cv2.cvtColor(cal, cv2.COLOR_HSV2BGR)
#
#     @property
#     def brightness(self):
#         return self.brightness_scale.get()
#
#     @property
#     def contrast(self):
#         return self.contrast_scale.get()
#
#     @property
#     def hue(self):
#         return self.hue_scale.get()
#
#     @property
#     def sat(self):
#         return self.sat_scale.get()

class EditImageWindow:
    def __init__(self):
        self.img = cv2.resize(captured_pic, (240 * 2, 320 * 2))
        self.main()

    def adjust_image(self, brightness=0):
        global captured_pic, captured_pic_edit, IMAGE_EDITED_FLAG
        try:
            brightness = cv2.getTrackbarPos('Brightness', 'EDIT')
            contrast = cv2.getTrackbarPos('Contrast', 'EDIT')
            hue = cv2.getTrackbarPos('Hue', 'EDIT')
            sat = cv2.getTrackbarPos('Saturation', 'EDIT')
        except:
            cv2.imshow('EDIT', self.img)
            return

        effect = self.controller(self.img, brightness,
                                 contrast, hue, sat)
        captured_pic_edit = self.controller(captured_pic, brightness,
                                 contrast, hue, sat)
        IMAGE_EDITED_FLAG = True

        cv2.imshow('EDIT', effect)

    @staticmethod
    def controller(img, brightness, contrast, hue, sat):
        brightness += 255 - 35
        contrast += 127 - 35
        hue -= 10
        sat -= 35

        brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))
        cal = img.copy()

        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                max = 255
            else:
                shadow = 0
                max = 255 + brightness
            alpha = (max - shadow) / 255
            gamma = shadow
            cal = cv2.addWeighted(img, alpha,
                                  img, 0, gamma)

        contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127))
        if contrast != 0:
            alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
            gamma = 127 * (1 - alpha)
            cal = cv2.addWeighted(cal, alpha, cal, 0, gamma)

        cal = cv2.cvtColor(cal, cv2.COLOR_BGR2HSV)
        h, s, i = cv2.split(cal)
        h = h.astype(np.float64)
        h = h + int(hue)
        h[h < 0] += 180
        h[h > 180] -= 180
        h = h.astype(np.uint8)

        s = s.astype(np.float64)
        s_shift = sat / 100.0
        s = s + 255.0 * s_shift
        s[s < 0] = 0
        s[s > 255] = 255
        s = s.astype(np.uint8)
        cal = cv2.merge([h, s, i])
        cal = cv2.cvtColor(cal, cv2.COLOR_HSV2BGR)

        return cal

    def main(self):
        cv2.namedWindow('EDIT', cv2.WINDOW_NORMAL)
        cv2.imshow('EDIT', self.img)

        cv2.createTrackbar('Brightness',
                           'EDIT', 35, 2 * 35,
                           self.adjust_image
                           )

        cv2.createTrackbar('Contrast', 'EDIT',
                           35, 2 * 35,
                           self.adjust_image
                           )

        cv2.createTrackbar('Hue', 'EDIT',
                           10, 2 * 10,
                           self.adjust_image
                           )

        cv2.createTrackbar('Saturation', 'EDIT',
                           35, 2 * 35,
                           self.adjust_image
                           )
        cv2.waitKey(0)

        def __del__(self):
            global IMAGE
            print('exiting...')
            IMAGE = self.image


window = Tk()
window.title('ID Card App')
variables = {x: StringVar() for x in df_columns}
empty_image = ImageTk.PhotoImage(
    Image.new('RGB', (width, height), (244, 240, 236)))
setting_obj = Settings()

window.geometry("1197x700")
window.configure(bg="#f4f0ec")
canvas = Canvas(
    window,
    bg="#f4f0ec",
    height=700,
    width=1197,
    bd=0,
    highlightthickness=0,
    relief="ridge")
canvas.place(x=0, y=0)
video_frame = Label()
video_frame.place(x=73, y=300,
                  width=width,
                  height=height)

preview_frame = Label()
preview_frame.imgtk = empty_image
preview_frame.place(x=420, y=305,
                    width=120,
                    height=170)
background_img = PhotoImage(file=f"app_files/background.png")
background = canvas.create_image(
    478.0, 285.0,
    image=background_img)

entry0 = ttk.Combobox(values=main_file['Roll No.'],
                      textvariable=variables['Roll No.'])
entry0.bind("<<ComboboxSelected>>", update_all_fields)

entry0.place(
    x=180.5, y=135,
    width=310.0,
    height=21)

entry1_img = PhotoImage(file=f"app_files/img_textBox1.png")
entry1_bg = canvas.create_image(
    276.0, 185.5,
    image=entry1_img)

entry1 = Entry(
    bd=0,
    bg="#f5f5f5",
    highlightthickness=0,
    textvariable=variables['Name of the Student (In Capital Letters only eg. NANDHA KUMAR)'])

entry1.place(
    x=180.5, y=174,
    width=191.0,
    height=21)

entry2_img = PhotoImage(file=f"app_files/img_textBox2.png")
entry2_bg = canvas.create_image(
    448.0, 185.5,
    image=entry2_img)

entry2 = Entry(
    bd=0,
    bg="#f5f5f5",
    highlightthickness=0,
    textvariable=variables['Student\'s Initial'])

entry2.place(
    x=405.5, y=174,
    width=85.0,
    height=21)

entry5_img = PhotoImage(file=f"app_files/img_textBox5.png")
entry5_bg = canvas.create_image(
    981.5, 148.0,
    image=entry5_img)

entry5 = Entry(
    bd=0,
    bg="#f5f5f5",
    highlightthickness=0,
    textvariable=variables['Register No.'])

entry5.place(
    x=826.0, y=137,
    width=311.0,
    height=20)

entry6_img = PhotoImage(file=f"app_files/img_textBox6.png")
entry6_bg = canvas.create_image(
    981.5, 185.5,
    image=entry6_img)

entry6 = Entry(
    bd=0,
    bg="#f5f5f5",
    highlightthickness=0,
    textvariable=variables['Date of Birth '])

entry6.place(
    x=825.5, y=175,
    width=312.0,
    height=19)

entry7 = Combobox(
    values=list(courses_dict.keys()),
    textvariable=variables['Course']
)

entry7.place(
    x=825.5, y=213,
    width=312.0,
    height=19)

entry8 = Combobox(
    textvariable=variables['Branch'],
)

entry8.place(
    x=826.0, y=250,
    width=311.0,
    height=20)

entry9 = Combobox(
    textvariable=variables['Blood Group'],
    values=blood_groups
)

entry9.place(
    x=826.0, y=288,
    width=135.0,
    height=20)

entry17 = Combobox(
    textvariable=variables['Gender'],
    values=['Gender', 'Male', 'Female', 'Transgender']
)
entry17.current(0)
entry17.place(
    x=998.0, y=288,
    width=139.0,
    height=20)

entry11_img = PhotoImage(file=f"app_files/img_textBox11.png")
entry11_bg = canvas.create_image(
    893.5, 336.5,
    image=entry11_img)

entry11 = Entry(
    bd=0,
    bg="#f5f5f5",
    highlightthickness=0,
    textvariable=variables['Parent\'s Name'])

entry11.place(
    x=825.5, y=326,
    width=136.0,
    height=19)

entry12_img = PhotoImage(file=f"app_files/img_textBox12.png")
entry12_bg = canvas.create_image(
    1067.5, 336.5,
    image=entry12_img)

entry12 = Entry(
    bd=0,
    bg="#f5f5f5",
    highlightthickness=0,
    textvariable=variables['Parent\'s Occupation'])

entry12.place(
    x=997.5, y=326,
    width=140.0,
    height=19)

entry4_img = PhotoImage(file=f"app_files/img_textBox4.png")
entry4_bg = canvas.create_image(
    981.5, 374.0,
    image=entry4_img)

entry4 = Entry(
    bd=0,
    bg="#f5f5f5",
    highlightthickness=0,
    textvariable=variables['Mobile Number(Parent)'])

entry4.place(
    x=826.0, y=363,
    width=311.0,
    height=20)

entry10_img = PhotoImage(file=f"app_files/img_textBox10.png")
entry10_bg = canvas.create_image(
    981.5, 408.5,
    image=entry10_img)

entry10 = Entry(
    bd=0,
    bg="#f5f5f5",
    highlightthickness=0,
    textvariable=variables['Address line1(Door No. & Street Name)']
)

entry10.place(
    x=825.5, y=398,
    width=312.0,
    height=19)

entry13_img = PhotoImage(file=f"app_files/img_textBox13.png")
entry13_bg = canvas.create_image(
    981.5, 446.0,
    image=entry13_img)

entry13 = Entry(
    bd=0,
    bg="#f5f5f5",
    highlightthickness=0,
    textvariable=variables['Address line2(Area/Landmark)']
)

entry13.place(
    x=826.0, y=435,
    width=311.0,
    height=20)

entry16_img = PhotoImage(file=f"app_files/img_textBox16.png")
entry16_bg = canvas.create_image(
    981.5, 484.0,
    image=entry16_img)

entry16 = Entry(
    bd=0,
    bg="#f5f5f5",
    highlightthickness=0,
    textvariable=variables['City/Town/Village'])

entry16.place(
    x=826.0, y=473,
    width=311.0,
    height=20)

entry14_img = PhotoImage(file=f"app_files/img_textBox14.png")
entry14_bg = canvas.create_image(
    893.5, 521.5,
    image=entry14_img)

entry14 = Entry(
    bd=0,
    bg="#f5f5f5",
    highlightthickness=0,
    textvariable=variables['Pincode'])

entry14.place(
    x=825.5, y=511,
    width=136.0,
    height=19)

entry15 = Combobox(
    textvariable=variables['State'],
    values=indian_states
)

entry15.place(
    x=997.5, y=511,
    width=140.0,
    height=19)

entry3_img = PhotoImage(file=f"app_files/img_textBox3.png")
entry3_bg = canvas.create_image(
    981.5, 556.5,
    image=entry3_img)

entry3 = Entry(
    bd=0,
    bg="#f5f5f5",
    highlightthickness=0,
    textvariable=variables['Mobile Number(Student)'])

entry3.place(
    x=825.5, y=546,
    width=312.0,
    height=19)

img0 = PhotoImage(file=f"app_files/img0.png")
b0 = Button(
    image=img0,
    borderwidth=0,
    highlightthickness=0,
    command=capture_pic,
    relief="flat")

b0.place(
    x=120, y=477,
    width=94,
    height=36)

img1 = PhotoImage(file=f"app_files/img1.png")
b1 = Button(
    image=img1,
    borderwidth=0,
    highlightthickness=0,
    command=register,
    relief="flat")

b1.place(
    x=939, y=586,
    width=94,
    height=36)

img2 = PhotoImage(file=f"app_files/img2.png")
b2 = Button(
    image=img2,
    borderwidth=0,
    highlightthickness=0,
    command=fetch,
    relief="flat")

b2.place(
    x=289, y=211,
    width=94,
    height=36)

img3 = PhotoImage(file=f"app_files/img3.png")
b3 = Button(
    image=img3,
    borderwidth=0,
    highlightthickness=0,
    command=setting_obj.popup,
    relief="flat")

b3.place(
    x=509, y=554,
    width=90,
    height=32)

img4 = PhotoImage(file=f"app_files/img4.png")
b4 = Button(
    image=img4,
    borderwidth=0,
    highlightthickness=0,
    command=GoogleSync,
    relief="flat")

b4.place(
    x=360, y=554,
    width=90,
    height=39)

img5 = PhotoImage(file=f"app_files/RefreshButton.png")
b5 = Button(
    image=img5,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: refresh(refresh_all=True),
    relief="flat")
b5.place(
    x=120, y=554,
    width=90,
    height=39)

img6 = PhotoImage(file=f"app_files/preview_button.png")
b6 = Button(
    image=img6,
    borderwidth=0,
    highlightthickness=0,
    command=EditImageWindow,
    relief="flat")

b6.place(
    x=430, y=485,
    width=90,
    height=39)

show_frame()
threading.Thread(target=thread_bg).start()
window.mainloop()
cv2.destroyAllWindows()
