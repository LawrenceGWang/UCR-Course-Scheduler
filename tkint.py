from tkinter import *
from tkinter import ttk, messagebox
import tkinter.font as tkFont
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont, ImageGrab, ImageEnhance
from sys import exit
from datetime import *
from main import getCourseData

import time
import pickle
import concurrent.futures

root = Tk()
root.title('Input Term and Courses')
root.geometry("390x335")
root.resizable(False, False)
fontStyle = tkFont.Font(family="Century Gothic", size=15)

frame = Frame(root)
frame.pack()


def focus_in(event):
    if event.widget.cget('fg') == 'grey':
        try:
            event.widget.delete(0, END)
        except:
            event.widget.delete('1.0', END)
        event.widget.config(fg='black')


def focus_out(event, default):
    try:
        text = event.widget.get("1.0", "end-1c")
    except:
        text = event.widget.get()
    if not text:
        event.widget.config(fg='grey')
        event.widget.insert(END, default)


""" Get term of classes """
default_term_text = 'Fall 2020'
Label(frame, text="Course Term\n(Leave blank\nfor latest)", font=fontStyle).grid(row=1, padx=(10, 10))
termin = Entry(frame, width=10, font=fontStyle, fg='grey')
termin.insert(END, default_term_text)
termin.grid(row=1, column=1, sticky='ew', padx=(10, 10))
termin.bind("<FocusIn>", focus_in)
termin.bind("<FocusOut>", lambda event: focus_out(event, default_term_text))

""" Get list of courses to scrape """
# default_course_text = 'AHS007\nPHYS040A\nHIST010\nECON002\nCS010A'
default_course_text = 'PHYS040A\nHIST010\nECON002\nCS010'
Label(frame, text="Course Codes\n(One per line)", font=fontStyle).grid(row=3, padx=(10, 10))
coursesin = Text(frame, width=10, height=5, font=fontStyle, fg='grey')
coursesin.insert(END, default_course_text)
coursesin.grid(row=3, column=1, sticky="nsew", padx=(10, 10))
coursesin.bind("<FocusIn>", focus_in)
coursesin.bind("<FocusOut>", lambda event: focus_out(event, default_course_text))


def submitCmd():
    global ret
    x = termin.get()
    if termin.cget('fg') == 'grey':
        x = ''
    y = coursesin.get('1.0', END).split()
    # if coursesin.cget('fg') == 'grey':
    # y = []
    ret = (x, y)
    frame.destroy()
    root.destroy()


submit = Button(frame, text='Button', font=fontStyle, command=submitCmd)
submit.grid(row=5, column=0, rowspan=2, columnspan=2, sticky='nsew', padx=(10, 10))

col_count, row_count = frame.grid_size()
for col in range(col_count):
    frame.grid_columnconfigure(col, minsize=10)
for row in range(row_count):
    frame.grid_rowconfigure(row, minsize=30)
frame.grid_rowconfigure(0, minsize=10)

root.mainloop()



root = Tk()
root.title('Course Scheduler')
width, height = 1012, 759
posHor = int(root.winfo_screenwidth() / 2 - width / 2)
posVert = int(root.winfo_screenheight() / 2 - height / 2)
root.geometry(f"{width}x{height}+{posHor}+{posVert - 50}")
root.resizable(False, False)

notebook = ttk.Notebook(root)
notebook.pack()

tabs = []
buttons = []


def keyCall(event):
    if event.char == 's':
        pick = {'Term': gterm}
        for f in final:
            pick.update({f.data[1] + f.data[3]: []})
        for f in final:
            pick.update({f.data[1] + f.data[3]: pick[f.data[1] + f.data[3]] + [f.data[0]]})
        pickle.dump(pick, open(f"./pickles/final.p", "wb"))
        print('Saved!')
    elif event.char == 'u':
        global normal_bg
        normal_bg = not normal_bg
        toggle_bg()
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


root.bind_all('<Key>', lambda event: keyCall(event))

background_image = PhotoImage(file='./blank_schedule.png')

finaltab = Canvas(notebook, width=width, height=height, bd=0, highlightthickness=0, relief='ridge')
finaltab.pack(fill=BOTH, expand=True)
finaltab.create_image(0, 0, image=background_image, anchor="nw", tags='bg')
notebook.add(finaltab, text='Final')
final = []
fimage = Image.open('./blank_schedule.png')
fdraw = ImageDraw.Draw(fimage, 'RGBA')
fimagetemp = None
normal_bg = True
def toggle_bg():
    global fimage, fdraw, fimagetemp, normal_bg
    fimage = Image.open('./blank_schedule.png')
    if normal_bg:
        fdraw = ImageDraw.Draw(fimage, 'RGBA')
        for fbutton in final:
            x, y = fbutton.tab.coords(fbutton.cbutton)
            fimage.paste(fbutton.pilimage, (int(x), int(y)), fbutton.pilimage)
    fimagetemp = ImageTk.PhotoImage(fimage)
    for tab in tabs:
        tab.delete(tab.gettags('bg')[0])
        tab.create_image(0, 0, image=fimagetemp, anchor="nw", tags='bg')
        tab.tag_lower(tab.gettags('bg')[0])


class myButton:
    cbutton = None
    fbutton = None
    state = 'normal'
    siblings = []

    def __init__(self, days, ctime, data):
        self.days = days
        self.ctime = ctime
        self.data = data
        self.type = self.data[5].split()[-1]
        self.code = self.data[1] + self.data[3]

    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.tab = tabs[-1]
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            self.fill = kwargs.pop('fill')
            self.fill = root.winfo_rgb(self.fill) + (alpha,)
            image = Image.new('RGBA', (x2 - x1 - 2, y2 - y1 - 2), self.fill)
            image = ImageOps.expand(image, border=2, fill='black')
            self.pilimage = Image.new('RGBA', (x2 - x1 - 10, y2 - y1 - 10), (0, 0, 255, 128))
            self.pilimage = ImageOps.expand(self.pilimage, border=5, fill=(255, 0, 0, 128))
            image2 = Image.new('RGBA', (self.x2 - self.x1 - 2, self.y2 - self.y1 - 2), (0, 0, 0, 10))
            image2 = ImageOps.expand(image2, border=2, fill=(0, 0, 0, 50))

            draw = ImageDraw.Draw(image)
            draw2 = ImageDraw.Draw(image2)
            draw3 = ImageDraw.Draw(self.pilimage)
            textfont = ImageFont.truetype('GOTHIC.TTF', size=15)
            lines = [self.code, self.type]
            iwidth, iheight = x2 - x1 - 1, y2 - y1 - 1
            for i, line in enumerate(lines):
                textw, texth = draw.textsize(line, textfont)
                draw.text(((iwidth - textw) / 2, (iheight - (texth * len(lines))) / 2 + (i * texth)), line,
                          fill=(0, 0, 0), font=textfont)
                draw2.text(((iwidth - textw) / 2, (iheight - (texth * len(lines))) / 2 + (i * texth)), line,
                           fill=(0, 0, 0, 100), font=textfont)
                draw3.text(((iwidth - textw) / 2, (iheight - (texth * len(lines))) / 2 + (i * texth)), line,
                           fill=(0, 0, 0, 200), font=textfont)

            self.image = ImageTk.PhotoImage(image)
            self.greyimage = ImageTk.PhotoImage(image2)
            self.cbutton = self.tab.create_image(x1, y1, image=self.image, disabledimage=self.greyimage, anchor='nw')
            self.tab.tag_bind(self.cbutton, '<Button-1>', lambda event, id=self.cbutton: self.callback(id))
        else:
            self.cbutton = c.create_rectangle(x1, y1, x2, y2, **kwargs)

    def callback(self, id):
        # print(id)
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

invalid_courses, futures = [], []

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     futures = [(param, executor.submit(getCourseData, ret[0], param)) for param in ret[1]]
# for course, tempdata in [(f[0], f[1].result()) for f in futures]:

coursecopy = ret[1][:]
for course in ret[1]:
    if len(course) < 3:
        continue
    try:
        futures.append(pickle.load(open(f"./pickles/{course}.p", "rb")))
        coursecopy.remove(course)
        print('pickle loaded')
    except:
        continue

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures2 = [(param, executor.submit(getCourseData, ret[0], param)) for param in coursecopy]

for course, futuredata in futures2:
    try:
        result = futuredata.result()
        pickle.dump((course, result), open(f"./pickles/{course}.p", "wb"))
        futures.append((course, result))
        print('pickle saved')
    except Exception as e:
        invalid_courses.append(e)
        continue

# """
# for course in ret[1]:
#     if len(course) < 3:
#         continue
#
#     try:
#         tempdata = pickle.load(open(f"./{course}.p", "rb"))
#         print('pickle loaded')
#     except:
#         try:
#             tempdata = getCourseData(ret[0], course)
#             pickle.dump(tempdata, open(f"./{course}.p", "wb"))
#             print('pickle saved')
#         except Exception as e:
#             invalid_courses.append(e)
#             continue
# """
for course, tempdata in futures:
    c = Canvas(notebook, width=width, height=height, bd=0, highlightthickness=0, relief='ridge')
    c.focus_set()
    c.pack(fill=BOTH, expand=True)
    c.create_image(0, 0, image=background_image, anchor="nw", tags='bg')
    tabs.append(c)
    notebook.add(tabs[-1], text=course)

    for days, ctime, data, term in tempdata:  # for each section
        global gterm
        gterm = term
        siblings = []
        for day in days:
            cstart, cend = ctime.split(' - ')
            format = '%I:%M %p'
            top = datetime.strptime('07:00 AM', format)
            start = datetime.strptime(cstart, format)
            end = datetime.strptime(cend, format)
            length = (end - start).seconds / 60

            adjh = int(length / 60 * (cellh * 2))  # adjusted pixel height
            x1 = originx + weekdays.index(day) * cellw
            y1 = originy + int((start - top).seconds / 1800) * cellh
            x2 = originx + weekdays.index(day) * cellw + cellw
            y2 = originy + int((start - top).seconds / 1800) * cellh + adjh
            buttons.append(myButton(days, ctime, data))
            # if len(days) > 1:
            siblings.append(buttons[-1])

            typecolor = 'black'
            if 'Lecture' in data[5]:
                typecolor = 'Red'
            elif 'Discussion' in data[5]:
                typecolor = 'Blue'
            elif 'Laboratory' in data[5] or 'Studio' in data[5]:
                typecolor = 'Yellow'
            buttons[-1].create_rectangle(x1, y1, x2, y2, fill=typecolor, alpha=.8)

        for b in siblings:
            b.siblings = siblings
        # print(days, len(siblings))

if invalid_courses:
    error_msg = ''
    for error in invalid_courses:
        error_msg += str(error) + '\n'
    messagebox.showwarning(title='Course not found', message=error_msg)

root.mainloop()
