# Dependencies
from typing import re

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBodyTouch, OneLineListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from datetime import datetime

# To be added after creating the database
from database import Database
# Initialize db instance
db = Database()


class DialogContent(MDBoxLayout):
    """OPENS A DIALOG BOX THAT GETS THE TASK FROM THE USER"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.date_text.text = str(datetime.now().strftime('%A %d %B %Y'))

    
    def show_date_picker(self):
        """Opens the date picker"""
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        date = value.strftime('%A %d %B %Y')
        self.ids.date_text.text = str(date)

# After creating the database.py
class ListItemWithCheckbox(TwoLineAvatarIconListItem):
    '''Custom list item'''

    def __init__(self, pk=None, **kwargs):
        super().__init__(**kwargs)
        # state a pk which we shall use link the list items with the database primary keys
        self.pk = pk

    def mark(self, check, the_list_item):
        '''mark the task as complete or incomplete'''
        if check.active == True:
            the_list_item.text = '[s]'+the_list_item.text+'[/s]'
            db.mark_task_as_complete(the_list_item.pk)# here
        else:
            the_list_item.text = str(db.mark_task_as_incomplete(the_list_item.pk))# Here

    def delete_item(self, the_list_item):
        '''Delete the task'''
        self.parent.remove_widget(the_list_item)
        db.delete_task(the_list_item.pk)# Here

class LeftCheckbox(ILeftBodyTouch, MDCheckbox):
    '''Custom left container'''

# Main App class
class MainApp(MDApp):
    task_list_dialog = None
    def build(self):
        # Setting theme to my favorite theme
        self.theme_cls.primary_palette = "Cyan"
        
    # Showing the task dialog to add tasks 
    def show_task_dialog(self):
        if not self.task_list_dialog:
            self.task_list_dialog = MDDialog(
                title="Use AcademEase and add your task",
                type="custom",
                content_cls=DialogContent(),
            )

        def edit_entry(self, proc, depth, rod, dist):
            """new_entry = OneLineListItem(text=f"Rod: {rod-1} Distance: {dist-3} Proc: {proc} Depth: {depth}",
                                        on_press=lambda x: self.change_entry(proc, depth, new_entry))"""
            self.protocol[-1] = {"Rod": rod - 1, "Distance": dist - 3, "Proc": proc, "Depth": depth}
            clean_entry = re.sub(r"[,'{}]", '', str(self.protocol[-1]))
            new_entry = OneLineListItem(text=clean_entry,
                                        on_press=lambda x: self.change_entry(proc, depth, new_entry))
            self.root.ids.container.add_widget(new_entry)
            self.root.ids.edit.disabled = True
            self.root.ids.add.disabled = False

        def change_entry(self, proc, depth, entry):
            self.root.ids.proc.text = proc
            self.root.ids.depth.text = depth
            self.root.ids.container.remove_widget(entry)
            self.root.ids.edit.disabled = False
            self.root.ids.add.disabled = True

        def add_entry(self, proc, depth):
            self.protocol.append({"Rod": '', "Distance": '', "Proc": '', "Depth": ''})
            self.protocol[self.rod - 1]["Proc"] = proc
            self.protocol[self.rod - 1]["Depth"] = depth
            self.protocol[self.rod - 1]["Rod"] = self.rod
            self.protocol[self.rod - 1]["Distance"] = self.dist
            clean_entry = re.sub(r"[,'{}]", '', str(self.protocol[self.rod - 1]))
            entry = OneLineListItem(text=f"{clean_entry}", on_press=lambda x: self.change_entry(proc, depth, entry))
            self.root.ids.container.add_widget(entry)
            self.rod += 1
            self.dist += 3


        self.task_list_dialog.open()
    def on_start(self):
        # Load the saved tasks and add them to the MDList widget when the application starts
        try:
            incompleted_tasks, completed_tasks = db.get_tasks()

            if incompleted_tasks != []:
                for task in incompleted_tasks:
                    add_task = ListItemWithCheckbox(pk=task[0],text=str(task[1]), secondary_text=task[2])
                    add_task.ids.check.active = False
                    self.root.ids.container.add_widget(add_task)
            if completed_tasks != []:
                for task in completed_tasks:
                    add_task = ListItemWithCheckbox(pk=task[0],text='[s]'+str(task[1])+'[/s]', secondary_text=task[2])
                    add_task.ids.check.active = True
                    self.root.ids.container.add_widget(add_task)
        except Exception as e:
            print(e)
            pass

    def close_dialog(self, *args):
        self.task_list_dialog.dismiss()

    def add_task(self, task, task_date):
        '''Add task to the list of tasks'''
        # print(task.text, task_date)
        created_task = db.create_task(task.text, task_date)

        # return the created task details and create a list item
        self.root.ids['container'].add_widget(ListItemWithCheckbox(pk=created_task[0], text='[b]'+str(created_task[1])+'[/b]', secondary_text=created_task[2]))
        task.text = ''

if __name__ == ('__main__'):
    app = MainApp()
    app.run()
