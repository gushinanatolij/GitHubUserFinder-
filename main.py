import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

GITHUB_API = "https://api.github.com/users/"
FAVORITES_FILE = "favorites.json"

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_favorites(favorites):
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, indent=2, ensure_ascii=False)

def search_github():
    username = search_entry.get().strip()
    if not username:
        messagebox.showwarning("Ошибка", "Поле поиска не может быть пустым")
        return
    
    try:
        response = requests.get(GITHUB_API + username)
        if response.status_code == 200:
            user_data = response.json()
            display_user(user_data)
        elif response.status_code == 404:
            messagebox.showinfo("Результат", f"Пользователь '{username}' не найден")
            clear_display()
        else:
            messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}")
    except requests.RequestException as e:
        messagebox.showerror("Ошибка", f"Ошибка соединения: {e}")

def display_user(user):
    clear_display()
    
    info_text = f"""Логин: {user.get('login', 'Нет данных')}
Имя: {user.get('name', 'Не указано')}
Компания: {user.get('company', 'Не указана')}
Локация: {user.get('location', 'Не указана')}
Репозитории: {user.get('public_repos', 0)}
Подписчики: {user.get('followers', 0)}
Подписки: {user.get('following', 0)}
Создан: {user.get('created_at', 'Нет данных')[:10]}
"""
    
    result_text.delete(1.0, tk.END)
    result_text.insert(1.0, info_text)
    
    current_user = user.get('login')
    if current_user:
        add_fav_button.config(state=tk.NORMAL, command=lambda: add_to_favorites(current_user, user))
        
        favorites = load_favorites()
        if any(f['login'] == current_user for f in favorites):
            add_fav_button.config(text="✓ В избранном", state=tk.DISABLED)
        else:
            add_fav_button.config(text="★ Добавить в избранное", state=tk.NORMAL)

def clear_display():
    result_text.delete(1.0, tk.END)
    add_fav_button.config(text="★ Добавить в избранное", state=tk.DISABLED)

def add_to_favorites(username, user_data):
    favorites = load_favorites()
    
    if any(f['login'] == username for f in favorites):
        messagebox.showinfo("Инфо", f"{username} уже в избранном")
        return
    
    favorite = {
        'login': username,
        'name': user_data.get('name', ''),
        'avatar_url': user_data.get('avatar_url', ''),
        'html_url': user_data.get('html_url', ''),
        'added_at': datetime.now().isoformat()
    }
    
    favorites.append(favorite)
    save_favorites(favorites)
    add_fav_button.config(text="✓ В избранном", state=tk.DISABLED)
    update_favorites_list()
    messagebox.showinfo("Успех", f"{username} добавлен в избранное")

def update_favorites_list():
    for item in favorites_tree.get_children():
        favorites_tree.delete(item)
    
    favorites = load_favorites()
    for fav in favorites:
        favorites_tree.insert('', tk.END, values=(
            fav['login'],
            fav.get('name', 'Не указано'),
            fav['added_at'][:10]
        ))

def remove_from_favorites():
    selected = favorites_tree.selection()
    if not selected:
        messagebox.showwarning("Ошибка", "Выберите пользователя для удаления")
        return
    
    username = favorites_tree.item(selected[0])['values'][0]
    favorites = load_favorites()
    favorites = [f for f in favorites if f['login'] != username]
    save_favorites(favorites)
    update_favorites_list()
    
    current_display = result_text.get(1.0, tk.END).strip()
    if username in current_display:
        add_fav_button.config(text="★ Добавить в избранное", state=tk.NORMAL)
    
    messagebox.showinfo("Успех", f"{username} удален из избранного")

def on_favorite_select(event):
    selected = favorites_tree.selection()
    if selected:
        username = favorites_tree.item(selected[0])['values'][0]
        search_entry.delete(0, tk.END)
        search_entry.insert(0, username)
        search_github()

root = tk.Tk()
root.title("GitHub User Finder - Гущин Анатолий")
root.geometry("900x700")
root.resizable(True, True)

main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(main_frame, text="Поиск пользователя GitHub:", font=('Arial', 12)).grid(row=0, column=0, sticky=tk.W, pady=5)
search_entry = ttk.Entry(main_frame, width=50, font=('Arial', 11))
search_entry.grid(row=0, column=1, padx=5, pady=5)
search_entry.bind('<Return>', lambda event: search_github())

search_button = ttk.Button(main_frame, text="🔍 Найти", command=search_github)
search_button.grid(row=0, column=2, padx=5, pady=5)

ttk.Label(main_frame, text="Информация о пользователе:", font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=(10, 5))

result_frame = ttk.Frame(main_frame)
result_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

result_text = tk.Text(result_frame, height=12, width=70, font=('Courier', 10), wrap=tk.WORD)
result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=result_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
result_text.config(yscrollcommand=scrollbar.set)

button_frame = ttk.Frame(main_frame)
button_frame.grid(row=3, column=0, columnspan=3, pady=10)

add_fav_button = ttk.Button(button_frame, text="★ Добавить в избранное", state=tk.DISABLED, width=20)
add_fav_button.pack(side=tk.LEFT, padx=5)

ttk.Label(main_frame, text="Избранные пользователи:", font=('Arial', 11, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=(10, 5))

favorites_frame = ttk.Frame(main_frame)
favorites_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

columns = ('Логин', 'Имя', 'Дата добавления')
favorites_tree = ttk.Treeview(favorites_frame, columns=columns, show='headings', height=10)

for col in columns:
    favorites_tree.heading(col, text=col)
    favorites_tree.column(col, width=150)

favorites_tree.bind('<<TreeviewSelect>>', on_favorite_select)

tree_scrollbar = ttk.Scrollbar(favorites_frame, orient=tk.VERTICAL, command=favorites_tree.yview)
favorites_tree.configure(yscrollcommand=tree_scrollbar.set)

favorites_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

remove_button = ttk.Button(main_frame, text="🗑 Удалить из избранного", command=remove_from_favorites)
remove_button.grid(row=6, column=0, columnspan=3, pady=10)

update_favorites_list()

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)
main_frame.grid_rowconfigure(2, weight=1)
main_frame.grid_rowconfigure(5, weight=1)

root.mainloop()
