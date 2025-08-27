import tkinter as tk
from core.persistence import load_accounts, save_accounts
from core.otp_manager import generate_otp

accounts = {}
last_otps = {}
selected_user = None

def add_account(entry_user, entry_secret, entry_password, entry_note, refresh_accounts):
    user = entry_user.get().strip()
    secret = entry_secret.get().strip()
    password = entry_password.get().strip()
    note = entry_note.get().strip()
    if user and secret:
        accounts[user] = {
            "secret": secret,
            "password": password,
            "note": note
        }
        save_accounts(accounts)
        refresh_accounts()
        entry_user.delete(0, tk.END)
        entry_secret.delete(0, tk.END)
        entry_password.delete(0, tk.END)
        entry_note.delete(0, tk.END)

def edit_account(user, entry_user, entry_secret, entry_password, entry_note, btn_add, btn_update, btn_cancel, refresh_accounts):
    # Fill entry fields with selected account data
    data = accounts.get(user, {})
    entry_user.delete(0, tk.END)
    entry_user.insert(0, user)
    entry_secret.delete(0, tk.END)
    entry_secret.insert(0, data.get("secret", ""))
    entry_password.delete(0, tk.END)
    entry_password.insert(0, data.get("password", ""))
    entry_note.delete(0, tk.END)
    entry_note.insert(0, data.get("note", ""))
    entry_user.config(state="disabled")
    btn_add.config(state="disabled")
    btn_update.config(state="normal")
    btn_cancel.config(state="normal")

def update_account(entry_user, entry_secret, entry_password, entry_note, btn_add, btn_update, btn_cancel, refresh_accounts):
    user = entry_user.get().strip()
    secret = entry_secret.get().strip()
    password = entry_password.get().strip()
    note = entry_note.get().strip()
    if user and secret:
        accounts[user] = {
            "secret": secret,
            "password": password,
            "note": note
        }
        save_accounts(accounts)
        refresh_accounts()
    entry_user.config(state="normal")
    btn_add.config(state="normal")
    btn_update.config(state="disabled")
    btn_cancel.config(state="disabled")
    entry_user.delete(0, tk.END)
    entry_secret.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    entry_note.delete(0, tk.END)

def cancel_edit(entry_user, entry_secret, entry_password, entry_note, btn_add, btn_update, btn_cancel):
    entry_user.config(state="normal")
    btn_add.config(state="normal")
    btn_update.config(state="disabled")
    btn_cancel.config(state="disabled")
    entry_user.delete(0, tk.END)
    entry_secret.delete(0, tk.END)
    entry_password.delete(0, tk.END)
    entry_note.delete(0, tk.END)

def generate_otp_ui(user, label_result):
    try:
        secret = accounts[user]["secret"]
        otp = generate_otp(secret)
        last_otps[user] = otp
        label_result.config(text=f"{user}\nOTP: {otp}", fg="green")
    except Exception as e:
        label_result.config(text=f"❌ Error: {e}", fg="red")

def copy_otp(user, root, label_result):
    if user in last_otps:
        otp = last_otps[user]
        root.clipboard_clear()
        root.clipboard_append(otp)
        root.update()
        label_result.config(text=f"{user}\nOTP: {otp} ✅ Copied!", fg="green")
    else:
        label_result.config(text="❌ ยังไม่มี OTP ให้ copy", fg="red")

def copy_field(user, field, root, label_result):
    if field == "user":
        value = user
    else:
        value = accounts.get(user, {}).get(field, "")
    if value:
        root.clipboard_clear()
        root.clipboard_append(value)
        root.update()
        label_result.config(text=f"{field.capitalize()} copied for {user}!", fg="green")
    else:
        label_result.config(text=f"❌ {field.capitalize()} is empty", fg="red")

def delete_account(user, refresh_accounts, label_result, selected_var):
    if user in accounts:
        del accounts[user]
        if user in last_otps:
            del last_otps[user]
        save_accounts(accounts)
        refresh_accounts()
        label_result.config(text="")
        selected_var.set("")

def refresh_accounts(frame_accounts, label_result, root, selected_var, entry_user, entry_secret, entry_password, entry_note, btn_add, btn_update, btn_cancel):
    for widget in frame_accounts.winfo_children():
        widget.destroy()
    # --- Header row ---
    columns = ["User/Email", "Password", "Secret Key", "Note"]
    header = tk.Frame(frame_accounts)
    header.pack(fill="x", pady=2)
    tk.Label(header, text="", width=3).pack(side="left")  # For radio button
    for col in columns:
        tk.Label(header, text=col, width=18, anchor="w", font=("Arial", 10, "bold")).pack(side="left")
    # --- Data rows ---
    for user, data in accounts.items():
        frame = tk.Frame(frame_accounts)
        frame.pack(fill="x", pady=2)
        rb = tk.Radiobutton(frame, variable=selected_var, value=user)
        rb.pack(side="left")
        # Username
        tk.Label(frame, text=user, width=20, anchor="w").pack(side="left")
        # Password
        tk.Label(frame, text=data.get("password", ""), width=16, anchor="w", fg="gray").pack(side="left")
        # Secret Key
        tk.Label(frame, text=data.get("secret", ""), width=16, anchor="w", fg="gray").pack(side="left")
        # Note
        tk.Label(frame, text=data.get("note", ""), width=16, anchor="w", fg="gray").pack(side="left")
        btn_edit = tk.Button(frame, text="Edit", width=6, command=lambda u=user: edit_account(u, entry_user, entry_secret, entry_password, entry_note, btn_add, btn_update, btn_cancel, lambda: refresh_accounts(frame_accounts, label_result, root, selected_var, entry_user, entry_secret, entry_password, entry_note, btn_add, btn_update, btn_cancel)))
        btn_edit.pack(side="left", padx=2)
        btn_del = tk.Button(frame, text="Delete", width=7, command=lambda u=user: delete_account(u, lambda: refresh_accounts(frame_accounts, label_result, root, selected_var, entry_user, entry_secret, entry_password, entry_note, btn_add, btn_update, btn_cancel), label_result, selected_var))
        btn_del.pack(side="left", padx=2)

def run_app():
    global accounts
    root = tk.Tk()
    root.title("2FA OTP Manager")
    root.geometry("1100x600")

    label_header = tk.Label(root, text="2FA OTP MANAGER", font=("Arial", 28, "bold"), fg="white")
    label_header.pack(pady=10)

    frame_add = tk.Frame(root)
    frame_add.pack(pady=5)
    label_user = tk.Label(frame_add, text="User/Email:")
    label_user.grid(row=0, column=0, padx=2, pady=2, sticky="e")
    entry_user = tk.Entry(frame_add, width=15)
    entry_user.grid(row=0, column=1, padx=2, pady=2)
    label_password = tk.Label(frame_add, text="Password:")
    label_password.grid(row=0, column=2, padx=2, pady=2, sticky="e")
    entry_password = tk.Entry(frame_add, width=15)
    entry_password.grid(row=0, column=3, padx=2, pady=2)
    label_secret = tk.Label(frame_add, text="Secret Key:")
    label_secret.grid(row=0, column=4, padx=2, pady=2, sticky="e")
    entry_secret = tk.Entry(frame_add, width=15)
    entry_secret.grid(row=0, column=5, padx=2, pady=2)
    label_note = tk.Label(frame_add, text="Note:")
    label_note.grid(row=0, column=6, padx=2, pady=2, sticky="e")
    entry_note = tk.Entry(frame_add, width=15)
    entry_note.grid(row=0, column=7, padx=2, pady=2)

    btn_add = tk.Button(frame_add, text="Confirm")
    btn_add.grid(row=0, column=8, padx=10, pady=2)
    btn_update = tk.Button(frame_add, text="Update", state="disabled")
    btn_update.grid(row=0, column=9, padx=2, pady=2)
    btn_cancel = tk.Button(frame_add, text="Cancel", state="disabled")
    btn_cancel.grid(row=0, column=10, padx=2, pady=2)

    frame_container = tk.Frame(root)
    frame_container.pack(pady=10, fill="both", expand=True)
    canvas = tk.Canvas(frame_container)
    canvas.pack(side="left", fill="both", expand=True)

    xscrollbar = tk.Scrollbar(frame_container, orient="horizontal", command=canvas.xview)
    xscrollbar.pack(side="bottom", fill="x")
    yscrollbar = tk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
    yscrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)

    frame_accounts = tk.Frame(canvas)
    frame_id = canvas.create_window((0,0), window=frame_accounts, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas_width = max(event.width, frame_accounts.winfo_reqwidth())
        canvas.itemconfig(frame_id, width=canvas_width)
    frame_accounts.bind("<Configure>", on_frame_configure)

    def _on_mousewheel(event):
        if event.state & 0x1:
            canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        else:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    selected_var = tk.StringVar(value="")

    frame_result = tk.Frame(root)
    frame_result.pack(pady=10)
    label_result = tk.Label(frame_result, text="OTP: ", font=("Arial", 24, "bold"), fg="green")
    label_result.pack(padx=5, pady=2)

    # ปุ่มด้านล่างสำหรับ account ที่เลือก
    def get_selected():
        return selected_var.get()

    btn_gen = tk.Button(frame_result, text="Gen OTP", command=lambda: generate_otp_ui(get_selected(), label_result))
    btn_gen.pack(side="left", padx=5)
    btn_copy_otp = tk.Button(frame_result, text="Copy OTP", command=lambda: copy_otp(get_selected(), root, label_result))
    btn_copy_otp.pack(side="left", padx=5)
    btn_copy_user = tk.Button(frame_result, text="Copy User", command=lambda: copy_field(get_selected(), "user", root, label_result))
    btn_copy_user.pack(side="left", padx=5)
    btn_copy_pass = tk.Button(frame_result, text="Copy Pass", command=lambda: copy_field(get_selected(), "password", root, label_result))
    btn_copy_pass.pack(side="left", padx=5)
    btn_copy_secret = tk.Button(frame_result, text="Copy Secret", command=lambda: copy_field(get_selected(), "secret", root, label_result))
    btn_copy_secret.pack(side="left", padx=5)
    btn_copy_note = tk.Button(frame_result, text="Copy Note", command=lambda: copy_field(get_selected(), "note", root, label_result))
    btn_copy_note.pack(side="left", padx=5)

    label_credit = tk.Label(root, text="Edit by: DAPPER", font=("Arial", 10), fg="gray")
    label_credit.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

    def refresh():
        refresh_accounts(
            frame_accounts, label_result, root, selected_var,
            entry_user, entry_secret, entry_password, entry_note,
            btn_add, btn_update, btn_cancel
        )

    btn_add.config(command=lambda: add_account(entry_user, entry_secret, entry_password, entry_note, refresh))
    btn_update.config(command=lambda: update_account(entry_user, entry_secret, entry_password, entry_note, btn_add, btn_update, btn_cancel, refresh))
    btn_cancel.config(command=lambda: cancel_edit(entry_user, entry_secret, entry_password, entry_note, btn_add, btn_update, btn_cancel))

    # migrate old accounts if needed
    loaded = load_accounts()
    # migrate old format (user: secret) to new format (user: {secret, password, note})
    for k, v in loaded.items():
        if isinstance(v, dict):
            accounts[k] = v
        else:
            accounts[k] = {"secret": v, "password": "", "note": ""}
    refresh()

    root.mainloop()
    refresh()

    root.mainloop()
