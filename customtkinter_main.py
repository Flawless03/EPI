
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import os, socket, paramiko, sys, subprocess

VERSION = 1.0
WHITE = "#ffffff"
TIME_OUT = 5000
USER_NAME = "pi"
PASSWORD = "etechme"
FOLDER_PATH = r'.\EPI-Files'












def reboot():
    pingable = check_host_reachable(device_ip_textbox.get())

    # Create a new SSH client
    ssh = paramiko.SSHClient()
    # Set the policy to automatically add the server's host key
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ip_address = device_ip_textbox.get()
    if len(ip_address) == 0:
        messagebox.showinfo(title="Blank Entry", message="textbox can not be blank")

    elif pingable != "Online":
        messagebox.showinfo(title="No connection", message="Destination unreachable")

    else:
        # reboot_message()

        try:
            # Connect to the SSH server and reboot
            ssh.connect(ip_address, username=USER_NAME, password=PASSWORD)
            _stdin, _stdout, _stderr = ssh.exec_command("sudo rm -rf ~/snap/chromium/common/chromium/Singleton*")
            _stdin, _stdout, _stderr = ssh.exec_command("sudo netplan apply")
            _stdin, _stdout, _stderr = ssh.exec_command("sudo reboot")
            # print(_stdout.read().decode())

            reboot_message = Tk()
            reboot_message.withdraw()  # Hide the main window
            messagebox.showwarning("Reboot", "Rebooting device now!")
            reboot_message.after(500,
                                 reboot_message.destroy())  # Destroy the main window after 3000 milliseconds (3 seconds)
            reboot_message.mainloop()
            ssh.close()
            # ...
        except paramiko.AuthenticationException:
            # Handle authentication errors
            # print("Authentication failed for %s" % ip_address)
            messagebox.showinfo(title="Exception", message="Authentication failed for %s" % ip_address)
        except socket.timeout:
            # Handle connection timeout errors
            # print("Connection timed out for %s" % ip_address)
            messagebox.showinfo(title="Exception", message="Connection timed out for %s" % ip_address)
        except socket.error as e:
            # Handle other socket errors
            # print("Socket error occurred: %s" % e)
            messagebox.showinfo(title="Exception", message="Socket error occurred: %s" % ip_address)
        except EOFError as e:
            # print("EOF error occurred: %s" % e)
            messagebox.showinfo(title="Exception", message="EOF error occurred: %s" % ip_address)
        except Exception as e:
            # Handle any other exceptions
            # print("An error occurred: %s" % e)
            messagebox.showinfo(title="Exception", message="Exception error occurred: %s" % ip_address)
        except BaseException as e:
            # Handle any other exceptions
            # print("An error occurred: %s" % e)
            messagebox.showinfo(title="Exception", message="BaseException error occurred: %s" % ip_address)
        finally:
            # Close the SSH connection
            ssh.close()


def setup():
    # Create a new SSH client
    ssh = paramiko.SSHClient()
    # Set the policy to automatically add the server's host key
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ip_address = device_ip_textbox.get()
    hostname = hostname_textbox.get()
    new_ip = ip_textbox.get()
    gateway = gateway_textbox.get()
    resolution = resolution_radio_var.get()
    new_rotation = rotation_radio_var.get()
    browser_choice = browser_radio_var.get()
    url = url_textbox.get()

    ip_pattern = r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}$'

    # print(ip_address, hostname, new_ip, gateway, url, resolution, new_rotation, browser_choice)
    if len(ip_address) == 0 or len(hostname) == 0 or len(new_ip) == 0 or len(gateway) == 0 or len(url) == 0 or len(
            resolution) == 0 or len(new_rotation) == 0:
        messagebox.showinfo(title="Missing Entry", message="check textbox and radio buttons")

    elif url[0] != '"' or url[-1] != '"':
        messagebox.showinfo(title="URL Syntax Error", message=f"{url} is missing double quotes")

    elif len(new_ip) < 10 or new_ip.isalpha() or "/" not in new_ip:
        messagebox.showinfo(title="IP Syntax Error", message=f"IP should look like this => 10.8.4.251/20")

    elif check_host_reachable(device_ip_textbox.get()) != "Online":
        messagebox.showinfo(title="No connection", message="Destination unreachable")

    else:
        is_ok = messagebox.askokcancel(title=hostname, message=f"These are the details entered: \nHostname: {hostname} "
                                                               f"\nNew IP: {new_ip}"
                                                               f"\nGateway: {gateway}"
                                                               f"\nResolution: {resolution}"
                                                               f"\nRotation: {new_rotation}"
                                                               f"\nBrowser: {browser_choice}"
                                                               f"\nURL: {url}"
                                                               f"\nIs it ok to apply?")

        if is_ok:
            try:
                os.system(
                    f'echo y | pscp.exe -q -l {USER_NAME} -pw {PASSWORD} .\\authorized_keys {device_ip_textbox.get()}:/home/pi/.ssh')
                # Connect to the SSH server
                ssh.connect(ip_address, username=USER_NAME, password=PASSWORD)

                # Get current hostname
                # Changes the system hostname
                _stdin, _stdout, _stderr = ssh.exec_command(f"sudo hostnamectl set-hostname {hostname}")

                # get the current network hostname
                _stdin, _stdout, _stderr = ssh.exec_command("sudo sed -n 2,3p /etc/hosts")
                local_hostname = _stdout.read().decode()
                local_hostname = local_hostname[10:].strip()
                # print("local hostname", local_hostname, "hostname",  hostname)

                # Set a new network hostname
                _stdin, _stdout, _stderr = ssh.exec_command(f"sudo sed -i 's/{local_hostname}/{hostname}/g' /etc/hosts")

                # Get current rotation
                _stdin, _stdout, _stderr = ssh.exec_command("sudo sed -n 8,3p /etc/X11/xorg.conf")
                rotate_screen = _stdout.read().decode()
                current_rotation = rotate_screen.rstrip()
                # print("current screen rotation", current_rotation)

                # Change Resolution
                ten80p = '"1080p60hz"'
                fourteen40p = '"1440x900p60hz"'
                fourk = '"2160p60hz"'

                if resolution == ten80p:
                    _stdin, _stdout, _stderr = ssh.exec_command(
                        f"sudo find /boot/boot.ini -type f -exec sed -i 's/''setenv hdmimode {fourteen40p}''/''setenv hdmimode {resolution}''/g' {{}} \;")
                    _stdin, _stdout, _stderr = ssh.exec_command(
                        f"sudo find /boot/boot.ini -type f -exec sed -i 's/''setenv hdmimode {fourk}''/''setenv hdmimode {resolution}''/g' {{}} \;")
                    # print(_stdout.read().decode())
                elif resolution == fourteen40p:
                    _stdin, _stdout, _stderr = ssh.exec_command(
                        f"sudo find /boot/boot.ini -type f -exec sed -i 's/''setenv hdmimode {ten80p}''/''setenv hdmimode {resolution}''/g' {{}} \;")
                    _stdin, _stdout, _stderr = ssh.exec_command(
                        f"sudo find /boot/boot.ini -type f -exec sed -i 's/''setenv hdmimode {fourk}''/''setenv hdmimode {resolution}''/g' {{}} \;")
                    # print(_stdout.read().decode())
                elif resolution == fourk:
                    _stdin, _stdout, _stderr = ssh.exec_command(
                        f"sudo find /boot/boot.ini -type f -exec sed -i 's/''setenv hdmimode {ten80p}''/''setenv hdmimode {resolution}''/g' {{}} \;")
                    _stdin, _stdout, _stderr = ssh.exec_command(
                        f"sudo find /boot/boot.ini -type f -exec sed -i 's/''setenv hdmimode {fourteen40p}''/''setenv hdmimode {resolution}''/g' {{}} \;")
                    # print(_stdout.read().decode())

                # ROTATION
                left = '        Option "rotate" "ccw"'
                right = '        Option "rotate" "cw"'
                normal = '        Option "rotate" "c"'
                # print(new_rotation, current_rotation, left, right, normal)
                # print(len(new_rotation), len(current_rotation), len(left), len(right), len(normal))
                if new_rotation == left:
                    _stdin, _stdout, _stderr = ssh.exec_command(
                        f"sudo sed -i 's/{current_rotation}/{new_rotation}/g' /etc/X11/xorg.conf")
                    # print(f"sudo sed -i 's/{current_rotation}/{new_rotation}/g' /etc/X11/xorg.conf")
                    # print(_stdout.read().decode())
                elif new_rotation == right:
                    _stdin, _stdout, _stderr = ssh.exec_command(
                        f"sudo sed -i 's/{current_rotation}/{new_rotation}/g' /etc/X11/xorg.conf")
                    # print(f"sudo sed -i 's/{current_rotation}/{new_rotation}/g' /etc/X11/xorg.conf")
                    # print(_stdout.read().decode())
                elif new_rotation == normal:
                    _stdin, _stdout, _stderr = ssh.exec_command(
                        f"sudo sed -i 's/{current_rotation}/{new_rotation}/g' /etc/X11/xorg.conf")
                    # print(f"sudo sed -i 's/{current_rotation}/{new_rotation}/g' /etc/X11/xorg.conf")
                    # print(_stdout.read().decode())

                # BROWSER AND URL
                # Get current chrome url
                _stdin, _stdout, _stderr = ssh.exec_command(
                    "sudo sed -n 5,3p /home/pi/.config/autostart/'chromium-browser (copy)'.desktop")
                current_chrome_url = _stdout.read().decode()
                current_chrome_url = current_chrome_url[21:].strip()
                # print("current chrome url", current_chrome_url)

                # Get current firefox url
                _stdin, _stdout, _stderr = ssh.exec_command(
                    "sudo sed -n 4,3p /home/pi/.config/autostart/firefox.desktop")
                current_firefox_url = _stdout.read().decode()
                current_firefox_url = current_firefox_url[21:].strip()
                # print("current firefox url", current_firefox_url)

                # Change URL of file
                enable_browser = "X-MATE-Autostart-enabled=true"
                disable_browser = "X-MATE-Autostart-enabled=false"

                os.system(
                    f'echo y | pscp.exe -q -l {USER_NAME} -pw {PASSWORD} {device_ip_textbox.get()}:"''/home/pi/.config/autostart/chromium-browser\ (\copy\).desktop'f'" {FOLDER_PATH}')
                os.system(
                    f'echo y | pscp.exe -q -l {USER_NAME} -pw {PASSWORD} {device_ip_textbox.get()}:/home/pi/.config/autostart/firefox.desktop {FOLDER_PATH}')

                if browser_choice == "Chrome":

                    with open(f"{FOLDER_PATH}\\chromium-browser (copy).desktop", "r") as chrome_read:
                        with open(f"{FOLDER_PATH}\\chromium-browser-updated.desktop", "w") as chrome_write:
                            for line in chrome_read:
                                chrome_write.writelines(
                                    line.replace(current_chrome_url, url))

                    _stdin, _stdout, _stderr = ssh.exec_command(
                        "sudo rm /home/pi/.config/autostart/'chromium-browser (copy).desktop'")

                    os.system(
                        f'echo y | pscp.exe -q -l {USER_NAME} -pw {PASSWORD} {FOLDER_PATH}\\chromium-browser-updated.desktop {device_ip_textbox.get()}:/home/pi/.config/autostart/chromium-browser.desktop')

                    # _stdin, _stdout, _stderr = ssh.exec_command("sudo cd /home/pi/.config/autostart/")

                    _stdin, _stdout, _stderr = ssh.exec_command(
                        "sudo mv /home/pi/.config/autostart/'chromium-browser.desktop' /home/pi/.config/autostart/'chromium-browser (copy).desktop'")
                    _stdin, _stdout, _stderr = ssh.exec_command(
                        "sudo chmod +x /home/pi/.config/autostart/'chromium-browser (copy).desktop'")
                    _stdin, _stdout, _stderr = ssh.exec_command(
                        f"sudo sed -i 's/{disable_browser}/{enable_browser}/g' /home/pi/.config/autostart/'chromium-browser (copy).desktop'")
                    _stdin, _stdout, _stderr = ssh.exec_command(
                        f"sudo sed -i 's/{enable_browser}/{disable_browser}/g' /home/pi/.config/autostart/firefox.desktop")

                elif browser_choice == "Firefox":

                    with open(f"{FOLDER_PATH}\\firefox.desktop", "r") as firefox_read:
                        with open(f"{FOLDER_PATH}\\firefox-updated.desktop", "w") as firefox_write:
                            for line in firefox_read:
                                firefox_write.write(line.replace(current_firefox_url, url))

                    os.system(
                        f'echo y | pscp.exe -q -l {USER_NAME} -pw {PASSWORD} {FOLDER_PATH}\\firefox-updated.desktop {device_ip_textbox.get()}:/home/pi/.config/autostart/firefox.desktop')
                    _stdin, _stdout, _stderr = ssh.exec_command(
                        f"sudo sed -i 's/{disable_browser}/{enable_browser}/g' /home/pi/.config/autostart/firefox.desktop")
                    _stdin, _stdout, _stderr = ssh.exec_command(
                        f"sudo sed -i 's/{enable_browser}/{disable_browser}/g' /home/pi/.config/autostart/'chromium-browser (copy).desktop'")

                # SET NETWORK ADDRESSES
                # Create a new netplan yaml config file
                _stdin, _stdout, _stderr = ssh.exec_command(f"sudo touch ~/99-custom.yaml")
                _stdin, _stdout, _stderr = ssh.exec_command(f"sudo chmod 777 ~/99-custom.yaml")

                # Apply network config to netplan yaml config file
                _stdin, _stdout, _stderr = ssh.exec_command("echo  "'network:'" > ~/99-custom.yaml")

                _stdin, _stdout, _stderr = ssh.exec_command("echo "'"  "version: 2'" >> ~/99-custom.yaml")

                _stdin, _stdout, _stderr = ssh.exec_command("echo "'"  "renderer: networkd'" >> ~/99-custom.yaml")

                _stdin, _stdout, _stderr = ssh.exec_command("echo "'"  "ethernets:'" >> ~/99-custom.yaml")

                _stdin, _stdout, _stderr = ssh.exec_command("echo "'"    "eth0:'" >> ~/99-custom.yaml")

                _stdin, _stdout, _stderr = ssh.exec_command("echo "'"      "dhcp4: false'" >> ~/99-custom.yaml")

                _stdin, _stdout, _stderr = ssh.exec_command("echo "'"      "addresses:'"  >> ~/99-custom.yaml")

                _stdin, _stdout, _stderr = ssh.exec_command("echo "f'"        "- {new_ip}'" >> ~/99-custom.yaml")

                _stdin, _stdout, _stderr = ssh.exec_command("echo "f'"      "gateway4: {gateway}'" >> ~/99-custom.yaml")

                _stdin, _stdout, _stderr = ssh.exec_command("sudo cp ~/99-custom.yaml /etc/netplan/99-custom.yaml")

                ssh.close()
                # ...
            except paramiko.AuthenticationException:
                # Handle authentication errors
                # print("Authentication failed for %s" % ip_address)
                messagebox.showinfo(title="Exception", message="Authentication failed for %s" % ip_address)
            except socket.timeout:
                # Handle connection timeout errors
                # print("Connection timed out for %s" % ip_address)
                messagebox.showinfo(title="Exception", message="Connection timed out for %s" % ip_address)
            except socket.error as e:
                # Handle other socket errors
                # print("Socket error occurred: %s" % e)
                messagebox.showinfo(title="Exception", message="Socket error occurred: %s" % ip_address)
            except EOFError as e:
                # print("EOF error occurred: %s" % e)
                messagebox.showinfo(title="Exception", message="EOF error occurred: %s" % ip_address)
            except Exception as e:
                # Handle any other exceptions
                # print("An error occurred: %s" % e)
                messagebox.showinfo(title="Exception", message="Exception error occurred: %s" % ip_address)
            except BaseException as e:
                # Handle any other exceptions
                # print("An error occurred: %s" % e)
                messagebox.showinfo(title="Exception", message="BaseException error occurred: %s" % ip_address)
            finally:
                # Close the SSH connection
                ssh.close()


def check_host_reachable(host):
    cmd = "ping -n 3 " + host
    res = (subprocess.check_output(cmd, shell=True))
    res = res.decode("utf-8")
    if 'unreachable' in res or 'timed out' in res or '100% packet loss' in res:
        # print("Offline")
        return "Offline"
    else:
        # print("Online")
        return "Online"


def resolution_on_select():
    selected_option = resolution_radio_var.get()
    # print(f"Selected option: {selected_option}")


def rotation_on_select():
    selected_option = rotation_radio_var.get()
    # print(f"Selected option: {selected_option}")


def browser_on_select():
    selected_option = browser_radio_var.get()
    # print(f"Selected option: {selected_option}")


def resource_path_icon(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def resource_path_img(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



if __name__ == '__main__':
    # Create EPI-Files folder if none exists
    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)

        # Create the main application window
    root = tk.Tk()
    root.title("Custom Tkinter Application")
    root.iconbitmap("reboot.ico")  # Set the window icon (replace "icon.ico" with your icon file)

    # Set the window size and center it on the screen
    window_width = 600
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 1) - (window_width // 1)
    y = (screen_height // 1) - (window_height // 1)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Load background image
    # bg_image = Image.open("rpi.jpg")  # Replace "background.jpg" with your image file
    # bg_image = bg_image.resize((window_width, window_height))
    # bg_photo = ImageTk.PhotoImage(bg_image)
    # bg_label = tk.Label(root, image=bg_photo)
    # bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Create a frame for organizing widgets
    main_frame = ttk.Frame(root)
    main_frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)





    #Add widgets to the frame
    #LABELS
    device_ip_label = ttk.Label(main_frame, text="Device IP:", font=("Helvetica", 10))
    device_ip_label.grid(column=0, row=1)

    setup_label = ttk.Label(main_frame, text="Setup PI", font=("Helvetica", 10))
    setup_label.grid(column=1, row=2, columnspan=2)

    hostname_label = ttk.Label(main_frame, text="Hostname:", font=("Helvetica", 10))
    hostname_label.grid(column=0, row=3)

    ip_label = ttk.Label(main_frame, text="IP:", font=("Helvetica", 10))
    ip_label.grid(column=0, row=4)

    gateway_label = ttk.Label(main_frame, text="Gateway:", font=("Helvetica", 10))
    gateway_label.grid(column=0, row=5)

    resolution_label = ttk.Label(main_frame, text="Resolution:", font=("Helvetica", 10))
    resolution_label.grid(column=0, row=6)

    rotation_label = ttk.Label(main_frame, text="Rotation:", font=("Helvetica", 10))
    rotation_label.grid(column=0, row=7)

    browser_label = ttk.Label(main_frame, text="Browser", font=("Helvetica", 10))
    browser_label.grid(column=0, row=8)

    url_label = ttk.Label(main_frame, text="eVue URL:", font=("Helvetica", 10))
    url_label.grid(column=0, row=9)

    version_label = ttk.Label(main_frame, text=f"Version:{VERSION}", font=("Helvetica", 7))
    version_label.grid(column=3, row=10)

    signature_label = ttk.Label(main_frame, text="M.Monkweh", font=("Helvetica", 7))
    signature_label.grid(column=0, row=10)

    # TEXT BOXES

    device_ip_textbox = ttk.Entry(main_frame, width=40)
    device_ip_textbox.grid(column=1, row=1, columnspan=1)
    device_ip_textbox.insert(0, "10.8.4.251")

    hostname_textbox = ttk.Entry(main_frame, width=40)
    hostname_textbox.grid(column=1, row=3, columnspan=3)
    hostname_textbox.insert(0, "bananapi")

    ip_textbox = ttk.Entry(main_frame, width=40)
    ip_textbox.grid(column=1, row=4, columnspan=3)
    ip_textbox.insert(0, "10.8.4.251/20")

    gateway_textbox = ttk.Entry(main_frame, width=40)
    gateway_textbox.grid(column=1, row=5, columnspan=3)
    gateway_textbox.insert(0, "10.8.15.254")

    url_textbox = ttk.Entry(main_frame, width=40)
    url_textbox.grid(column=1, row=9, columnspan=3)
    url_textbox.insert(0, '"http://10.8.15.119/evue_by_ip"')



    # RADIO BUTTONS

    resolution_frame = ttk.LabelFrame(main_frame, text="Choose One")
    resolution_frame.grid(column=1, row=6, pady=10)

    rotation_frame = ttk.LabelFrame(main_frame, text="Choose One")
    rotation_frame.grid(column=1, row=7, pady=10)

    browser_frame = ttk.LabelFrame(main_frame, text="Choose One")
    browser_frame.grid(column=1, row=8, pady=10)

    resolution_radio_var = tk.StringVar(value="Option 1")
    rotation_radio_var = tk.StringVar(value="Option 2")
    browser_radio_var = tk.StringVar(value="Option 3")

    resolution_radio_button_1 = ttk.Radiobutton(resolution_frame, text="1440p", variable=resolution_radio_var, value="1440x900p60hz")
    resolution_radio_button_1.grid(column=1, row=6, columnspan=1, padx=10, pady=0, )
    resolution_radio_button_2 = ttk.Radiobutton(resolution_frame, text="1080p", variable=resolution_radio_var, value="1080p60hz")
    resolution_radio_button_2.grid(column=2, row=6, columnspan=1, padx=10, pady=0, )
    resolution_radio_button_3 = ttk.Radiobutton(resolution_frame, text="2160p", variable=resolution_radio_var, value="2160p60hz")
    resolution_radio_button_3.grid(column=3, row=6, columnspan=1, padx=10, pady=0, )

    rotation_radio_button_1 = ttk.Radiobutton(rotation_frame, text="Left", variable=rotation_radio_var, value='        Option "rotate" "ccw"')
    rotation_radio_button_1.grid(column=1, row=7, columnspan=1, padx=10, pady=0, )
    rotation_radio_button_2 = ttk.Radiobutton(rotation_frame, text="Right", variable=rotation_radio_var, value='        Option "rotate" "cw"')
    rotation_radio_button_2.grid(column=2, row=7, columnspan=1, padx=10, pady=0, )
    rotation_radio_button_3 = ttk.Radiobutton(rotation_frame, text="Normal", variable=rotation_radio_var, value='        Option "rotate" "c"')
    rotation_radio_button_3.grid(column=3, row=7, columnspan=1, padx=10, pady=0, )

    browser_radio_button_1 = ttk.Radiobutton(browser_frame, text="Chrome", variable=browser_radio_var, value='Chrome')
    browser_radio_button_1.grid(column=1, row=8, columnspan=1, padx=10, pady=0, )
    browser_radio_button_2 = ttk.Radiobutton(browser_frame, text="Firefox", variable=browser_radio_var, value='Firefox')
    browser_radio_button_2.grid(column=2, row=8, columnspan=1, padx=10, pady=0, )



    # BUTTONS

    reboot_button = ttk.Button(main_frame, text="Reboot", command=reboot, width=15)
    reboot_button.grid(column=2, row=1, columnspan=2, padx=10, pady=0, )


    apply_button = ttk.Button(main_frame, text="Apply", command=setup, width=15)
    apply_button.grid(column=1, row=10, columnspan=2, padx=10, pady=0, )






















































































    #
    # check_var1 = tk.IntVar()
    # check_var2 = tk.IntVar()
    # check1 = ttk.Checkbutton(main_frame, text="Check 1", variable=check_var1)
    # check1.grid(pady=10)
    # check2 = ttk.Checkbutton(main_frame, text="Check 2", variable=check_var2)
    # check2.grid()

    # # Create tabs
    # tab_control = ttk.Notebook(main_frame)
    # tab1 = ttk.Frame(tab_control)
    # tab2 = ttk.Frame(tab_control)
    # tab_control.add(tab1, text='Tab 1')
    # tab_control.add(tab2, text='Tab 2')
    #
    # tab_control.grid(expand=1, fill="both")
    #
    # # Menu
    # menu_bar = tk.Menu(root)
    # root.config(menu=menu_bar)
    #
    # file_menu = tk.Menu(menu_bar, tearoff=0)
    # menu_bar.add_cascade(label="File", menu=file_menu)
    # file_menu.add_command(label="New")
    # file_menu.add_separator()
    # file_menu.add_command(label="Exit", command=root.quit)
    #
    # help_menu = tk.Menu(menu_bar, tearoff=0)
    # menu_bar.add_cascade(label="Help", menu=help_menu)
    # help_menu.add_command(label="About", command=lambda: messagebox.showinfo("Button Clicked", "You clicked the button!", ))

root.mainloop()
