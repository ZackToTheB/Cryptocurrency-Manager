import sqlite3 as sql
import tkinter as tk
from tkinter import ttk
import time, threading

import CoinGeckoAPITest as GC_API

class CryptoWindow:
    def __init__(self, master, db):
        self._master = master
        self._master.title("Crypto Manager - {0}".format(getTime(False)))
        #self._master.iconbitmap(self, default = "icon_crypto.ico")
        self._master.resizable(False, False)

        self.__create_layout()
        self.__create_items()
        self.__run_time()

        self.__cursor = db.cursor()
        self.__db = db

        self.__view_table()

    def __create_layout(self):
        self.__time_frame = tk.Frame(self._master)
        self.__button_frame = tk.Frame(self._master)
        self.__widget_frame = tk.Frame(self._master)
        self.__exit_frame = tk.Frame(self._master)

        self.__time_frame.grid(row = 0, column = 0, columnspan = 1)#, sticky = "ew")
        self.__button_frame.grid(row = 1, column = 0)
        self.__widget_frame.grid(row = 2, column = 0)
        self.__exit_frame.grid(row = 0, column = 0, sticky = "w")

    def __create_items(self):
        self.__time_label = tk.Label(self.__time_frame, text = "TIME", font = ("TkDefaultFont", 14))
        self.__time_label.grid(row = 0, column = 0, columnspan = 2, sticky = "ew")

        self.__quit_button = tk.Button(self.__exit_frame, text = "QUIT", fg = "red", command = lambda:self.__close())
        self.__quit_button.grid(row = 0, column = 0, sticky = "w")

        #self.__view_table_button = tk.Button(self.__button_frame, text = "View Table", height = 2, width = 15, command = lambda:self.__view_table())
        #self.__view_table_button.grid(row = 0, column = 0, padx = 3, pady = 3)
        self.__valuation_button = tk.Button(self.__button_frame, text = "Valuation", height = 2, width = 15, command = lambda:self.get_valuation())
        self.__valuation_button.grid(row = 0, column = 1, padx = 3, pady = 3)
        self.__edit_invested_button = tk.Button(self.__button_frame, text = "Edit Invested", height = 2, width = 15, command = lambda:self.edit_invested())
        self.__edit_invested_button.grid(row = 0, column = 2, padx = 3, pady = 3)

    def __close(self):
        if self.__tick is not None:
            self.__tick.cancel()
        self._master.destroy()

    def __run_time(self):
        try:
            self.__tick = threading.Timer(1.0, self.__run_time)
            self.__tick.start()
            time = getTime()
            self.__time_label["text"] = "{}".format(time[1])
            if self._master.title()[-10:] != time[0]:
                self._master.title("Crypto Manager - {0}".format(time[0]))
        except Exception as e:
            print("Time error:", e, end="! || ")
            if str(self.__tick)[17:24] == "started":
                print("Cancelling time tick.")
            else:
                print("Time tick cancelled.")
            self.__tick.cancel()

    ###TABLE FUNCTIONS###

    def __view_table(self):
        self.columns = ("id", "symbol", "holdings")
        self.tree = ttk.Treeview(self.__widget_frame, columns=self.columns[1:])
        i = 0
        for column in self.columns:
            #print("C: {0}".format(column))
            self.tree.heading("#{0}".format(i), text = column)
            self.tree.column("#{0}".format(i), stretch=tk.NO)
            i += 1
        self.tree.grid(row=2, columnspan=3, sticky="nsew")
        self.treeview = self.tree
        self.tree.bind("<Double-1>", self.select_item)
        self.selected = None
        
        sql = """SELECT * FROM crypto_table"""
        self.__cursor.execute(sql)
        data = self.__cursor.fetchall()
        for each in data:
            temp = []
            for i in range(1, len(each)):
                temp.append(each[i])
            values = tuple(temp)
            if values[1] != 0 or 1:
                self.treeview.insert('', 'end', text=each[0], values=values)

        self.newButton = tk.Button(self.__widget_frame, text = "New Record", height = 3, width = 25, font = ("TkDefaultFont", 10), command = lambda:self.new_record())
        self.editButton = tk.Button(self.__widget_frame, text = "Edit Record", height = 3, width = 25, font = ("TkDefaultFont", 10), command = lambda:self.edit_record())
        self.removeButton = tk.Button(self.__widget_frame, text = "Remove Record", height = 3, width = 25, font = ("TkDefaultFont", 10), command = lambda:self.remove_record())
        self.selectedLabel = tk.Label(self.__widget_frame, text = "")
        
        self.newButton.grid(row = 0, column = 0, pady = 1)
        self.editButton.grid(row = 0, column = 1, pady = 1)
        self.removeButton.grid(row = 0, column = 2, pady = 1)
        self.selectedLabel.grid(row = 1, column = 0, sticky = "w", pady = 2)

    def select_item(self, e):
        selected = self.tree.focus()
        if len(selected) > 0:
            self.selected = self.tree.item(selected, "text")
            self.selectedLabel.config(text= "   Selected id: {0}".format(self.selected))
        #print(self.selected)
        
    def new_record(self):
        self.task = "new"
        self.record_view("New Record")

    def edit_record(self): #Fills record view for edit
        if self.selected is not None:
            self.task = "edit"
            self.__cursor.execute("""SELECT * FROM crypto_table WHERE id='"""+str(self.selected)+"""'""")
            data = self.__cursor.fetchone()
            self.record_view("Record: {0}".format(self.selected))
            #print(data)
            for i in range(0, len(data)):
                    self.inputs[i].insert(0, data[i])

    def remove_record(self):
        self.__cursor.execute("""DELETE FROM crypto_table WHERE id='"""+str(self.selected)+"""'""")
        self.__db.commit()
        self.__view_table()

    def record_view(self, title): #Record view for edit and new
        self.recordView = tk.Tk()
        self.recordView.title(title)
        self.recordView.resizable(False, False)

        self.labelFrame = tk.Frame(self.recordView)
        self.inputFrame = tk.Frame(self.recordView)
        
        self.labelFrame.grid(row = 0, column = 0)
        self.inputFrame.grid(row = 0, column = 1)

        labels = []
        self.inputs = []
        i = 0
        for column in self.columns:
            labels.append(tk.Label(self.labelFrame, text = "{0}:".format(column)))
            self.inputs.append(tk.Entry(self.inputFrame))

            labels[i].grid(row = i, column = 0, sticky = "e", pady = 1)
            self.inputs[i].grid(row = i, column = 1, sticky = "w", pady = 1)

            i += 1

        self.cancel = tk.Button(self.recordView, text = "Cancel", height = 2, width = 20, command = lambda:self.record_view_close(True))
        self.cancel.grid(row = 1, column = 0)
        self.confirm = tk.Button(self.recordView, text = "Confirm", height = 2, width = 20, command = lambda:self.record_view_close())
        self.confirm.grid(row = 1, column = 1)

    def __unselect(self):
        self.selectedLabel.config(text= " "*40)
        self.selected = None
        
    def record_view_close(self, cancel = False): #Closes record view
        if cancel:
            self.recordView.destroy()
        else:
            values = []
            for i in range(0, len(self.inputs)):
                if i == 0:
                    newVal = self.inputs[i].get().lower()
                elif i == 1:
                    newVal = self.inputs[i].get().upper()
                else:
                    newVal = self.inputs[i].get()
                values.append(newVal)
            #print(values)
            flag = False #Flags if any values are empty
            for value in values:
                if "" == value:
                    flag = True
            if flag:
                print("Error: Empty value(s)")
            else:
                if self.task == "edit":
                    sql = """UPDATE crypto_table SET """
                    for i in range(0, len(values)):
                        sql += self.columns[i] + """ = '"""+str(values[i])+"""', """
                    sql = sql[:-2] + """ WHERE id='"""+str(self.selected)+"""'"""
                elif self.task == "new":
                    sql = """INSERT INTO crypto_table ("""
                    for i in range(0, len(self.columns)):
                        sql += self.columns[i] +""", """
                    sql = sql[:-2] + """) VALUES ('"""
                    for i in range(0, len(self.columns)):
                        sql += str(values[i])+"""', '"""
                    sql = sql[:-4] + """')"""
                #print(sql)
                self.__cursor.execute(sql)
                self.__db.commit()
                self.__view_table()
                
                self._master.deiconify()
                self.recordView.destroy()
        if self.task == "new" or not cancel:
            self.__unselect()

        ###TABLE FUNCTIONS END###

    def get_valuation(self, currency = "gbp"):
        self.__cursor.execute("""SELECT id, symbol, holdings FROM crypto_table""")
        results = self.__cursor.fetchall()
        self.__cursor.execute("""SELECT invested FROM invested_table""")
        invested = float(self.__cursor.fetchone()[0])
        total, totalR = 0, 0
        for crypto in results:
            if crypto[2] > 0:
                url = "https://api.coingecko.com/api/v3/coins/{}".format(crypto[0])
                data = GC_API.CoingeckoAPI(url).get_coingecko_data()["market_data"]
                price = data["current_price"][currency]
                #print(price)
                value = price*crypto[2]
                valueR = round_(value)
                total += value
                totalR += valueR
                print("{0:>7} {1:^5} = £{2:<7.2f} >>  £{3:.2f}".format(crypto[2], crypto[1], value, valueR))
            
        print("-----\nTotal Blockfolio Value: £{0:<7.2f} >>  £{1:.2f}".format(total, totalR))
        print("Total Investment Made:  £{0}, P/L: {1}£{2:.2f} ({3:.1f}%)".format(invested, isPos(total - invested), abs(total - invested), (total - invested)*100 / invested))
        print("@ {} on {}\n-----".format(getTime(1)[1], getTime(0)))

    def edit_invested(self):
        self.investedView = tk.Tk()
        self.investedView.title("Edit Invested")
        self.investedView.resizable(False, False)

        current_label = tk.Label(self.investedView, text = "Current:")
        current_label.grid(row = 0, column = 0)
        current_amount = tk.Label(self.investedView, text = self.get_invested())
        current_amount.grid(row = 0, column = 1)
        invested_label = tk.Label(self.investedView, text = "Invested:")
        invested_label.grid(row = 1, column = 0)
        self.invested_entry = tk.Entry(self.investedView)
        self.invested_entry.grid(row = 1, column = 1)

        i_cancel = tk.Button(self.investedView, text = "Cancel", height = 2, width = 20, command = lambda:self.invested_view_close(True))
        i_cancel.grid(row = 2, column = 0)
        i_confirm = tk.Button(self.investedView, text = "Confirm", height = 2, width = 20, command = lambda:self.invested_view_close())
        i_confirm.grid(row = 2, column = 1)

    def get_invested(self):
        self.__cursor.execute("SELECT invested FROM invested_table")
        return int(self.__cursor.fetchone()[0])
    
    def invested_view_close(self, cancel = False): #Closes record view
        if cancel:
            self.investedView.destroy()
        else:
            value = self.invested_entry.get()
            #print(values)
            flag = False #Flags if any values are empty
            if "" == value:
                flag = True
            if flag:
                print("Error: Empty value")
            else:
                if value[0] == "+" or value[0] == "-":
                    value = self.get_invested() + int(str(value[0:]))
                sql = """UPDATE invested_table SET invested = '"""+str(value)+"""'"""
                #print(sql)
                self.__cursor.execute(sql)
                self.__db.commit()
                
                self.investedView.destroy()
                
def round_(value, to = .5):
    if (value % to) >= (to / 2):
        rounded = (value + to) - (value % to)
    else:
        rounded = value - (value % to)
    return rounded

def isPos(value):
    if value < 0:
        return "-"
    else:
        return " "                   
        
def getTime(time_ = True):
    t = time.localtime()
    ts = [str(t[3]), str(t[4]), str(t[5]), str(t[2]), str(t[1]), str(t[0])]
    for i in range(5):
        if len(ts[i]) == 1:
            new = "0"+str(ts[i])
            ts[i] = new
            
    tstring = "{0}:{1}:{2}".format(ts[0], ts[1], ts[2])
    dstring = "{0}/{1}/{2}".format(ts[3], ts[4], ts[5])

    if time_:
        return dstring, tstring
    else:
        return dstring

def main():
    with sql.connect("data.db") as db:
        db_ = db
        #cursor = db.cursor()
    
    root = tk.Tk()
    win = CryptoWindow(root, db_)
    win._master.mainloop()

if __name__ == "__main__":

    main()
