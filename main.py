import tkinter as tk
import random
import asyncio
import simpleaudio as sa
import tempfile
import speech_recognition as sr
import threading
from googletrans import Translator
from gtts import gTTS
from trivia import trivia
import soundfile as sf
from utils import categories, game_dialogs


class TriviaApp:
    def __init__(self, master):
        self.master = master
        self.is_listening = True
        self.language = 'id'
        self.questions = []
        self.disab_mode = False
        self.score = 0
        self.right_answers = 0
        self.wrong_answers = 0
        self.radio_buttons = {}
        master.title("Fun Trivia App")

        self.main_frame = tk.Frame(
            master, padx=20, pady=20, background="white", height=600, width=800)
        self.main_frame.pack_propagate(False)
        self.main_frame.pack()

        self.amount_label = tk.Label(self.main_frame, font=(
            "Courier New", 24), text="Pilih jumlah:")
        self.amount_label.pack(padx=5, pady=5)

        self.amount_var = tk.IntVar(self.main_frame, value=1)
        self.amount_menu = tk.OptionMenu(
            self.main_frame, self.amount_var, *range(1, 51))
        self.amount_menu.pack(padx=5, pady=5)

        self.difficulty_label = tk.Label(
            self.main_frame, font=("Courier New", 24), text="Pilih kesulitan:")
        self.difficulty_label.pack(padx=5, pady=5)

        self.difficulty_var = tk.StringVar(self.main_frame, value="easy")
        self.difficulty_menu = tk.OptionMenu(
            self.main_frame, self.difficulty_var, "easy", "medium", "hard")
        self.difficulty_menu.pack(padx=5, pady=5)

        self.category_label = tk.Label(
            self.main_frame, font=("Courier New", 24), text="Pilih kategori:")
        self.category_label.pack(padx=5, pady=5)

        self.categories = categories
        self.category_var = tk.StringVar(
            self.main_frame, value=self.categories[0]["name"])
        self.category_menu = tk.OptionMenu(
            self.main_frame, self.category_var, *[el["name"] for el in self.categories])
        self.category_menu.pack(padx=5, pady=5)

        self.type_label = tk.Label(self.main_frame, font=(
            "Courier New", 24), text="Pilih jenis:")
        self.type_label.pack(padx=5, pady=5)

        self.type_var = tk.StringVar(self.main_frame, value="multiple")
        self.type_menu = tk.OptionMenu(
            self.main_frame, self.type_var, "multiple", "boolean")
        self.type_menu.pack(padx=5, pady=5)

        self.disab_button = tk.Button(
            root, text="Mode disabilitas nonaktif", command=self.toggle_is_listening)
        self.disab_button.pack(padx=5, pady=5)

        self.generate_button = tk.Button(
            self.main_frame, text="Generate", command=self.generate_questions)
        self.generate_button.pack(padx=5, pady=5)

    def update_button_text(self):
        if self.is_listening:
            self.disab_button.config(text="Mode disabilitas nonaktif")
        else:
            self.disab_button.config(text="Mode disabilitas aktif")

    def toggle_is_listening(self):
        self.is_listening = not self.is_listening
        if not self.disab_mode:
            self.disab_mode = True
            q_dict = threading.Thread(
                target=self.dict_disab_mode)
            q_dict.start()
            self.expected_answer.extend(
                ["jumlah", "kesulitan", "kategori", "jenis", "main"])
        else:
            q_dict = threading.Thread(
                target=self.dict_disab_mode)
            q_dict.start()
        self.update_button_text()
        self.is_listening = not self.is_listening

    def dict_disab_mode(self):
        if self.disab_mode:
            self.say_message(game_dialogs["disabilitas"])
        else:
            self.say_message(
                "Mode disabilitas dinonaktifkan.")

    def create_questions_window(self):
        self.current_question_idx = 0
        self.trivia_start_wd = tk.Toplevel(
            self.master, background="white", padx=20, pady=20, height=600, width=800)
        self.trivia_start_wd.title("Questions Window")
        self.trivia_start_wd.pack_propagate(False)

        self.question_label = tk.Label(
            self.trivia_start_wd, font=("Courier New", 18), text=self.questions[self.current_question_idx]["question"])
        self.question_label.pack()

        self.radio_group = tk.Frame(self.trivia_start_wd)
        self.radio_group.pack()

        incorrect_answers = self.questions[self.current_question_idx]["incorrect_answers"]

        if self.type_var.get() == "boolean":
            options = ["True", "False"]
        else:
            options = incorrect_answers + \
                [self.questions[self.current_question_idx]["correct_answer"]]
            random.shuffle(options)

        if self.disab_mode:
            q_dict = threading.Thread(
                target=self.dict_option_question, args=(options, self.questions[self.current_question_idx]["question"]))
            q_dict.start()

        self.answer_var = tk.StringVar(self.trivia_start_wd, value=options[0])
        for option in options:
            rb = tk.Radiobutton(
                self.radio_group, variable=self.answer_var, text=option, value=option)
            if self.disab_mode:
                self.radio_buttons[option] = rb
            rb.pack()

        next_button = tk.Button(self.trivia_start_wd,
                                text="Next", command=self.next_question)
        next_button.pack()

    def dict_option_question(self, options, question):
        self.is_listening = not self.is_listening
        prefixes = ['1', '2', '3', '4'] if len(options) == 4 else ['1', '2']
        if "opsi" not in self.expected_answer and "lanjut" not in self.expected_answer:
            self.expected_answer += ["opsi", "lanjut"]

        self.say_message(question)
        for option in options:
            prefix = prefixes.pop(0) if prefixes else '1'

            self.say_message(f"{prefix},{option}")

        self.is_listening = not self.is_listening

    def dict_answer(self, sel_idx, key):
        self.is_listening = not self.is_listening

        self.say_message(
            f"Jawaban diubah menjadi {sel_idx + 1},{key}")

        self.is_listening = not self.is_listening

    def dict_corrections(self):
        self.is_listening = not self.is_listening

        self.say_message(
            f"Jawaban betul: {self.right_answers} dari {self.amount_var.get()}")

        self.say_message(f"Skor akhir:{self.score}")

        for i, answer in enumerate(self.questions):
            label_text = f"{i + 1}. {answer['question']}\Jawaban: {answer['correct_answer']}"
            self.say_message(label_text)

        self.say_message("Katakan 'kembali' untuk kembali ke menu utama.")
        self.expected_answer.append("kembali")

        self.is_listening = not self.is_listening

    def next_question(self):
        self.radio_buttons = {}
        if self.questions[self.current_question_idx]["correct_answer"] == self.answer_var.get():
            self.right_answers += 1
        else:
            self.wrong_answers += 1

        if self.current_question_idx < self.amount_var.get() - 1:
            self.current_question_idx += 1
            self.question_label.config(
                text=self.questions[self.current_question_idx]["question"])
            widgets = self.radio_group.winfo_children()
            for widget in widgets:
                widget.destroy()

            incorrect_answers = self.questions[self.current_question_idx]["incorrect_answers"]

            if self.type_var.get() == "boolean":
                options = ["True", "False"]
            else:
                options = incorrect_answers + \
                    [self.questions[self.current_question_idx]["correct_answer"]]
                random.shuffle(options)

            if self.disab_mode:
                q_dict = threading.Thread(
                    target=self.dict_option_question, args=(options, self.questions[self.current_question_idx]["question"]))
                q_dict.start()

            self.answer_var = tk.StringVar(
                self.trivia_start_wd, value=options[0])
            for option in options:
                rb = tk.Radiobutton(
                    self.radio_group, variable=self.answer_var, text=option, value=option)
                if self.disab_mode:
                    self.radio_buttons[option] = rb
                rb.pack()
        else:
            point_per_question = 100 / self.amount_var.get()
            self.score = "{:.2f}".format(
                point_per_question * self.right_answers)

            self.trivia_start_wd.destroy()

            self.details_wd = tk.Toplevel(
                self.master, background="white", padx=20, pady=20, height=500, width=1000)
            self.details_wd.title("Evaluation Window")
            self.details_wd.pack_propagate(False)

            total_label = tk.Label(
                self.details_wd, text=f"Jawaban betul: {self.right_answers}/{self.amount_var.get()}", font=("Courier New", 24))
            total_label.pack()

            score_label = tk.Label(
                self.details_wd, text=f"Skor akhir: {self.score}", font=("Courier New", 24))
            score_label.pack()

            if self.disab_mode:
                q_dict = threading.Thread(
                    target=self.dict_corrections)
                q_dict.start()

            for i, answer in enumerate(self.questions):
                label_text = f"{i + 1}. {answer['question']}\Jawaban: {answer['correct_answer']}"
                tk.Label(
                    self.details_wd, text=label_text, font=("Courier New", 16)).pack()
            back_button = tk.Button(self.details_wd,
                                    text="Back", command=self.details_wd.destroy)
            back_button.pack()

    def generate_questions(self):
        if not self.disab_mode:
            self.is_listening = False

        cat_idx = 0
        for idx, el in enumerate(self.categories):
            if el["name"] == self.category_var.get():
                cat_idx = idx
                break
        try:
            loop = asyncio.get_event_loop()
            self.questions = loop.run_until_complete(trivia.question(
                amount=self.amount_var.get(), category=cat_idx, difficulty=self.difficulty_var.get(), quizType=self.type_var.get()))

            for idx in range(len(self.questions)):
                temp = self.questions[idx]["question"]
                self.questions[idx]["question"] = self.translate(temp)

        except:
            tk.Label(self.main_frame, text="There is an error when fetching questions from the API server!", font=(
                "Courier New", 14)).pack()

        if self.questions:
            self.create_questions_window()

    def translate(self, text):
        tr_data = None
        translator = Translator(service_urls=['translate.google.com'])

        if isinstance(text, str):
            tr_data = text
        elif isinstance(text, list):
            tr_data.extend(text)

        translations = translator.translate(tr_data, dest="id")

        if isinstance(text, str):
            return translations.text
        elif isinstance(text, list):
            for el in translations:
                return el.text

        return "Translation error occured."

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        self.expected_answer = ["disabilitas"]

        while True:
            if self.is_listening:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source)

                    try:
                        text = recognizer.recognize_google(
                            audio, language=self.language)
                        print(text)

                        if text or int(text) in self.expected_answer:
                            if not self.disab_mode and "disabilitas" in text.lower().split():
                                self.disab_button.config(
                                    text="Mode disabilitas aktif")
                                self.say_message(game_dialogs["disabilitas"])
                                self.disab_mode = True
                                self.expected_answer.extend(
                                    ["jumlah", "kesulitan", "kategori", "jenis", "main"])
                            elif self.disab_mode and "disabilitas" in text.lower().split():
                                self.disab_button.config(
                                    text="Mode disabilitas nonaktif")
                                self.say_message(
                                    "Mode disabilitas dinonaktifkan.")
                                self.update_button_text()
                                break

                            if self.disab_mode:
                                number_mapping = {
                                    "nol": 0,
                                    "satu": 1,
                                    "dua": 2,
                                    "tiga": 3,
                                    "empat": 4,
                                    "lima": 5,
                                    "enam": 6,
                                    "tujuh": 7,
                                    "delapan": 8,
                                    "sembilan": 9
                                }
                                if "jumlah" in text.lower().split():
                                    n_opts = [i for i in range(1, 51)]
                                    n_opts.append("jml_pick")
                                    self.say_message(game_dialogs["jumlah"])
                                    self.expected_answer.extend(n_opts)
                                elif "jml_pick" in self.expected_answer and "cat_pick" not in self.expected_answer and "opsi" not in self.expected_answer and text.lower() in number_mapping.keys():
                                    if not text.isdigit():
                                        self.amount_var.set(
                                            number_mapping[text.lower()])
                                        self.say_message(
                                            f"Berhasil mengganti jumlah ke {number_mapping[text.lower()]}")
                                    else:
                                        self.amount_var.set(int(text))
                                        self.say_message(
                                            f"Berhasil mengganti jumlah ke {int(text)}")
                                    for item in self.expected_answer[:]:
                                        if item != "disabilitas" or item != "jumlah" or item != "kategori" or item != "kesulitan" or item != "jenis" or item != "main":
                                            self.expected_answer.remove(item)
                                elif "kesulitan" in text.lower().split():
                                    self.expected_answer.extend(
                                        ["mudah", "sedang", "sulit"])
                                    self.say_message(game_dialogs['kesulitan'])
                                elif "mudah" and "sedang" and "sulit" in self.expected_answer and text.lower() == "mudah" or text.lower() == "sedang" or text.lower() == "sulit":
                                    match text.lower():
                                        case "mudah":
                                            self.difficulty_var.set("easy")
                                        case "sedang":
                                            self.difficulty_var.set("medium")
                                        case "sulit":
                                            self.difficulty_var.set("hard")
                                    self.say_message(
                                        f"Berhasil mengubah kesulitan ke {text.lower()}")
                                    for item in self.expected_answer[:]:
                                        if item != "disabilitas" or item != "jumlah" or item != "kategori" or item != "kesulitan" or item != "jenis" or item != "main":
                                            self.expected_answer.remove(item)
                                elif "kategori" in text.lower().split():
                                    nopt = [i for i in range(1, 25)]
                                    nopt.append("cat_pick")
                                    self.say_message(game_dialogs["kategori"])
                                    self.expected_answer.extend(nopt)
                                elif "cat_pick" in self.expected_answer and text.lower() in number_mapping.keys() or text.isdigit():
                                    new_opts = ["iya", "tidak"]
                                    self.expected_answer.extend(new_opts)
                                    if text.isdigit():
                                        self.temp_cat = categories[int(
                                            text)-1]['name']
                                        td_cat = self.translate(categories[int(
                                            text)-1]['name'])
                                        self.say_message(
                                            f"Apakah anda yakin akan memilih {td_cat}? Katakan iya atau tidak.")
                                    else:
                                        self.temp_cat = categories[number_mapping[text.lower(
                                        )]]["name"]
                                        td_cat = self.translate(
                                            categories[number_mapping[text.lower()]]["name"])
                                        self.say_message(
                                            f"Apakah anda yakin akan memilih {td_cat}? Katakan iya atau tidak.")
                                elif "cat_pick" in self.expected_answer and text.lower() in ["iya", "tidak"]:
                                    match text.lower():
                                        case "iya":
                                            self.category_var.set(
                                                self.temp_cat)
                                            for item in self.expected_answer[:]:
                                                if item != "disabilitas" or item != "jumlah" or item != "kategori" or item != "kesulitan" or item != "jenis" or item != "main":
                                                    self.expected_answer.remove(
                                                        item)
                                            self.say_message(
                                                f"Sukses mengganti kategori menjadi {self.translate(self.temp_cat)}")
                                        case "tidak":
                                            for item in self.expected_answer[:]:
                                                if item == "iya" or item == "tidak":
                                                    self.expected_answer.remove(
                                                        item)
                                            self.say_message(
                                                game_dialogs["kategori"])
                                    self.temp_cat = None
                                elif "jenis" in text.lower().split():
                                    self.expected_answer.extend(
                                        ["pilihan ganda", "benar atau salah"])
                                    self.say_message(game_dialogs['jenis'])
                                elif "pilihan ganda" and "benar atau salah" in self.expected_answer and text.lower() == "pilihan ganda" or text.lower() == "benar atau salah":
                                    match text.lower():
                                        case "pilihan ganda":
                                            self.type_var.set("multiple")
                                        case "benar atau salah":
                                            self.type_var.set("boolean")
                                    self.say_message(
                                        f"Berhasil mengganti jenis ke {text.lower()}")
                                    for item in self.expected_answer[:]:
                                        if item != "disabilitas" or item != "jumlah" or item != "kategori" or item != "kesulitan" or item != "jenis" or item != "main":
                                            self.expected_answer.remove(item)
                                elif "main" in text.lower().split():
                                    self.generate_button.invoke()
                                elif "lanjut" in self.expected_answer and "lanjut" in text.lower().split():
                                    self.next_question()
                                elif "opsi" in self.expected_answer and text.lower() in number_mapping.keys() or text.lower() in number_mapping.values():
                                    temp_values = list(
                                        self.radio_buttons.values())
                                    rb_items = list(
                                        self.radio_buttons.items())
                                    sel_idx = int(text) - 1 if text.isdigit(
                                    ) else number_mapping[text.lower()] - 1

                                    key = rb_items[sel_idx][0]

                                    temp_values[sel_idx].invoke()
                                    q_dict = threading.Thread(
                                        target=self.dict_answer, args=(sel_idx, key))
                                    q_dict.start()
                                elif "kembali" in self.expected_answer and "kembali" in text.lower().split():
                                    for item in self.expected_answer[:]:
                                        if item != "disabilitas" or item != "jumlah" or item != "kategori" or item != "kesulitan" or item != "jenis" or item != "main":
                                            self.expected_answer.remove(item)

                                    self.details_wd.destroy()
                                    self.say_message(
                                        "Telah kembali ke menu utama.")
                    except sr.UnknownValueError:
                        if not self.disab_mode:
                            continue
                        self.say_message("Tidak dapat mengenali perintah.")
                    except sr.RequestError as e:
                        self.say_message(
                            f"Error terjadi pada saat mendengarkan perintah: {e}")

    def say_message(self, text):
        tts = gTTS(text=text, lang=self.language)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_file:
            temp_wav = temp_file.name
            temp_pcm = temp_wav.replace(".wav", ".pcm")
            tts.save(temp_pcm)
            sf.write(temp_wav, sf.read(temp_pcm)[0], 22050, 'PCM_16')
            wave_obj = sa.WaveObject.from_wave_file(temp_wav)
            play_obj = wave_obj.play()
            play_obj.wait_done()


def back_listening_thread(recognize_speech):
    back_listening = threading.Thread(target=recognize_speech)
    back_listening.daemon = True

    back_listening.start()


if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)

    app = TriviaApp(root)
    back_listening_thread(app.recognize_speech)
    root.mainloop()
