import winreg
import psutil
import time
from collections import defaultdict
import datetime

# Registry paths for non-packaged app access
MICROPHONE_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone\NonPackaged"
WEBCAM_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam\NonPackaged"
WINDOWS_EPOCH = datetime.datetime(1601, 1, 1)


def filetime_hex_to_datetime(hex_str):
    try:
        ft_int = int(hex_str, 16)
        if ft_int == 0:
            return None
        return WINDOWS_EPOCH + datetime.timedelta(microseconds=ft_int / 10)
    except ValueError:
        return None


def read_registry_usage(capability_path):
    used_apps = []

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, capability_path) as base_key:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(base_key, i)
                    full_subkey_path = f"{capability_path}\\{subkey_name}" 
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, full_subkey_path) as subkey:
                        start_raw = stop_raw = None
                        try:
                            start_raw, _ = winreg.QueryValueEx(subkey, "LastUsedTimeStart")
                            stop_raw, _ = winreg.QueryValueEx(subkey, "LastUsedTimeStop")

                        except FileNotFoundError:
                            pass

                        start_time = filetime_hex_to_datetime(start_raw) if isinstance(start_raw, str) else start_raw
                        stop_time = filetime_hex_to_datetime(stop_raw) if isinstance(stop_raw, str) else stop_raw

                        if start_time and (not stop_time or start_time > stop_time):
                            exe_path = subkey_name.replace("#", "\\")
                            used_apps.append({
                                "path": exe_path,
                                "start_time": start_time,
                                "stop_time": stop_time
                            })

                    i += 1
                except OSError as error:
                    print(f"Error: {error}")
                    break
    except FileNotFoundError:
        pass

    return used_apps

def match_running_processes(app_paths):
    matched_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            proc_exe = proc.info['exe']
            if proc_exe:
                for app_path in app_paths:
                    if app_path["path"].lower() in proc_exe.lower():
                        matched_processes.append((proc.info['pid'], proc.info['name'], proc_exe))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return matched_processes

def print_grouped_results(resource, running_apps):
    if not running_apps:
        print(f"\n{resource} is not currently in use.")
        return

    print(f"\n{resource} is currently in use by:")

    grouped = defaultdict(list)
    for pid, name, path in running_apps:
        grouped[(name, path)].append(pid)

    for (name, path), pids in grouped.items():
        print(f"  {name} -> {path}")
        print(f"    PIDs: {', '.join(str(pid) for pid in pids)}")

def detect_main():
    print("Checking for microphone usage...")
    mic_apps = read_registry_usage(MICROPHONE_PATH)
    mic_running = match_running_processes(mic_apps)
    isMicrophoneInUse = len(mic_running) > 0

    print("Checking for webcam usage...")
    cam_apps = read_registry_usage(WEBCAM_PATH)
    cam_running = match_running_processes(cam_apps)
    isCameraInUse = len(cam_running) > 0

    # print_grouped_results("Microphone", mic_running)
    # print_grouped_results("Camera", cam_running)

    # Export or return if needed
    return {
        "isMicrophoneInUse": isMicrophoneInUse,
        "isCameraInUse": isCameraInUse,
        "microphoneProcesses": mic_running,
        "cameraProcesses": cam_running,
    }
def check_camera_and_mic_status():
    result = detect_main()
    is_cam, is_mic = result['isCameraInUse'], result['isMicrophoneInUse']
    return is_cam, is_mic



# if __name__ == "__main__":
#     while True:
#         result = detect_main()
#         # Example access:
#         print("\n[DEBUG] Flags:")
#         print(f"Microphone in use: {result['isMicrophoneInUse']}")
#         print(f"Camera in use: {result['isCameraInUse']}")
#         time.sleep(5)