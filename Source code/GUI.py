import tkinter as tk
from tkinter import font as tkfont
import threading
from googleapiclient.discovery import build
import email_retrieval_service as ers
import queue
import re


def fetch_emails(email_queue):
    email_subjects = ers.list_emails(service=service).values()
    email_queue.put(email_subjects)


def update_emails_from_queue(email_queue):
    try:
        emails = email_queue.get_nowait()
        i = 0
        for email in emails:
            i += 1
            listbox.insert(tk.END, f'  {i}. {email}')  # Insert each email into the Listbox
    except queue.Empty:
        pass
    finally:
        if root.winfo_exists():
            root.after(1000, update_emails_from_queue, email_queue)


def update_emails(email_queue):
    listbox.delete(0, tk.END) # remove all listed emails
    fetch_emails(email_queue)
    update_emails_from_queue(email_queue)


def url_search(event):
    # top level
    links = []
    usearch = search.get()
    links.append(usearch)
    response = ers.check_reputation(links, api_token)
    w = tk.Toplevel(root)
    w.geometry("450x300")
    w.title('URL scan results')
    try:
        verdict = tk.Label(w, text=f'Search: {usearch}\n\nVerdict: {response['result']['data'][usearch]['verdict']}', font=font)
    except Exception as e:
        verdict = tk.Label(w, text=f'Wrong URL, must start with "http" or "https".\n\nError: {e}', font=font)
    verdict.grid(row=0, column=0, padx=15, pady=10, sticky='nw')
    w.mainloop()


def create_scan_button(email):
    global scan_button
    if scan_button: scan_button.destroy()
    urls = ers.url_find(email['Message'])
    if len(urls) == 1:
        text="Scan URL"
    elif len(urls) > 1:
        text="Scan URLs"
    else: 
        scan_button = tk.Button(root, text='No URLs found')
        scan_button.grid(row=5, column=1, padx=35, pady=10, sticky='nw')
        return None 
    scan_button = tk.Button(root, text=text, command=lambda: scan_button_press(email))
    scan_button.grid(row=5, column=1, padx=35, pady=10, sticky='nw')


def scan_button_press(email):
    urls = ers.url_find(email['Message'])
    response = ers.check_reputation(urls, api_token=api_token)
    if len(urls) > 1:
        url = response['result']['location'] # the URL to the results from the scan
        bulk = ers.request_response(url, api_token) # getting the results
    elif len(urls) == 1:
        bulk = response
    #w = tk.Toplevel(root)
    #w.geometry("450x300")
    #w.title('URL scan results')
    scan_results = f'Scan results: {bulk['status']}\n\nScan summary:\n{bulk['summary']}\n\n'
    scan_results += 'Scanned:\n'
    for i in range(len(urls)):
        scan_results += str(list(bulk['result']['data'])[i]) + f'\n\nResult: {bulk['result']['data'][str(list(bulk['result']['data'])[i])]['verdict']}\n\n'
    # Creating the label
    label = tk.Label(root, text='Scan results:', font=('Roboto', 11, 'bold'), bg='#EBF0FF')
    label.grid(row=1, column=8, padx=15, pady=(25,0), sticky='sw')
    # Creating the results text
    results = tk.Text(root, font=font, width=45, height=15)
    results.grid(row=4, column=8, padx=(15, 80), pady=(25, 0), sticky='nw')
    results.config(state="normal")  # Enable editing to insert text
    results.delete("1.0", tk.END)  # Clear existing text
    results.insert(tk.END, scan_results)  # Insert email info
    results.config(state="disabled")  # Disable editing after insertion
    #w.mainloop()


def select_email(event):
    # Your function code here
    selected_index = listbox.curselection()
    if selected_index:
        # Get selected email
        email_id = list(ers.list_emails(service=service).keys())[selected_index[0]]
        email = ers.email_parser(ers.get_email(msg_id=email_id, service=service))
        # Add label
        emails_label = tk.Label(root, text="Email details:", font=('Roboto', 11, 'bold'), bg='#EBF0FF')
        emails_label.grid(row=1, column=1, padx=(32, 0), pady=(15,0), sticky='sw')
        # Build window
        results = tk.Text(root, font=font, width=45, height=15)
        results.grid(row=4, column=1, padx=(35, 0), pady=(25, 0), sticky='nw')
        results.config(state="normal")  # Enable editing to insert text
        results.delete("1.0", tk.END)  # Clear existing text
        results.insert(tk.END, f'From:\n{email['From']}\n\nTo:\n{email['To']}\n\nDate:\n{email['Date']}\n\nURLs found:\n{len(ers.url_find(email['Message']))}')  # Insert email info
        results.config(state="disabled")  # Disable editing after insertion
        create_scan_button(email)


# CONFIGURATION

api_token = None
credentials_file_path = None
service = None
root = None
listbox = None
font = None
scan_button = None
scopes = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    with open('project_pangea.conf', 'rt', encoding='UTF-8') as config:
        config.seek(0)
        content = config.read()
        for line in content.split('\n'):
            if "api_token" in line:
                # Extracting the value between single quotes
                global api_token
                api_token = re.findall(r"'(.*?)'", line)[0]
            if "credentials_file_path" in line:
                # Extracting the value between double quotes
                global credentials_file_path
                credentials_file_path = re.findall(r"'(.*?)'", line)[0]


    credentials = ers.get_credentials(credentials_file_path, scopes) # logging to gmail's OAuth
    global service
    service = build('gmail', 'v1', credentials=credentials) # Building the service

    # Create the main window (root boject)
    global root
    root = tk.Tk()
    root.title("Project Pangea")
    root.geometry("1080x600")# Set the size of the window
    root.configure(bg='#EBF0FF')

    # Row and column configfuration for size and scaling
    root.columnconfigure(5, weight=1)
    root.rowconfigure(5, weight=1)

    # Configuring the font
    font = tkfont.Font(family='Roboto', size=10)

    # Create a welcome label
    welcome_label = tk.Label(root, text="Welcome to Project Pangea.", font=('Roboto', 12, 'bold'), bg='#EBF0FF')
    welcome_label.grid(row=0, column=0, padx=15, pady=10, sticky='')

    # The author label
    author = tk.Label(root, text="Author: Wojciech Sołtys", font=('Roboto', 8), bg='#EBF0FF')
    author.grid(row=8, column=8, padx=(0, 5), pady=(0, 5), sticky='ne')

    # Entry widget for the search entry
    global search
    search = tk.Entry(root, width=30)
    search.grid(row=0, column=8, sticky='ne', padx=(0, 15), pady=10)

    # Button for the search widget
    search_label = tk.Button(root, text="Scan a URL:", font=('Roboto', 8, 'bold'), bg='#3D5588', fg = "#ffffff", command=lambda: url_search(search.get()))
    search_label.grid(row=0, column=8, sticky='ne', pady=(7,0), padx=(0, 200))

    # Latest emails label
    latest_label = tk.Label(root, text="Your emails:", font=('Roboto', 12, 'bold'), bg='#EBF0FF')
    latest_label.grid(row=1, column=0, padx=15, pady=(25,0), sticky='sw')

    # Listbox with email subjects and id's
    global listbox
    listbox = tk.Listbox(root, width=30, height=15, font=font, fg='#000000',bg='#ffffff')
    listbox.grid(row=4, column=0, padx=15, pady=(10, 0), sticky='sw')
    listbox.bind("<<ListboxSelect>>", select_email)

    # Refresh button for email listbox
    refresh_button = tk.Button(root, text="Refresh", bg='#3D5588', fg = "#ffffff",command=lambda: threading.Thread(target=update_emails, args=(email_queue,)).start())
    refresh_button.grid(row=1, column=0, padx=15, pady=(10, 5), sticky='se')

    # Email queue
    email_queue = queue.Queue()

    # Main loop
    root.after(0, update_emails, email_queue)
    root.mainloop()

if __name__ == '__main__':
    main()
