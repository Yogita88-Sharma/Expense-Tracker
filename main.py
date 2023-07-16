import datetime
import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sv_ttk

root = Tk()
root.geometry("1130x607")
root.title("Expense Tracker")

sv_ttk.set_theme("dark")

desc = StringVar()
amnt = DoubleVar()
payee = StringVar()
MoP = StringVar(value="Cash")
VoP = StringVar(value="Expense")

sideFrame = Frame(root, background="#1b1b1b", width=250)
buttonFrame = Frame(root, background="#212121", height=60)
buttonFrame.pack(side=TOP, fill=X)
sideFrame.pack(side=LEFT, fill=Y)

connector = sqlite3.connect("Expense Tracker.db")
cursor = connector.cursor()
connector.execute(
    'CREATE TABLE IF NOT EXISTS ExpenseTracker (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Date DATETIME, Payee TEXT, Expense TEXT, Amount FLOAT, ModeOfPayment TEXT)'
)
connector.commit()


# Functions
def list_all_expenses():
    global connector, table

    table.delete(*table.get_children())

    all_data = connector.execute('SELECT * FROM ExpenseTracker')
    data = all_data.fetchall()

    for values in data:
        table.insert('', END, values=values)


def view_expense_details():
    global table
    global date, payee, VoP, amnt, MoP

    if not table.selection():
        messagebox.showerror('No expense selected', 'Please select an expense from the table to view its details')

    current_selected_expense = table.item(table.focus())
    values = current_selected_expense['values']

    expenditure_date = datetime.date(int(values[1][:4]), int(values[1][5:7]), int(values[1][8:]))

    date.set_date(expenditure_date)
    payee.set(values[2])
    desc.set(values[3])
    amnt.set(values[4])
    MoP.set(values[5])


def clear_fields():
    global VoP, payee, amnt, MoP, date, table

    today_date = datetime.datetime.now().date()

    VoP.set('')
    payee.set('')
    amnt.set(0.0)
    MoP.set('Cash'), date.set_date(today_date)
    table.selection_remove(*table.selection())


def remove_expense():
    if not table.selection():
        messagebox.showerror('No record selected!', 'Please select a record to delete!')
        return

    current_selected_expense = table.item(table.focus())
    values_selected = current_selected_expense['values']

    surety = messagebox.askyesno('Are you sure?',
                                 f'Are you sure that you want to delete the record of {values_selected[2]}')

    if surety:
        connector.execute('DELETE FROM ExpenseTracker WHERE ID=%d' % values_selected[0])
        connector.commit()

        list_all_expenses()
        messagebox.showinfo('Record deleted successfully!',
                            'The record you wanted to delete has been deleted successfully')


def remove_all_expenses():
    surety = messagebox.askyesno('Are you sure?',
                                 'Are you sure that you want to delete all the expense items from the database?',
                                 icon='warning')

    if surety:
        table.delete(*table.get_children())

        connector.execute('DELETE FROM ExpenseTracker')
        connector.commit()

        clear_fields()
        list_all_expenses()
        messagebox.showinfo('All Expenses deleted', 'All the expenses were successfully deleted')
    else:
        messagebox.showinfo('Ok then', 'The task was aborted and no expense was deleted!')


def add_another_expense():
    global date, payee, VoP, amnt, MoP
    global connector

    if not date.get() or not payee.get() or not VoP.get() or not amnt.get() or not MoP.get():
        messagebox.showerror('Fields empty!', "Please fill all the missing fields before pressing the add button!")
    else:
        connector.execute(
            'INSERT INTO ExpenseTracker (Date, Payee,  Expense,Amount, ModeOfPayment) VALUES (?, ?, ?, ?, ?)',
            (date.get_date(), payee.get(), VoP.get(),amnt.get(), MoP.get())
        )
        connector.commit()

        clear_fields()
        list_all_expenses()
        messagebox.showinfo('Expense added',
                            'The expense whose details you just entered has been added to the database')


def edit_expense():
    global table

    def edit_existing_expense():
        global date, amnt, VoP, payee, MoP
        global connector, table

        current_selected_expense = table.item(table.focus())
        contents = current_selected_expense['values']

        connector.execute(
            'UPDATE ExpenseTracker SET Date = ?, Payee = ?, Expense = ?, Amount = ?, ModeOfPayment = ? WHERE ID = ?',
            (date.get_date(), payee.get(), desc.get(), amnt.get(), MoP.get(), contents[0]))
        connector.commit()

        clear_fields()
        list_all_expenses()

        messagebox.showinfo('Data edited', 'We have updated the data and stored in the database as you wanted')
        edit_btn.destroy()
        return

    if not table.selection():
        messagebox.showerror('No expense selected!',
                             'You have not selected any expense in the table for us to edit; please do that!')
        return

    view_expense_details()

    edit_btn = Button(buttonFrame, text='Edit expense', width=30, command=edit_existing_expense)
    edit_btn.pack()


def selected_expense_to_words():
    global table

    if not table.selection():
        messagebox.showerror('No expense selected!', 'Please select an expense from the table for us to read')
        return

    current_selected_expense = table.item(table.focus())
    values = current_selected_expense['values']

    message = f'Your expense can be read like: \n"You paid {values[4]} to {values[2]} for {values[3]} on {values[1]} via {values[5]}"'

    messagebox.showinfo('Here\'s how to read your expense', message)


def expense_to_words_before_adding():
    global date, VoP, amnt, payee, MoP

    if not date or not VoP or not amnt or not payee or not MoP:
        messagebox.showerror('Incomplete data', 'The data is incomplete, meaning fill all the fields first!')

    message = f'Your expense can be read like: \n"You paid {amnt.get()} to {payee.get()} for {desc.get()} on {date.get_date()} via {MoP.get()}"'

    add_question = messagebox.askyesno('Read your record like: ', f'{message}\n\nShould I add it to the database?')

    if add_question:
        add_another_expense()
    else:
        messagebox.showinfo('Ok', 'Please take your time to add this record')


date = DateEntry(sideFrame, date=datetime.datetime.now())
Label(sideFrame, text="Date: ", background="#1b1b1b").place(x=5, y=15)
date.place(x=60, y=10)

Label(sideFrame, text="Expense: ", background="#1b1b1b").place(x=5, y=80)
expense_list = ttk.OptionMenu(sideFrame, VoP,
                              *['Food', 'Travel', 'Education', 'Entertainment', 'Electricity', 'Household',
                                'Groceries'])
expense_list.config(width=15)
expense_list.place(x=70, y=80)

ttk.Label(sideFrame, text="Amount: ", background="#1b1b1b").place(x=5, y=145)
ttk.Entry(sideFrame, text=amnt).place(x=70, y=140)

ttk.Label(sideFrame, text="Payee: ", background="#1b1b1b").place(x=5, y=205)
ttk.Entry(sideFrame, text=payee).place(x=60, y=205)

ttk.Label(sideFrame, text="Mode Of Pay: ", background="#1b1b1b").place(x=5, y=270)
mode_of_pay = ttk.OptionMenu(sideFrame, MoP,
                             *['Cash', 'Cheque', 'Credit Card', 'Debit Card', 'Paytm', 'Google Pay', 'Razorpay',
                               'BHIM UPI'])
mode_of_pay.config(width=10)
mode_of_pay.place(x=100, y=265)

ttk.Button(sideFrame, text='Add expense', command=add_another_expense).place(x=10, y=350)

#########################################################

ttk.Button(buttonFrame, text='Delete Expense', command=remove_expense).place(x=5, y=11)

ttk.Button(buttonFrame, text='Clear Fields in DataEntry', command=clear_fields).place(x=130, y=11)

ttk.Button(buttonFrame, text='Delete All Expenses',
           command=remove_all_expenses).place(x=310, y=11)

ttk.Button(buttonFrame, text='Edit Selected Expense', command=edit_expense).place(x=465, y=11)

ttk.Button(buttonFrame, text='Convert Expense to a sentence', command=selected_expense_to_words).place(x=630, y=11)

tree_frame = Frame(root, background="#121212")
tree_frame.place(relx=0.202, rely=0.11, relwidth=0.79, relheight=0.86)

table = ttk.Treeview(tree_frame, selectmode=BROWSE,
                     columns=('ID', 'Date', 'Payee', 'Expense', 'Amount', 'Mode of Payment'))

X_Scroller = Scrollbar(table, orient=HORIZONTAL, command=table.xview)
Y_Scroller = Scrollbar(table, orient=VERTICAL, command=table.yview)
X_Scroller.pack(side=BOTTOM, fill=X)
Y_Scroller.pack(side=RIGHT, fill=Y)

table.config(yscrollcommand=Y_Scroller.set, xscrollcommand=X_Scroller.set)

table.heading('ID', text='S No.', anchor=CENTER)
table.heading('Date', text='Date', anchor=CENTER)
table.heading('Payee', text='Payee', anchor=CENTER)
table.heading('Expense', text='Expense', anchor=CENTER)
table.heading('Amount', text='Amount', anchor=CENTER)
table.heading('Mode of Payment', text='Mode of Payment', anchor=CENTER)

table.column('#0', width=0, stretch=NO)
table.column('#1', width=50, stretch=NO)
table.column('#2', width=95, stretch=NO)  # Date column
table.column('#3', width=150, stretch=NO)  # Payee column
table.column('#4', width=325, stretch=NO)  # Title column
table.column('#5', width=135, stretch=NO)  # Amount column
table.column('#6', width=125, stretch=NO)  # Mode of Payment column

table.place(relx=0, y=0, relheight=1, relwidth=1.2)

list_all_expenses()

mainloop()