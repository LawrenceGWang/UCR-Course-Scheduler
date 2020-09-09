from tkinter import *
from tkinter import ttk, messagebox, simpledialog, filedialog
import tkinter.font as tkFont
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont
from datetime import *
from scraper import *
import pickle
import concurrent.futures

root = Tk()
root.title('Course Scheduler')
width, height = 1012, 759
posHor = int(root.winfo_screenwidth() / 2 - width / 2)
posVert = int(root.winfo_screenheight() / 2 - height / 2)
root.geometry(f"{width}x{height}+{posHor}+{posVert - 50}")
root.resizable(False, False)
root.withdraw()

background_image = PhotoImage(file='./blank_schedule.png')
notebook = ttk.Notebook(root)
notebook.pack()
finaltab = Canvas(notebook, width=width, height=height, bd=0, highlightthickness=0, relief='ridge')
finaltab.pack(fill=BOTH, expand=True)
finaltab.create_image(0, 0, image=background_image, anchor="nw", tags='bg')
notebook.add(finaltab, text='Final')
final = []
fimage = Image.open('./blank_schedule.png')
fdraw = ImageDraw.Draw(fimage, 'RGBA')
fimagetemp = None


session = rweb_session()
courses, tabs, buttons = [], [], []


class get_term_courses:
    def __init__(self):
        self.master = Toplevel(root)
        self.master.title('Input Term and Courses')
        self.master.geometry("390x335")
        self.master.resizable(False, False)

        fontStyle = tkFont.Font(family="Century Gothic", size=15)
        self.frame = Frame(self.master)
        self.frame.pack()

        """ Get term of classes """
        default_term_text = session.term_codes[0]['description']
        Label(self.frame, text="Course Term\n(Leave blank\nfor latest)", font=fontStyle).grid(row=1, padx=(10, 10))
        self.term_input = Entry(self.frame, width=10, font=fontStyle, fg='grey')
        self.term_input.insert(END, default_term_text)
        self.term_input.grid(row=1, column=1, sticky='ew', padx=(10, 10))
        self.term_input.bind("<FocusIn>", self.focus_in)
        self.term_input.bind("<FocusOut>", lambda event: self.focus_out(event, default_term_text))

        """ Get list of courses to scrape """
        default_course_text = 'AHS007\nPHYS040A\nHIST010\nECON002\nCS010A'
        Label(self.frame, text="Course Codes\n(One per line)", font=fontStyle).grid(row=3, padx=(10, 10))
        self.course_input = Text(self.frame, width=10, height=5, font=fontStyle, fg='grey')
        self.course_input.insert(END, default_course_text)
        self.course_input.grid(row=3, column=1, sticky="nsew", padx=(10, 10))
        self.course_input.bind("<FocusIn>", self.focus_in)
        self.course_input.bind("<FocusOut>", lambda event: self.focus_out(event, default_course_text))

        submit = Button(self.frame, text='Button', font=fontStyle, command=self.submitCmd)
        submit.grid(row=5, column=0, rowspan=2, columnspan=2, sticky='nsew', padx=(10, 10))

        col_count, row_count = self.frame.grid_size()
        for col in range(col_count):
            self.frame.grid_columnconfigure(col, minsize=10)
        for row in range(row_count):
            self.frame.grid_rowconfigure(row, minsize=30)
        self.frame.grid_rowconfigure(0, minsize=10)

    def focus_in(self, event):
        if event.widget.cget('fg') == 'grey':
            try:
                event.widget.delete(0, END)
            except:
                event.widget.delete('1.0', END)
            event.widget.config(fg='black')

    def focus_out(self, event, default):
        try:
            text = event.widget.get("1.0", "end-1c")
        except:
            text = event.widget.get()
        if not text:
            event.widget.config(fg='grey')
            event.widget.insert(END, default)

    def submitCmd(self):
        if session.init_term(self.term_input.get()):
            for tempc in self.course_input.get('1.0', END).split():
                if not session.is_valid_course(tempc):
                    messagebox.showwarning(title='Course not found',
                                           message=f'Error! Invalid course: {tempc}\nDid you mean: \n'
                                                   f'{[code for code in session.course_codes if tempc.upper() in code]}?')
                    break
            else:
                global courses
                courses = self.course_input.get('1.0', END).split()
                self.master.destroy()
                return
        else:
            print(f'Error! Invalid term: {self.term_input.get()}')


popup = get_term_courses()
root.wait_window(popup.master)


show_final = False
def toggle_show_final():
    for tab in tabs:
        if show_final:
            for fbutton in final:
                tab.create_image(int(fbutton.x1), int(fbutton.y1), image=fbutton.image, anchor='nw', tags='temp')
        else:
            tab.delete(tab.gettags('temp'))


def key_press(event):
    if event.char == 's' and final:
        pick = {'Term': final[0].data['term']}
        for f in final:
            pick.update({f.code: []})
        for f in final:
            pick.update({f.code: pick[f.code] + [f.data['courseReferenceNumber']]})
        pickle.dump(pick, open(filedialog.asksaveasfilename(initialdir="./schedules/", title="Save schedule", filetypes=(("all files", "*.*"),)), "wb"))
        messagebox.showinfo(title='Schedule saved!', message='Schedule saved!')
    elif event.char == 'u':
        global show_final
        show_final = not show_final
        toggle_show_final()
    elif event.char == 'r':
        for b in final:
            finaltab.delete(b.fbutton)
        for b in buttons:
            b.state = 'normal'
            b.tab.itemconfig(b.cbutton, state=b.state)
        final.clear()
    else:
        for b in buttons:
            if event.char == 'h':
                if b.state == 'disabled':
                    b.state = 'hidden'
                elif b.state == 'hidden':
                    b.state = 'disabled'
                b.tab.itemconfig(b.cbutton, state=b.state)
            elif event.char == 'i' and b.type == 'Lecture':
                b.toggle()
            elif event.char == 'o' and b.type == 'Discussion':
                b.toggle()
            elif event.char == 'p' and b.type == 'Laboratory' or b.type == 'Studio':
                b.toggle()


root.bind_all('<Key>', lambda event: key_press(event))


class course_button:
    cbutton = None
    fbutton = None
    state = 'normal'
    siblings = []

    def __init__(self, data):
        self.data = data
        self.type = data['scheduleTypeDescription']
        self.code = data['subject'] + data['courseNumber']

    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.tab = tabs[-1]
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            self.fill = kwargs.pop('fill')
            self.fill = root.winfo_rgb(self.fill) + (alpha,)
            image = Image.new('RGBA', (x2 - x1 - 2, y2 - y1 - 2), self.fill)
            image = ImageOps.expand(image, border=2, fill='black')
            image2 = Image.new('RGBA', (self.x2 - self.x1 - 2, self.y2 - self.y1 - 2), (0, 0, 0, 10))
            image2 = ImageOps.expand(image2, border=2, fill=(0, 0, 0, 50))

            draw = ImageDraw.Draw(image)
            draw2 = ImageDraw.Draw(image2)
            textfont = ImageFont.truetype('GOTHIC.TTF', size=15)
            lines = [self.code, self.type]
            iwidth, iheight = x2 - x1 - 1, y2 - y1 - 1
            for i, line in enumerate(lines):
                textw, texth = draw.textsize(line, textfont)
                draw.text(((iwidth - textw) / 2, (iheight - (texth * len(lines))) / 2 + (i * texth)), line,
                          fill=(0, 0, 0), font=textfont)
                draw2.text(((iwidth - textw) / 2, (iheight - (texth * len(lines))) / 2 + (i * texth)), line,
                           fill=(0, 0, 0, 100), font=textfont)

            self.image = ImageTk.PhotoImage(image)
            self.greyimage = ImageTk.PhotoImage(image2)
            self.cbutton = self.tab.create_image(x1, y1, image=self.image, disabledimage=self.greyimage, anchor='nw')
            self.tab.tag_bind(self.cbutton, '<Button-1>', lambda event, id=self.cbutton: self.callback(id))
        else:
            self.cbutton = c.create_rectangle(x1, y1, x2, y2, **kwargs)

    def callback(self, id):
        if self in final:
            for sibling in self.siblings:
                final.remove(sibling)
                finaltab.delete(sibling.fbutton)
                sibling.fbutton = None
            for b in buttons:
                if b.tab == self.tab and b.type == self.type and b is not self and b not in self.siblings:
                    b.state = 'normal'
                    b.tab.itemconfig(b.cbutton, state=b.state)
        else:
            for sibling in self.siblings:
                sibling.tab.tag_raise(sibling.cbutton)
                sibling.fbutton = finaltab.create_image(sibling.x1, sibling.y1, image=sibling.image, anchor='nw')
                final.append(sibling)
                finaltab.tag_bind(sibling.fbutton, '<Button-1>', lambda event, x=sibling: sibling.callback(x))
            for b in buttons:
                if b.tab == self.tab and b.type == self.type and b is not self and b not in self.siblings:
                    b.state = 'disabled'
                    b.tab.itemconfig(b.cbutton, state=b.state)

    def toggle(self):
        if self.state == 'normal':
            self.state = 'hidden'
        elif self.state == 'hidden':
            self.state = 'normal'
        self.tab.itemconfig(self.cbutton, state=self.state)


weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
originx, originy = 76, 30
cellw, cellh = 187, 28

""" Simultaneously scrape all course data """
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [(course, executor.submit(session.get_course_data, course)) for course in courses]

""" Create tab and buttons for each course """
for course_code, future in futures:
    c = Canvas(notebook, width=width, height=height, bd=0, highlightthickness=0, relief='ridge')
    c.focus_set()
    c.pack(fill=BOTH, expand=True)
    c.create_image(0, 0, image=background_image, anchor="nw", tags='bg')
    tabs.append(c)
    notebook.add(c, text=course_code)

    for section in future.result():  # for each section
        siblings = []
        days = [day for day in weekdays if section['meetingsFaculty'][0]['meetingTime'][day.lower()]]
        for day in days:
            time_format = '%H%M'
            top = datetime.strptime('0700', time_format)  # first time in schedule image
            start = datetime.strptime(section['meetingsFaculty'][0]['meetingTime']['beginTime'], time_format)
            end = datetime.strptime(section['meetingsFaculty'][0]['meetingTime']['endTime'], time_format)
            length = (end - start).seconds / 60

            adjh = int(length / 60 * (cellh * 2))  # scaled pixel height
            x1 = originx + weekdays.index(day) * cellw
            y1 = originy + int((start - top).seconds / 1800) * cellh
            x2 = originx + weekdays.index(day) * cellw + cellw
            y2 = originy + int((start - top).seconds / 1800) * cellh + adjh
            buttons.append(course_button(section))
            siblings.append(buttons[-1])

            typecolor = 'black'
            courseType = section['scheduleTypeDescription']
            if 'Lecture' in courseType:
                typecolor = 'Red'
            elif 'Discussion' in courseType:
                typecolor = 'Blue'
            elif 'Laboratory' in courseType or 'Studio' in courseType:
                typecolor = 'Yellow'
            buttons[-1].create_rectangle(x1, y1, x2, y2, fill=typecolor, alpha=.8)
        for b in siblings:
            b.siblings = siblings

root.deiconify()
root.mainloop()
