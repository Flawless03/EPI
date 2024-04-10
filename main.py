import subprocess
import sys
from tkinter import *
from tkinter import messagebox
import os, socket, paramiko

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

    # ---------------------------- UI SETUP ------------------------------- #
    # Window instance
    window = Tk()
    icon = window.wm_iconbitmap(resource_path_icon("E_PI_White.ico"))
    window.title("eVue PI Configurator".upper())
    window.config(bg="white")

    # canvas creation
    canvas = Canvas(width=150, height=100, bg="white", highlightthickness=0)
    my_pass_img = PhotoImage(file=resource_path_img("E_PI_White_good.png"))
    canvas.create_image(80, 50, image=my_pass_img)
    canvas.grid(column=0, row=0, columnspan=4)

    # LABELS
    device_ip_label = Label(text="Device IP:", bg=WHITE, padx=10, pady=10, font=("New Roman", 11, "bold"))
    device_ip_label.grid(column=0, row=1)

    setup_label = Label(text="Setup PI", bg=WHITE, padx=10, pady=10, font=("New Roman", 16, "bold"))
    setup_label.grid(column=1, row=2, columnspan=2)

    hostname_label = Label(text="Hostname:", bg=WHITE, padx=10, pady=10, font=("New Roman", 11, "bold"))
    hostname_label.grid(column=0, row=3)

    ip_label = Label(text="IP:", bg=WHITE, padx=10, pady=10, font=("New Roman", 11, "bold"))
    ip_label.grid(column=0, row=4)

    gateway_label = Label(text="Gateway:", bg=WHITE, padx=10, pady=10, font=("New Roman", 11, "bold"))
    gateway_label.grid(column=0, row=5)

    resolution_label = Label(text="Resolution:", bg=WHITE, padx=10, pady=10, font=("New Roman", 11, "bold"))
    resolution_label.grid(column=0, row=6)

    rotation_label = Label(text="Rotation:", bg=WHITE, padx=10, pady=10, font=("New Roman", 11, "bold"))
    rotation_label.grid(column=0, row=7)

    browser_label = Label(text="Browser:", bg=WHITE, padx=10, pady=10, font=("New Roman", 11, "bold"))
    browser_label.grid(column=0, row=8)

    url_label = Label(text="eVue URL:", bg=WHITE, padx=10, pady=10, font=("New Roman", 11, "bold"))
    url_label.grid(column=0, row=9)

    version_label = Label(text=f"Version {VERSION}", bg=WHITE, padx=10, pady=10, font=("New Roman", 7, "bold"))
    version_label.grid(column=3, row=10)

    signature_label = Label(text=f"M.Monkweh", bg=WHITE, padx=10, pady=10, font=("New Roman", 7, "bold"))
    signature_label.grid(column=0, row=10)

    # TEXTBOXES
    device_ip_textbox = Entry()
    device_ip_textbox.grid(column=1, row=1, columnspan=1)
    device_ip_textbox.focus()
    device_ip_textbox.insert(0, "10.8.4.251")

    hostname_textbox = Entry(width=40)
    hostname_textbox.grid(column=1, row=3, columnspan=3)
    hostname_textbox.insert(0, "bananapi")

    ip_textbox = Entry(width=40)
    ip_textbox.grid(column=1, row=4, columnspan=3)
    ip_textbox.insert(0, "10.8.4.251/20")

    gateway_textbox = Entry(width=40)
    gateway_textbox.grid(column=1, row=5, columnspan=3)
    gateway_textbox.insert(0, "10.8.15.254")

    url_textbox = Entry(width=40)
    url_textbox.grid(column=1, row=9, columnspan=3)
    url_textbox.insert(0, '"http://10.8.15.119/evue_by_ip"')

    # RADIO BUTTONS

    # Create a variable to hold the selected option
    resolution_radio_var = StringVar()
    rotation_radio_var = StringVar()
    browser_radio_var = StringVar()

    # Create Resolution Radio buttons
    resolution_radio_button_1 = Radiobutton(window, text="1440p", variable=resolution_radio_var,
                                            value='"1440x900p60hz"', bg="white", command=resolution_on_select)
    resolution_radio_button_1.grid(column=1, row=6, columnspan=1, padx=10, pady=0, )
    resolution_radio_button_2 = Radiobutton(window, text="1080p", variable=resolution_radio_var, value='"1080p60hz"',
                                            bg="white", command=resolution_on_select)
    resolution_radio_button_2.grid(column=2, row=6, columnspan=1, padx=10, pady=0, )
    resolution_radio_button_3 = Radiobutton(window, text="2160p", variable=resolution_radio_var, value='"2160p60hz"',
                                            bg="white", command=resolution_on_select)
    resolution_radio_button_3.grid(column=3, row=6, columnspan=1, padx=10, pady=0, )

    # Create Rotation Radio buttons
    rotation_radio_button_1 = Radiobutton(window, text="Left", variable=rotation_radio_var,
                                          value='        Option "rotate" "ccw"', bg="white", command=rotation_on_select)
    rotation_radio_button_1.grid(column=1, row=7, columnspan=1, padx=10, pady=0, )
    rotation_radio_button_2 = Radiobutton(window, text="Right", variable=rotation_radio_var,
                                          value='        Option "rotate" "cw"', bg="white", command=rotation_on_select)
    rotation_radio_button_2.grid(column=2, row=7, columnspan=1, padx=10, pady=0, )
    rotation_radio_button_3 = Radiobutton(window, text="Normal", variable=rotation_radio_var,
                                          value='        Option "rotate" "c"', bg="white", command=rotation_on_select)
    rotation_radio_button_3.grid(column=3, row=7, columnspan=1, padx=10, pady=0, )

    # Create Browser Radio buttons
    browser_radio_button_1 = Radiobutton(window, text="Chrome", variable=browser_radio_var, value='Chrome', bg="white",
                                         command=browser_on_select)
    browser_radio_button_1.grid(column=1, row=8, columnspan=1, padx=10, pady=0, )
    browser_radio_button_2 = Radiobutton(window, text="Firefox", variable=browser_radio_var, value='Firefox',
                                         bg="white", command=browser_on_select)
    browser_radio_button_2.grid(column=2, row=8, columnspan=1, padx=10, pady=0, )

    # BUTTONS
    reboot_button = Button(text="Reboot", command=reboot, padx=0, pady=0, width=15, bg=WHITE,
                           font=("New Roman", 11, "bold"))
    reboot_button.grid(column=2, row=1, columnspan=2, padx=10, pady=0, )

    apply_button = Button(text="Apply", command=setup, padx=0, pady=0, width=15, bg=WHITE,
                          font=("New Roman", 11, "bold"))
    apply_button.grid(column=1, row=10, columnspan=2, padx=10, pady=10, )

    mainloop()

# Developed by Mywiah Monkweh
