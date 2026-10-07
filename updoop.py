from __future__ import annotations
import tkinter as tk
from tkinter import filedialog
import rarfile
import sys
import os
from pathlib import Path
from shutil import copy, move
from requests import get
from re import search
from dataclasses import dataclass
from io import BytesIO
from tempfile import gettempdir
from traceback import print_exc, format_exc


FILEPATH = Path(__file__).parent
def res_path(relative):
    global FILEPATH
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
        FILEPATH = Path(sys.executable).parent
    else:
        base = FILEPATH
        
    return base / relative

def center_window(window):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    w = window.winfo_width()
    h = window.winfo_height()
    x = (screen_width - w) // 2
    y = (screen_height - h) // 2
    window.geometry(f"+{x}+{y}")
    

PROGRAM_NAME = "ZapretUpdater"
TEMP_DIR = res_path('temp')
rarfile.UNRAR_TOOL = res_path("UnRAR.exe")

BG          = "#1E1F22"   # фон окна
PANEL       = "#2B2D31"   # панели
PANEL_LIGHT = "#313338"   # светлее
ACCENT      = "#3BA55D"   # зелёный
ACCENT_H    = "#4CC16F"   # зелёный hover
TEXT        = "#E8E8E8"
MUTED       = "#9A9A9A"
    

class BlankApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Zpret Updater")
        self.iconbitmap(res_path('Zu.ico'))
        self.geometry('400x200')
        center_window(self)
        self.resizable(False, False)
        self.config(bg=BG)
        
        ff = FinalFrame(self)
        ff.set_text(format_exc())
        ff.btn['command'] = exit
        ff.btn['text'] = 'Quit'
        ff.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Zapret Updater")
        self.iconbitmap(res_path('Zu.ico'))
        self.geometry('400x200')
        center_window(self)
        self.resizable(False, False)
        self.config(bg=BG)
        choose_dir = ChooseDirFrame(self, bg=PANEL)
        choose_dir.pack(fill='both', expand=True, padx=20, pady=(20, 0), ipadx=10, ipady=10)
        
        choose_target_dir = ChooseTargetDirFrame(self, bg=PANEL)
        choose_target_dir.pack(fill='both', expand=True, padx=20, pady=10, ipadx=10, ipady=10)
        
        update = UpdateFrame(self, bg=BG)
        update.pack(fill='both', expand=True, padx=20, pady=(0, 20), ipadx=10, ipady=10)
        
        self.from_field = choose_dir.text_field
        self.to_field = choose_target_dir.text_field

    def upd(self):
        from_path = self.from_field.get("1.0", tk.END).strip()
        to_path = self.to_field.get("1.0", tk.END).strip() or FILEPATH
        ff = FinalFrame(self)

        try:
            Main.run(from_path, to_path)
        except BaseException:
            ff.set_text(format_exc())
            
        ff.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        
class ChooseBase:
    def mk_btn(self, master, text, cmd):
        return tk.Button(master, text=text, width=10, bg=PANEL_LIGHT, fg=TEXT, activebackground=ACCENT, activeforeground=TEXT, relief='solid', font=('Comic Sans MS', 10), command=cmd)
    
    def mk_field(self, master):
        return tk.Text(master, state=tk.DISABLED, bg=PANEL_LIGHT, fg=TEXT, relief='flat', width=29)
    
    def set_field(self, field: tk.Text, text):
        field['state'] = tk.NORMAL
        field.delete("1.0", tk.END)
        field.insert("1.0", text)
        field["state"] = tk.DISABLED
        

class ChooseDirFrame(tk.Frame, ChooseBase):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.pack_propagate(False)
        
        self.text_field = self.mk_field(self)
        self.text_field.pack(padx=10, pady=10, side="left")
        
        self.btn = self.mk_btn(self, "Zapret Folder", self.choose)
        self.btn.pack(side='right', padx=(0, 7), pady=10, ipadx=5, ipady=5)
    
    def choose(self):
        folder_path = filedialog.askdirectory(
            title='Choose Folder',
            initialdir=FILEPATH,
            mustexist=True
        )
        
        if folder_path:
            self.set_field(self.text_field, folder_path)


class ChooseTargetDirFrame(tk.Frame, ChooseBase):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.pack_propagate(False)
        
        self.text_field = self.mk_field(self)
        self.text_field.pack(padx=10, pady=10, side="left")
        
        self.btn = self.mk_btn(self, "End Folder", self.choose)
        self.btn.pack(side='right', padx=(0, 7), pady=10, ipadx=5, ipady=5)
    
    def choose(self):
        folder_path = filedialog.askdirectory(
            title='Choose Target',
            initialdir=FILEPATH,
            mustexist=True
        )
        
        if folder_path:
            self.set_field(self.text_field, folder_path)


class UpdateFrame(tk.Frame, ChooseBase):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.pack_propagate(False)
        
        btn = tk.Button(self, text="Update", width=10, height=4, bg=ACCENT, fg=TEXT, activebackground=PANEL, activeforeground=TEXT, relief='solid', font=('Comic Sans MS', 16), command=self.master.upd)
        btn.pack()
    

class FinalFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(bg=PANEL_LIGHT)
        
        self.text = tk.Text(self, bg=PANEL_LIGHT, state=tk.DISABLED, fg=TEXT, padx=20, pady=5)
        self.text.place(relx=0, y=30, relwidth=1, relheight=0.9)
        
        self.btn = tk.Button(self, command=self.destroy,text='Back', bg=ACCENT, fg=TEXT, activebackground=PANEL, activeforeground=TEXT, relief='solid', padx=20, height=1, font=('Comic Sans MS', 9))
        self.btn.place(x=10, rely=0)
        
        self.label = tk.Label(self, text="Result", bg=PANEL_LIGHT, fg=ACCENT, font=('Comic Sans MS', 13))
        self.label.place(relx=0.3, rely=0)
    
    def set_text(self, text):
        self.text['state'] = tk.NORMAL
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", text)
        self.text['state'] = tk.DISABLED

class GitHubClient:
    def __init__(self, api_url: str):
        self.api_url = api_url
        
    def get_latest_release(self) -> Release:
        response = get(self.api_url)
        response.raise_for_status()
        data = response.json()
        
        return Release(
            version=data["tag_name"],
            assets=data["assets"]
        )


@dataclass
class Release:
    version: str
    assets: list
      
        
class ZapretInstallation:
    def __init__(self, root: str):
        self.root = Path(root)
    
    @property
    def service_bat(self) -> Path:
        return self.root / "service.bat"
    
    @property
    def version(self) -> str:
        text = self.service_bat.read_text(encoding="utf-8", errors="ignore")
        v = search(r'"LOCAL_VERSION=(.*?)"', text)
        if not v:
            return '0.0.0'
        return v.group(1)
    
    @property
    def lists_dir(self) -> Path:
        return self.root / "lists"
    
    @property
    def utils_dir(self) -> Path:
        return self.root / "utils"
    

class ReleaseDownloader:
    def download(self, release: Release) -> bytes:
        target = None
        for asset in release.assets:
            if asset["name"].endswith(".rar"):
                target = asset
                break
                
        if target is None:
            raise Exception("RAR not found Error")

        download_url = target["browser_download_url"]
        response = get(download_url)
        response.raise_for_status()
        return response.content
    

class ArchiveExtractor:
    def __init__(self, temp_dir: str = TEMP_DIR):
        # self.temp_dir = Path(gettempdir()) / PROGRAMM_NAME
        self.temp_dir = temp_dir
    
    def extract(self, archive: bytes) -> Path:
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        with rarfile.RarFile(BytesIO(archive)) as rf:
            names = rf.namelist()
            first_name = names[0]
            top_folder = Path(first_name).parts[0]
            
            rf.extractall(self.temp_dir)
        
        return self.temp_dir / top_folder
    

class SettingsMigrator:
    def migrate(self, old: ZapretInstallation, new: ZapretInstallation):
        list_general = self.create_list(
            old.lists_dir / "list-general.txt",
            new.lists_dir / "list-general.txt"
        )
        list_exclude = self.create_list(
            old.lists_dir / "list-exclude.txt",
            new.lists_dir / "list-exclude.txt"
        )
        targets = self.create_list(
            old.utils_dir / "targets.txt",
            new.utils_dir / "targets.txt"
        )
        
        self.change_new(list_general, new.lists_dir / "list-general.txt")
        self.change_new(list_exclude, new.lists_dir / "list-exclude.txt")
        self.change_new(targets, new.utils_dir / "targets.txt")
        
        self.move_file(old.lists_dir / "ipset-all.txt", new.lists_dir / "ipset-all.txt")
        self.move_file(old.utils_dir / "check_updates.enabled", new.utils_dir / "check_updates.enabled")
        self.move_file(old.utils_dir / "game_filter.enabled", new.utils_dir / "game_filter.enabled")
    
    def create_list(self, old: Path, new: Path) -> list:
        lst = []
        with open(new, 'r') as f:
            for line in f.readlines():
                lst.append(line.strip())
        with open(old, 'r') as f:
            for l in f.readlines():
                lst.append(l.strip())
                
        return list(dict.fromkeys(lst))
    
    def change_new(self, lst: list, new: Path):
        with open(new, 'w') as f:
            for i in lst:
                f.write(f'{i}\n')
    
    def move_file(self, old_path: Path, new_path: Path):
        if os.path.exists(old_path):
            copy(old_path, new_path)
            
        elif os.path.exists(new_path):
            os.remove(new_path)
            
    
class Updater:
    def __init__(self, git: GitHubClient, zapret, downloader, extractor, migrator):
        self.git = git
        self.zapret = zapret
        self.downloader = downloader
        self.extractor = extractor
        self.migrator = migrator
    
    def update(self, to_path):
        release = self.git.get_latest_release()
        
        if not self.has_new_version(release.version, self.zapret.version):
            raise Exception("New Version Not Found Error")
        
        archive = self.downloader.download(release)
        new_path = self.extractor.extract(archive)
        new = ZapretInstallation(new_path)
        self.migrator.migrate(self.zapret, new)
        move(new.root, to_path)

    def has_new_version(self, new_version: str, curr_version: str) -> bool:
        return new_version != curr_version
        
        
class Main:
    def __init__(self):
        n = len(sys.argv)
        if n == 1:
            app = App()
            app.mainloop()
        elif n == 2:
            try:
                self.run(sys.argv[1])
            except Exception:
                BlankApp().mainloop()
        else:
            print("Something Went Wrong")
    
    @staticmethod
    def run(from_path, to_path=FILEPATH):
        git = GitHubClient("https://api.github.com/repos/Flowseal/zapret-discord-youtube/releases/latest")
        zapret = ZapretInstallation(from_path)
        updater = Updater(git, zapret, ReleaseDownloader(), ArchiveExtractor(), SettingsMigrator())
        
        updater.update(to_path)
 
 
if __name__ == '__main__':
    Main()