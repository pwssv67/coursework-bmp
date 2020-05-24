import PySimpleGUI as sg
import BMPFile as bmp

layout = [
    [sg.Text("Load or create file")],
    [sg.Text("File"), sg.InputText(size=(65, 10)), sg.FileBrowse(), sg.Button("Load")],
    [sg.Text("M"), sg.InputText(size=(10, 10)), sg.Text("W"), sg.InputText(size=(10, 10)),
     sg.Text("H"), sg.InputText(size=(10, 10)), sg.Button("Generate")],
    [sg.Text("Resize:")],
    [sg.Text("W"), sg.InputText(size=(10, 10)),  sg.Text("H"), sg.InputText(size=(10, 10)), sg.Button("Resize")],
    [sg.Text("Change to palette file")],
    [sg.Radio("4 bit", 0), sg.Radio("8 bit", 0), sg.Button("Change palette")],
    [sg.Text("Save result")],
    [sg.InputText(size=(55, 10), key = "file_save_path"), sg.FileSaveAs(key = "file_save"), sg.Save()]
     #sg.Text("Filename"), sg.InputText(size=(15, 10)), sg.Button("Save")]
]
# sg.theme("")
img = None
window = sg.Window('File Compare', layout)
while True:                             # The Event Loop
    event, values = window.read()
    # print(event, values) #debug
    if event in (None, 'Exit', 'Cancel'):
        break
    if event == "Load":
        if values[0] is not None and values[0] != "":
            img = bmp.read_image(values[0])
        else:
            sg.PopupQuickMessage("Please, choose file first")
    if event == "Generate":
        img = bmp.generate_image(int(values[1]), int(values[2]), int(values[3]))
    if event == "Resize":
        if img is None:
            sg.PopupQuickMessage("import or generate image first")
        else:
            img = bmp.copy_with_changed_size(img, int(values[4]), int(values[5]))
            bmp.write_image(img, "rgeg")
    if event == "Change palette":
        if img is None:
            sg.PopupQuickMessage("import or generate image first")
        else:
            pass
    if event == "Save":
        if values["file_save_path"] is not None and values["file_save_path"] != "":
            bmp.write_image(img, str(values["file_save_path"]))
        else:
            sg.PopupQuickMessage("Choose file name to save image")