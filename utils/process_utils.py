import psutil

def kill_processes_by_name(name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == name:
            try:
                proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                pass

def list_dlls_by_pid(pid):
    try:
        proc = psutil.Process(pid)
        dlls = proc.memory_maps()
        result = []
        for dll in dlls:
            if dll.path.lower().endswith('.dll'):
                result.append(dll.path)
        return result
    except:
        pass

def get_pids_by_name(name):
    pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] == name:
                pids.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return pids
def find_process_paths_by_name(name: str):
    matches = []
    for proc in psutil.process_iter(attrs=['pid', 'name', 'exe']):
        try:
            if name.lower() in proc.info['name'].lower():
                matches.append(proc.info['exe'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return list(filter(None, matches))
