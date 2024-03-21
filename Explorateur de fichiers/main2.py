from tkinter import *
import os
import ctypes
import pathlib
from tkinter import simpledialog  # Import de simpledialog pour utiliser la boîte de dialogue
from tkinter import messagebox


# Augmente les points par pouce pour une apparence plus nette
ctypes.windll.shcore.SetProcessDpiAwareness(True)
root = Tk()
root.geometry('1000x600')
# Définit un titre pour la fenêtre principale de l'explorateur de fichiers
root.title('Explorateur de Fichier')

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)

# Dictionnaire des favoris pour garder une trace des éléments favoris
favoris = {}
# Fonction pour afficher le message pop-up de bienvenue
def show_welcome_message():
    messagebox.showinfo("Bienvenue", "Bienvenue dans votre Explorateur de fichiers")

# Afficher le message pop-up de bienvenue après 1000 millisecondes (1 secondes)
root.after(1000, show_welcome_message)
# Liste pour garder une trace des fichiers récemment ouverts
recent_files = []

def pathChange(*event):
    # Obtenir le chemin d'accès actuel
    current_directory = currentPath.get()

    # Vérifier si le chemin d'accès existe
    if os.path.exists(current_directory):
        # Obtenir tous les fichiers et dossiers du répertoire donné
        directory = os.listdir(current_directory)
        # Effacer la liste
        list.delete(0, END)
        # Insérer les fichiers et dossiers dans la liste
        for file in directory:
            # Si c'est un dossier, ajouter l'emoji de dossier au nom du fichier affiché dans la liste
            if os.path.isdir(os.path.join(current_directory, file)):
                list.insert(END, "📁 " + file)
            else:
                list.insert(END, file)
    else:
        print("Le chemin d'accès spécifié est introuvable ou inaccessible.")


def refresh():
    pathChange()

def changePathByClick(event=None):
    # Vérifier si un élément a été sélectionné dans la liste
    if list.curselection():
        # Obtenir l'indice de l'élément sélectionné
        index = list.curselection()[0]
        # Obtenir le nom du fichier ou du dossier sélectionné à partir de l'indice
        picked = list.get(index)
        # Vérifier si l'élément est un dossier (en vérifiant s'il commence par l'emoji de dossier)
        if picked.startswith("📁 "):
            # Extraire le nom du dossier en supprimant l'emoji de dossier et l'espace
            folder_name = picked[2:]
            # Obtenir le chemin complet en joignant le chemin actuel avec le nom du dossier
            path = os.path.join(currentPath.get(), folder_name)
        else:
            # Si ce n'est pas un dossier, le nom de fichier est directement utilisé
            path = os.path.join(currentPath.get(), picked)
        
        # Vérifier si l'élément est un fichier, puis l'ouvrir
        if os.path.isfile(path):
            print('Ouverture : '+path)
            os.startfile(path)
            # Ajouter le fichier à la liste des fichiers récemment ouverts
            add_to_recent(path)
        # Définir le nouveau chemin, ce qui déclenchera la fonction pathChange.
        else:
            currentPath.set(path)

def goBack(event=None):
    # Obtenir le nouveau chemin
    newPath = pathlib.Path(currentPath.get()).parent
    # Définir le nouveau chemin actuel
    currentPath.set(newPath)
    # Message simple
    print('Retour en arrière')

def open_popup():
    global top
    top = Toplevel(root)
    top.geometry("250x150")
    top.resizable(False, False)
    top.title("Fenêtre enfant")
    top.columnconfigure(0, weight=1)
    Label(top, text='Entrez le nom du fichier ou du dossier').grid()
    Entry(top, textvariable=newFileName).grid(column=0, pady=10, sticky='NSEW')
    Button(top, text="Créer", command=newFileOrFolder).grid(pady=10, sticky='NSEW')

def newFileOrFolder():
    # Vérifier s'il s'agit d'un nom de fichier ou d'un dossier
    if len(newFileName.get().split('.')) != 1:
        open(os.path.join(currentPath.get(), newFileName.get()), 'w').close()
    else:
        os.mkdir(os.path.join(currentPath.get(), newFileName.get()))
    # Fermer la fenêtre enfant
    top.destroy()
    pathChange()

top = ''
# Variables de chaîne
newFileName = StringVar(root, " ", 'new_name')
currentPath = StringVar(
    root,
    name='currentPath',
    value=pathlib.Path.cwd()
)
# Lier les changements dans cette variable à la fonction pathChange
currentPath.trace('w', pathChange)
# Raccourci clavier pour remonter
root.bind("<Alt-Up>", goBack)

# Bouton "Remonter"
Button(root, text='Dossier Parent', command=goBack).grid(
     column=0, row=0
)

# Entrée de chemin d'accès
Entry(root, textvariable=currentPath).grid(
    sticky='NSEW', column=1, row=0, ipady=10, ipadx=10
)

# Liste des fichiers et dossiers
list = Listbox(root)
list.grid(sticky='NSEW', column=1, row=1, ipady=10, ipadx=10)
# Accélérateurs de liste
list.bind('<Double-1>', changePathByClick)
list.bind('<Return>', changePathByClick)

def show_context_menu(event):
    index = list.nearest(event.y)
    list.selection_clear(0, END)
    list.selection_set(index)
    list.activate(index)
    picked = list.get(index)
    path = os.path.join(currentPath.get(), picked)

    # Supprimer l'emoji de dossier du nom du fichier/dossier s'il est présent
    if picked.startswith("📁 "):
        path = os.path.join(currentPath.get(), picked[2:])

    # Créer le menu contextuel
    menu = Menu(root, tearoff=0)
    if os.path.isdir(path):
        menu.add_command(label="Ouvrir", command=lambda: currentPath.set(path))
        menu.add_command(label="Ajouter aux Favoris", command=lambda: add_to_favoris(path))
    else:
        menu.add_command(label="Ouvrir", command=lambda: os.startfile(path))
        menu.add_command(label="Ajouter aux Favoris", command=lambda: add_to_favoris(path))
    if os.path.isdir(path):
        menu.add_command(label="Supprimer", command=lambda: delete_item(path))
    else:
        menu.add_command(label="Supprimer", command=lambda: delete_item(path))
    menu.add_command(label="Renommer", command=lambda: rename_file(path))
    menu.add_command(label="Propriétés", command=lambda: show_properties(path))

    # Afficher le menu contextuel au pointeur de la souris
    menu.post(event.x_root, event.y_root)

# Liaison de la fonction show_context_menu à l'événement de clic droit
list.bind("<Button-3>", show_context_menu)

def add_to_favoris(path):
    # Ajouter le fichier ou dossier aux favoris avec son chemin d'accès complet
    favoris[os.path.basename(path)] = path
    print("Ajouté aux Favoris :", path)

list.bind("<Button-3>", show_context_menu)

def show_favoris():
    # Effacer la liste
    list.delete(0, END)
    for item in favoris:
        if os.path.isdir(favoris[item]):
            list.insert(END, "📁 " + item)
        else:
            list.insert(END, item)

def delete_item(path):
    if os.path.isdir(path):
        os.rmdir(path)
    else:
        os.remove(path)
    pathChange()

def rename_file(path):
    new_name = simpledialog.askstring("Renommer", "Entrez le nouveau nom :")
    if new_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
    os.rename(path, new_path)
    pathChange()

def show_properties(path):
    # Obtenir les propriétés du fichier/dossier sélectionné
    size = os.path.getsize(path)
    if os.path.isdir(path):
        type_str = "Dossier"
        size_str = "<DIR>"
    else:
        type_str = "Fichier"
        size_str = str(size) + " octets"

    # Afficher les propriétés dans une messagebox
    messagebox.showinfo("Propriétés", f"Type : {type_str}\nTaille : {size_str}")

def show_recent_files():
    # Effacer la liste
    list.delete(0, END)
    for file in recent_files:
        list.insert(0, file)

def add_to_recent(path):
    # Ajouter le fichier à la liste des fichiers récemment ouverts
    if path not in recent_files:
        recent_files.insert(0, path)

# Bouton "Favoris"
Button(root, text='Favoris', command=show_favoris).grid(
    column=0, row=1, sticky='EW'
)

# Bouton "Récents"
Button(root, text='Récents', command=show_recent_files).grid(
    column=0, row=2, sticky='EW'
)
def handle_search():
    # Afficher la boîte de dialogue pour la recherche
    keyword = simpledialog.askstring("Rechercher", "Entrez le mot-clé pour la recherche :")
    if keyword:
        search_files(keyword)

def search_files(keyword):
    # Effacer la liste des fichiers
    list.delete(0, END)
    # Obtenir le chemin d'accès actuel
    current_directory = currentPath.get()
    
    # Appeler la fonction recursive_search pour parcourir tous les fichiers et dossiers
    recursive_search(current_directory, keyword)

def recursive_search(directory, keyword):
    # Parcourir tous les fichiers et dossiers dans le répertoire donné
    for file in os.listdir(directory):
        # Chemin complet du fichier ou du dossier
        path = os.path.join(directory, file)
        # Si c'est un dossier, parcourir récursivement son contenu
        if os.path.isdir(path):
            recursive_search(path, keyword)
            # Vérifier si le nom du dossier contient le mot-clé
            if keyword.lower() in file.lower():
                # Ajouter le dossier à la liste
                list.insert(END, path)
        # Si c'est un fichier, vérifier si son nom contient le mot-clé
        elif keyword.lower() in file.lower():
            # Ajouter le fichier à la liste
            list.insert(END, path)

# Menu
menubar = Menu(root)
# Ajouter un nouveau bouton de fichier ou de dossier
menubar.add_command(label="Ajouter un fichier ou un dossier", command=open_popup)
# Ajouter l'option de recherche à côté de "Quitter"
menubar.add_command(label="Rechercher", command=handle_search)
menubar.add_command(label="Actualiser", command=refresh)
# Ajouter un bouton pour quitter dans le menu
menubar.add_command(label="Quitter", command=root.quit)
# Définir le menubar comme le menu principal
root.config(menu=menubar)


# Appeler la fonction pour afficher la liste
pathChange('')

# Lancer le programme principal
root.mainloop()

