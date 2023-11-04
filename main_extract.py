from tkinter import Button, Label, Spinbox, BooleanVar, NW, W, Canvas, Frame, Entry, YES, LAST, NS, N, Checkbutton, E, \
	Scrollbar, VERTICAL
from tkinter.filedialog import askdirectory, askopenfilenames
from tkinter.messagebox import showerror, askyesno
from tkinter.ttk import Combobox
from plyer import notification
from PIL import Image, ImageTk
from datetime import datetime
from threading import Thread
from tkinterdnd2 import *
from _tkinter import TclError

import shutil
import cv2
import os

MAX_THREAD_NUMBER = 3
SAVE_FORMAT_LIST = ("png", "jpg", "bmp")


def extract_img_thread():
	while files:
		try:
			file = files.pop(0)
		except IndexError:
			break
		extracting_files.append(file)
		date = str(datetime.now())
		is_size_modified = file.out_size != (file.width, file.height)
		fps_out = int(file.FPS_choise_sb.get())

		index_in = -1
		index_out = -1

		while True:
			success = file.video.grab()
			if not success:
				break
			index_in += 1

			out_due = int(index_in / file.fps * fps_out)
			if out_due > index_out:
				success, frame = file.video.retrieve()
				if not success:
					break
				index_out += 1
				file.extract_state = index_out
				imgname = file.out_name_e.get().replace("$index$", str(index_out)).replace("$videoName$",
																						   file.plain_filename).replace(
					"$time$", date)
				if success:
					if index_out % 10 == 0:
						file.tk_image = ImageTk.PhotoImage(Image.fromarray(
							cv2.cvtColor(cv2.resize(frame, (160, 90), interpolation=cv2.INTER_CUBIC),
										 cv2.COLOR_BGR2RGB)))
						file.img_l["image"] = file.tk_image
					if is_size_modified:
						frame = cv2.resize(frame, (file.width, file.height), interpolation=cv2.INTER_CUBIC)
					cv2.imwrite(file.out_dir + imgname + "." + output_format_cbb.get(), frame)
		extracting_files.remove(file)
		file.extract_state = -1
		file.loading_l["text"] = "     "
		file.delete()


def extract():
	global extracting
	start_btn.config(state="disabled")
	output_format_cbb.config(state="disabled")
	output_dir_btn.config(state="disabled")
	extracting = True
	for i in files:
		i.update_reso_choise()
		i.update_spin_box(False)
		i.delete_btn_c["state"] = "disabled"
		i.out_name_e["state"] = "disabled"
		i.FPS_choise_sb["state"] = "disabled"
		i.create_dir_cb["state"] = "disabled"
		i.custo_res_cb["state"] = "disabled"
		i.reso_cbb["state"] = "disabled"
		i.reso_x_sb["state"] = "disabled"
		i.reso_y_sb["state"] = "disabled"
		i.extract_state = 0
		i.loading_l.config(text="Attente")
		if i.custo_res_var.get():
			i.out_size = (int(i.reso_x_sb.get()), int(i.reso_y_sb.get()))
		else:
			i.out_size = i.av_export_size[0][i.reso_cbb.current()]

		if i.create_dir_var.get():
			if os.path.isdir(output_dir_path + "/" + i.plain_filename):
				if os.listdir(output_dir_path + "/" + i.plain_filename):
					if askyesno("Supprimer ?",
								"Le dossier \"" + output_dir_path + "/" + i.plain_filename + "\" contient déjà des fichiers. Voulez vous les supprimer ?"):
						if askyesno("Sûr ?",
									"Etes-vous sûr de vouloir supprimer les fichiers du dossier \"" + output_dir_path + "/" + i.plain_filename + "\" ? Il ne seront pas récupérables !"):
							shutil.rmtree(output_dir_path + "/" + i.plain_filename)
							os.mkdir(output_dir_path + "/" + i.plain_filename)

			else:
				os.mkdir(output_dir_path + "/" + i.plain_filename)
			i.out_dir = output_dir_path + "/" + i.plain_filename + "/"
		else:
			if os.listdir(output_dir_path + "/"):
				if askyesno("Supprimer ?",
							"Le dossier \"" + output_dir_path + "\" contient déja des fichiers. Voulez vous les supprimer ?"):
					if askyesno("Sûr ?",
								"Etes-vous sûr de vouloir supprimer les fichiers du dossier \"" + output_dir_path + "\" ? Il ne seront pas récupérables !"):
						shutil.rmtree(output_dir_path)
						os.mkdir(output_dir_path)
			i.out_dir = output_dir_path + "/"
	for t in range(MAX_THREAD_NUMBER):
		Thread(target=extract_img_thread).start()


def check_threads_state(loop):
	global extracting
	for i in extracting_files.copy():
		i.update_loading()
		try:
			i.loading_l["text"] = str(round(i.extract_state / i.modified_frame_count * 100, 1)) + " %"
		except TclError:
			pass
	if loop:
		main_wd.after(100, lambda: check_threads_state(True))
	if (not files) and (not extracting_files):
		output_format_cbb.config(state="readonly")
		output_dir_btn.config(state="normal")
		if extracting:
			update_start_btn()
			notification.notify(
				app_name="VideoSplitter",
				title="Extraction finie !",
				message="L'extraction des images est terminée !",
				timeout=10
			)
		extracting = False


def frame_size(event):
	canvas_width = event.width
	canvas_height = event.height
	v_list_c.itemconfig(v_list_c_f, width=canvas_width, height=canvas_height)


def on_frame_configure(*_):
	if files:
		v_list_c.pack(expand=YES, anchor=NW, fill="both", padx=20, pady=20)
	else:
		v_list_c.pack_forget()
	v_list_c.configure(scrollregion=v_list_c.bbox("all"))


def load_files(*_):
	if not extracting:
		imported_files = askopenfilenames()
		main_wd.update()
		if imported_files:
			for i in imported_files:
				file = File(i)
				files.append(file)
				if "frame" not in file.__dict__:
					files.remove(file)
		update_start_btn()


def drop_file(e):
	if not extracting:
		for i in e.data[1:len(e.data) - 1].split("} {"):
			file = File(i)
			files.append(file)
			if "frame" not in file.__dict__:
				files.remove(file)
		update_start_btn()


def update_import_rect(*_):
	v_import_c.delete("importRect")
	round_rectangle(v_import_c, 10, 10, v_import_c.winfo_width() - 25, v_import_c.winfo_height() - 10, dash=(100, 100),
					fill="", outline="grey", width=5, radius=50, tags="importRect")
	if not files:
		round_rectangle(v_import_c, v_import_c.winfo_width() / 2 - 80, v_import_c.winfo_height() / 2 - 50,
						v_import_c.winfo_width() / 2 + 80, v_import_c.winfo_height() / 2 + 50, fill="", outline="grey",
						width=8, radius=50, tags="importRect")
		v_import_c.create_line(v_import_c.winfo_width() / 2, v_import_c.winfo_height() / 2 - 90,
							   v_import_c.winfo_width() / 2,
							   v_import_c.winfo_height() / 2 + 10, width=30, arrow="last", arrowshape=(25, 25, 15),
							   fill='grey', tags="importRect")


def round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
	points = [x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius, x2,
			  y1 + radius, x2, y2 - radius, x2, y2 - radius, x2, y2, x2 - radius, y2, x2 - radius, y2, x1 + radius, y2,
			  x1 + radius, y2, x1, y2, x1, y2 - radius, x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1, y1]

	return canvas.create_polygon(points, **kwargs, smooth=True)


def draw_delete_btn(canvas: Canvas, x, y, size, **kwargs):
	return canvas.create_line(x, y, x + size, y + size, tags="drawing", **kwargs), canvas.create_line(x + size, y, x, y + size, tags="drawing", **kwargs)


def select_directory():
	global output_dir_path
	output_dir_path = askdirectory()
	update_start_btn()
	main_wd.update()
	if output_dir_path:
		output_dir_l["text"] = output_dir_path
	else:
		output_dir_l["text"] = "Non selectionné"


def update_start_btn():
	if not extracting:
		if output_dir_path and files:
			start_btn["state"] = "normal"
		else:
			start_btn["state"] = "disabled"


class File:
	def __init__(self, filepath):
		self.current_jobs = []
		self.extract_state = -1
		self.filepath = filepath
		self.out_dir = ""
		self.out_size = (-1, -1)
		self.loading_anim_state = 0
		self.video = cv2.VideoCapture(filepath)
		self.frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
		if self.frame_count <= 1:
			showerror("Fichier incompatible !",
					  "Le fichier que vous avez importé semble ne pas être une vidéo ou est corrompu. Merci de vérifier votre fichier.")
			self.delete()
			return
		self.fps = self.video.get(cv2.CAP_PROP_FPS)
		duration = self.frame_count / self.fps
		self.modified_frame_count = self.frame_count
		self.video.set(1, min(100, self.frame_count - 1))
		success, image = self.video.read()
		self.video.set(1, 0)
		tk_image_ = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

		self.width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
		self.height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

		self.av_export_size = self.get_available_size()

		self.tk_image = ImageTk.PhotoImage(tk_image_.resize((160, 90)))
		self.frame = Frame(v_list_f)

		self.delete_btn_c = Canvas(self.frame, width=25, height=25)
		draw_delete_btn(self.delete_btn_c, 2, 2, 21, width=3, fill="red")
		self.delete_btn_c.grid(row=0, column=0, padx=5)
		self.delete_btn_c.bind("<Button-1>", self.delete)

		self.img_l = Label(self.frame, image=self.tk_image)
		self.img_l.grid(row=0, column=1)

		self.text_f = Frame(self.frame)

		path = filepath.replace("\\", "/").split("/")
		self.filename = path[len(path) - 1]
		self.plain_filename = self.filename[:self.filename.rfind(".")]
		self.file_name_l = Label(self.text_f, text=self.filename, font=("Calibri", 15, "bold"), width=30,
								 justify="left", anchor="w")
		self.file_name_l.grid(row=0, column=0, sticky=NW)

		self.lenght_l = Label(self.text_f,
							  text="Durée : " + str(int(duration / 3600)) + "h " + str(int(duration / 60)) + "m " + str(
								  round(duration % 60, 3)) + "s", font=("Calibri", 12))
		self.lenght_l.grid(row=1, column=0, sticky=NW)

		self.FPS_base_l = Label(self.text_f, text="FPS : " + str(self.fps), font=("Calibri", 12))
		self.FPS_base_l.grid(row=2, column=0, sticky=NW)

		self.arrow_c = Canvas(self.text_f, width=70, height=10)
		self.arrow_c.create_line(0, 52, 70, 52, arrow=LAST, width=20, arrowshape=(25, 25, 15), fill='grey')
		self.arrow_c.grid(row=0, column=1, rowspan=3, sticky=NS, padx=10)
		self.loading_l = Label(self.text_f, text="     ", font=("Arial", 14, "bold"))
		self.loading_l.grid(row=0, column=1, rowspan=3, sticky=N, padx=10)

		self.out_name_e = Entry(self.text_f)
		self.out_name_e.grid(row=0, column=2, pady=5)
		self.out_name_e.insert(0, "$videoName$ frm $index$")  # $videoName$   $index$   $time$

		self.FPS_choise_c = Canvas(self.text_f)
		self.FPS_choise_l = Label(self.FPS_choise_c, text="FPS : ", font=("Calibri", 12))
		self.FPS_choise_sb = Spinbox(self.FPS_choise_c, from_=1, to=int(self.fps), width=4)
		self.FPS_choise_l.grid(row=0, column=0)
		self.FPS_choise_sb.grid(row=0, column=1)
		self.FPS_choise_sb.insert(0, int(self.fps))
		self.FPS_choise_c.grid(row=1, column=2)

		self.total_frames_l = Label(self.text_f, text="Nbr d'img : " + str(self.frame_count), font=("Calibri", 12))
		self.total_frames_l.grid(row=2, column=2, sticky=NW)

		self.create_dir_var = BooleanVar()
		self.create_dir_cb = Checkbutton(self.text_f, text="Créer dossier ?", variable=self.create_dir_var)
		self.create_dir_cb.grid(row=0, column=3, padx=5, sticky=W)

		self.custo_res_var = BooleanVar()
		self.custo_res_cb = Checkbutton(self.text_f, text="Res. perso. ?", variable=self.custo_res_var,
										command=self.update_reso_choise)
		self.custo_res_cb.grid(row=1, column=3, padx=5, sticky=W)
		self.reso_cbb = Combobox(self.text_f, values=self.av_export_size[1], state="readonly", width=12,
								 justify="center")
		self.reso_cbb.current(0)
		self.reso_cbb.grid(row=2, column=3, padx=5, sticky=W)

		self.custo_res_c = Canvas(self.text_f)
		self.reso_x_sb = Spinbox(self.custo_res_c, from_=1, to=self.width, width=6)
		self.reso_x_sb.insert(0, int(self.width))
		self.reso_y_sb = Spinbox(self.custo_res_c, from_=1, to=self.height, width=6)
		self.reso_y_sb.insert(0, int(self.height))
		Label(self.custo_res_c, text=" X ").grid(row=0, column=1)
		self.reso_x_sb.grid(row=0, column=0)
		self.reso_y_sb.grid(row=0, column=2)

		self.text_f.grid(row=0, column=2, sticky=NW, padx=15, pady=5)

		self.frame.pack(anchor=NW, expand=YES, pady=5)

		self.update_spin_box(True)

	def update_spin_box(self, loop):
		if not (self.FPS_choise_sb.get().isdigit() and self.fps >= int(self.FPS_choise_sb.get()) >= 1):
			self.FPS_choise_sb.delete(0, "end")
			self.FPS_choise_sb.insert(0, int(self.fps))
		self.modified_frame_count = int(self.frame_count / self.fps * int(self.FPS_choise_sb.get()))
		self.total_frames_l["text"] = "Nbr d'img : " + str(self.modified_frame_count)
		if not (self.reso_x_sb.get().isdigit() and self.width >= int(self.reso_x_sb.get()) >= 1):
			self.reso_x_sb.delete(0, "end")
			self.reso_x_sb.insert(0, int(self.width))
		if not (self.reso_y_sb.get().isdigit() and self.height >= int(self.reso_y_sb.get()) >= 1):
			self.reso_y_sb.delete(0, "end")
			self.reso_y_sb.insert(0, int(self.height))
		if loop:
			self.current_jobs.append(self.text_f.after(200, lambda: self.update_spin_box(True)))

	def get_available_size(self):
		i = 1
		ret = [[], []]
		while not (
				(float(int(self.width / i)) != (self.width / i)) or (float(int(self.height / i)) != (self.height / i))):
			ret[0].append((int(self.width / i), int(self.height / i)))
			ret[1].append((str(int(self.width / i)) + " X " + str((int(self.height / i)))))
			i *= 2
		return ret

	def delete(self, *_):
		for i in self.current_jobs:
			if i is not None:
				self.text_f.after_cancel(i)
		if self.extract_state == -1:
			if "frame" in self.__dict__:
				for i in self.frame.winfo_children():
					i.destroy()
				self.frame.destroy()
				if self in files:
					files.remove(self)
			update_import_rect()
			update_start_btn()
			on_frame_configure()

	def update_reso_choise(self):
		if self.custo_res_var.get():
			self.reso_cbb.grid_forget()
			self.custo_res_c.grid(row=2, column=3, padx=5, sticky=W)
		else:
			self.reso_cbb.grid(row=2, column=3, padx=5, sticky=W)
			self.custo_res_c.grid_forget()

	def update_loading(self):
		self.delete_btn_c.delete("drawing")
		if self.loading_anim_state == 0:
			self.delete_btn_c.create_oval(4, 4, 21, 21, dash=(2, 2), outline="grey", width=4, tags="drawing")
			self.delete_btn_c.update()
			self.loading_anim_state = 1
		else:
			self.delete_btn_c.create_oval(4, 4, 21, 21, outline="grey", width=4, tags="drawing")
			self.delete_btn_c.update()
			self.loading_anim_state = 0
		main_wd.update()


main_wd = TkinterDnD.Tk()
main_wd.title("VideoSplitter v2")

main_wd.geometry("1000x500")

v_import_c = Canvas(main_wd)
v_list_c = Canvas(v_import_c)

main_wd.bind("<Configure>", update_import_rect)

v_list_scb = Scrollbar(v_import_c, orient=VERTICAL)
v_list_scb.pack(side="right", fill="y")
v_list_scb.config(command=v_list_c.yview)

v_list_c.config(yscrollcommand=v_list_scb.set)

v_list_f = Frame(v_list_c)
v_list_c_f = v_list_c.create_window((0, 0), anchor='nw', window=v_list_f)

v_import_c.pack(expand=YES, anchor=NW, fill="both")

v_list_f.bind("<Configure>", on_frame_configure)
v_list_c.bind('<Configure>', lambda _: v_list_c.configure(scrollregion=v_import_c.bbox("all")))

v_import_c.drop_target_register(DND_FILES)
v_import_c.dnd_bind('<<Drop>>', drop_file)
v_import_c.bind("<Button-1>", load_files)
v_list_c.dnd_bind('<<Drop>>', drop_file)
v_list_c.bind("<Button-1>", load_files)

v_import_c.bind_all("<MouseWheel>", lambda event: v_list_c.yview_scroll(int(-1 * (event.delta / 120)), "units"))

output_dir_path = ""

extracting = False

editor_f = Frame()
editor_f.grid_columnconfigure(0, weight=1)
editor_f.grid_columnconfigure(2, weight=1)
dir_choise_f = Frame(editor_f)
output_dir_btn = Button(dir_choise_f, text="Dossier de sortie", font=("Calibri", 15, "bold"), relief="groove",
						command=select_directory)
output_dir_btn.pack()
output_dir_l = Label(dir_choise_f, text="Non selectionné", width=20, justify="left", anchor=E)
output_dir_l.pack()
dir_choise_f.grid(row=0, column=0, sticky="W", padx=70)

Label(editor_f, text="Format de sortie:", font=("Arial", 12)).grid(row=0, column=1)
output_format_cbb = Combobox(editor_f, values=SAVE_FORMAT_LIST, state="readonly", font=("Arial", 12), width=5,
							 justify="center")
output_format_cbb.current(0)
output_format_cbb.grid(row=0, column=2, sticky="w", padx=5)

start_btn = Button(editor_f, text="Extraire ►", font=("Calibri", 30, "bold"), relief="groove", state="disabled",
				   command=extract)
start_btn.grid(row=0, column=3, padx=20)

editor_f.pack(fill="x", anchor="center", pady=10)

files = []
extracting_files = []

check_threads_state(True)

update_import_rect()
v_list_c.configure(scrollregion=v_import_c.bbox("all"))

main_wd.mainloop()
