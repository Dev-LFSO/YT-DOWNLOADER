import tkinter as tk
from tkinter import messagebox, filedialog
from pytube import YouTube
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from os import path, remove
import moviepy.editor as mp
import threading


class Menu:
    def __init__(self):
        self.url = str
        self.yt = YouTube
        self.entry_url = tk.Entry

        self.ICON = 'imgs/YT.ico'
        self.IMAGE = Image.open('imgs/YT.png')
        self.FONTE_TEXT = 'Youtube Sans'

        self.config_janela()

    def config_janela(self):
        """
        Configura a janela principal do aplicativo.
        """
        def check():
            """
            Atualiza as opções da combobox com base na seleção do checkbox 'Apenas áudio'.
            """
            if self.combobox['values'][0] != 'Webm':
                self.combobox.set('')
                self.combobox['values'] = ['Webm', 'Mp3']
            else:
                self.combobox.set('')
                self.combobox['values'] = ['144p', '240p', '360p', '480p', '720p (HD)', '1080p (FHD)', '1440p (QHD)', '2160p (4K)']

        def on_progress(stream, chunk, bytes_remaining):
            """
            Atualiza a barra de progresso com base no progresso do download.
            """
            total_size = stream.filesize
            bytes_downloaded = total_size - bytes_remaining
            percentage_of_completion = bytes_downloaded / total_size * 100
            self.progress_bar['value'] = percentage_of_completion
            self.progress_window.update_idletasks()

        def exec_botao_dir():
            """
            Abre um diálogo para selecionar o diretório de download.
            """
            destino = filedialog.askdirectory()
            if destino:
                self.dire.set(destino)

        def exec_botao():
            """
            Desabilita o botão de download e inicia o processo de download em uma nova thread.
            """
            self.download_button.config(state=tk.DISABLED)
            thread = threading.Thread(target=download_video)
            thread.start()

        def safe_filename(title):
            """
            Remove ou substitui caracteres inválidos em um título para criar um nome de arquivo seguro.
            """
            import re
            # Substitui caracteres inválidos por um hífen
            return re.sub(r'[<>:"/\\|?*]', '-', title)

        def download_video():
            """
            Baixa o vídeo ou o áudio do YouTube com base na URL e nas opções fornecidas.
            """
            try:
                if not self.dire.get():
                    self.dire.set('.')

                url = self.entry_url.get().strip()
                formato = self.combobox.get()

                if '(' in formato:
                    formato = formato[0:formato.index('(')-1]

                yt = YouTube(url, on_progress_callback=on_progress)

                self.progress_window = tk.Toplevel(self.janela)
                self.progress_window.iconbitmap(self.ICON)
                self.progress_window.title("Progresso do Download")
                self.progress_window.geometry("400x100+800+300")
                tk.Label(self.progress_window, text="Baixando...", font=(self.FONTE_TEXT, 20)).pack(pady=10)
                self.progress_bar = ttk.Progressbar(self.progress_window, length=300, mode='determinate')
                self.progress_bar.pack(pady=10)

                if self.so_audio.get():
                    file_name = f"{safe_filename(yt.title)} ({formato}).mp3" if formato == 'Mp3' else f"{safe_filename(yt.title)} ({formato}).webm"
                    stream = yt.streams.filter(only_audio=True).first()
                    if stream:
                        try:
                            stream.download(filename=file_name, output_path=f'{self.dire.get()}/')
                            messagebox.showinfo('Sucesso!', f'O áudio -> {safe_filename(yt.title)} foi baixado com sucesso!')
                        except AttributeError:
                            messagebox.showwarning('Aviso', f'Não foi possível baixar o áudio -> {safe_filename(yt.title)}.\nTente outro formato!')
                    else:
                        messagebox.showwarning('Aviso', 'Stream de áudio não encontrado!')

                else:
                    file_name = f"{safe_filename(yt.title)} ({formato}).mp4"
                    for video in yt.streams.filter(progressive=True).all():
                        if video.resolution == formato:
                            stream = yt.streams.get_highest_resolution()
                            try:
                                stream.download(filename=file_name, output_path=f'{self.dire.get()}/')
                                messagebox.showinfo('Sucesso!', f'O vídeo -> {safe_filename(yt.title)} foi baixado com sucesso!')
                            except AttributeError:
                                messagebox.showwarning('Aviso', f'Não foi possível baixar o vídeo -> {safe_filename(yt.title)} na resolução -> {formato}.\nTente outra resolução!')
                    if not path.exists(f'{self.dire.get()}/{file_name}'):
                        video_stream  = yt.streams.filter(res=formato, file_extension='mp4', only_video=True).first()
                        audio_stream = yt.streams.filter(file_extension='mp4', only_audio=True).first()

                        if video_stream and audio_stream:
                            video_file = video_stream.download(filename='video.mp4')
                            audio_file = audio_stream.download(filename='audio.mp4')

                            video_clip = mp.VideoFileClip(video_file)
                            audio_clip = mp.AudioFileClip(audio_file)
                            final_clip = video_clip.set_audio(audio_clip)
                            final_clip.write_videofile(f"{self.dire.get()}/{file_name}", 
                                codec='libx264',         
                                audio_codec='aac',      
                                preset='ultrafast',    
                                threads=4)
                            
                            remove(video_file)
                            remove(audio_file)

                            if path.exists(f'{self.dire.get()}/{file_name}'):
                                messagebox.showinfo('Sucesso!', f'O vídeo -> {safe_filename(yt.title)} foi baixado com sucesso!')
                        else:
                            messagebox.showwarning('Aviso', 'Stream de vídeo ou áudio não encontrado!')

                self.progress_window.destroy()
            
            except IndexError:
                self.progress_window.destroy()
                messagebox.showerror('[ERRO]', 'Insira uma resolução!')
            except Exception as err:
                self.progress_window.destroy()
                messagebox.showerror('[ERRO]', f'Erro ao acessar o link! {err}')
            finally:
                self.download_button.config(state=tk.NORMAL)

        self.janela = tk.Tk()
        self.janela.title('Baixar vídeos do Youtube')
        self.janela.geometry('500x400+800+300')
        self.janela.iconbitmap(self.ICON)
        self.janela.resizable(False, False)

        self.IMAGE = ImageTk.PhotoImage(self.IMAGE.resize((180,170)))
        tk.Label(self.janela, image=self.IMAGE).place(x=30, y=-20)
        tk.Label(self.janela, text='Youtube', font=(self.FONTE_TEXT, 46)).place(x=205, y=25)
        tk.Label(self.janela, text='URL:', font=(self.FONTE_TEXT, 22)).place(x=27, y=135)
        
        self.entry_url = ttk.Entry(self.janela, bootstyle='dark', width=62)
        self.entry_url.place(x=100, y=143)

        estilo = ttk.Style()
        estilo.configure('dark.TButton', font=(self.FONTE_TEXT, 22), width=10)
        estilo.configure('dark.TCheckbutton', font=('Banschirift', 16))

        self.so_audio = tk.BooleanVar()

        ttk.Checkbutton(style='dark.TCheckbutton', text='Apenas áudio', variable=self.so_audio, onvalue=True, offvalue=False, command=check).place(x=316, y=200)
        
        tk.Label(self.janela, text='Formato:', font=(self.FONTE_TEXT, 20)).place(x=26, y=190)

        opcoes = ['144p', '240p', '360p', '480p', '720p (HD)', '1080p (FHD)', '1440p (QHD)', '2160p (4K)']
        self.combobox = ttk.Combobox(bootstyle='dark', values=opcoes)
        self.combobox.place(x=142, y=197)

        tk.Label(self.janela, text='Caminho:', font=(self.FONTE_TEXT, 20)).place(x=26, y=250)
        
        self.dire = tk.StringVar()
        ttk.Entry(bootstyle='dark', textvariable=self.dire, width=40).place(x=150, y=255)

        tk.Button(self.janela, text='Escolher', font=(self.FONTE_TEXT, 12), command=exec_botao_dir).place(x=410, y=255)

        self.download_button = ttk.Button(self.janela, text='BAIXAR', style='dark.TButton', command=exec_botao)
        self.download_button.place(x=150, y=320)

        self.janela.mainloop()


if __name__ == '__main__':
    Menu()
