import json
import os
import time
from os.path import dirname, join
from dotenv import load_dotenv
from netmiko import ConnectHandler


def load_dotenv_file(file='.env'):

    dotenv_path = join(dirname(__file__), file)
    load_dotenv(dotenv_path)

    return {
        "username": os.environ.get("DEVICE_USERNAME"),
        "password": os.environ.get("DEVICE_PASSWORD"),
        "ip": os.environ.get("DEVICE_IP")
    }


def set_connection_params(port='22', host=None, username='intelbras', password=None, device_type='cisco_ios'):

    return {
        'port': port,
        'host': host,
        'username': username,
        'password': password,
        'device_type': device_type,
        'verbose': True,
        'global_delay_factor': 10
    }


def run_command(command=None, context=None, sleep_time=5, delay_factor=2):

    output = context.send_command_timing(
        command_string=command,
        strip_prompt=False,
        strip_command=False,
        delay_factor=delay_factor
    )
    time.sleep(sleep_time)

    return output


def show_inventory_status(with_errors=None, without_errors=None):
    print("#" * 20)
    print(f"ONUs without errors type is: {type(without_errors)}")
    print(f"ONUs without errors: {len(without_errors)}")
    print(f"ONUs with errors type is: {type(with_errors)}")
    print(f"ONUs with errors: {len(with_errors)}")


def save_to_jsonfile(file_dict):
    path = join(os.getcwd() + "/olt8820g", "onu_inventory.json")
    with open(path, "w") as jsonfile:
        json.dump(file_dict, jsonfile)


def _onu_inventory_command():
    pass

def main():

    credentials = load_dotenv_file()
    zhone_intelbras = set_connection_params(
        host=credentials["ip"], password=credentials["password"])

    print('Connecting...')

    with ConnectHandler(**zhone_intelbras) as device:

        print('Connected to OLT, gathering info....')

        device.send_command('setline 0')
        time.sleep(4)

        # TODO: menu with commands options
        # menu()

        # _onu_inventory_command(connect_handler=device)
        port = input("Type GPON port to command 'onu inventory' [1-8]: ")
        command = f'onu inventory 1/{port}'
        cli_output = run_command(command, device, sleep_time=2)

        if 'Do you want to continue?  (yes or no) [no] ' in output.splitlines():
            command = "yes"
            cli_output += run_command(command, device, sleep_time=10)

        command = "a"
        cli_output += run_command(command, device,
                                  sleep_time=15, delay_factor=5)

    onus = []

    for output_line in cli_output.splitlines()[10:-5]:
        tmp = output_line.split()
        # tmp[7:9] = [str([' '.join(tmp[7:9])])]
        if len(tmp) == 12:
            del(tmp[8])
            del(tmp[9])

        onus.append(tmp)

    onu_inventory_header = 'id port serial sernoID modelo hw_versao sw_versao olt_rx olt_tx distancia'.split()
    onus_with_errors = []
    onus_without_errors = []
    # poped_without_error_index = 0
    # poped_with_error_index = 0

    for onu in onus:
        # FIXME: corrigir para quando existir o valor 'ERROR' em uma/várias posições da variável 'onu'
        # if len(onu) != 10 and 'error' in onu:
        if 'error' in onu or 'dbm' in onu or '-' in onu:
            # poped_with_error_index.append(onu.pop(0))
            onus_with_errors.append(list(zip(onu_inventory_header, onu)))

        else:
            # poped_without_error_index.append(onu.pop(0))
            onus_without_errors.append(list(zip(onu_inventory_header, onu)))
            # onus_without_errors.append(dict(zip(onu_inventory_header, onu)))

    onus_without_errors_dict = {}
    if onus_without_errors is not None:

        print("#" * 20)

        for onu_without_error_field in onus_without_errors:
            i = onu_without_error_field.pop(0)
            onus_without_errors_dict[i[1]] = dict(onu_without_error_field)

    onus_with_errors_dict = {}
    if onus_with_errors is not None:

        print("#" * 20)

        for onu_with_error_field in onus_with_errors:
            i = onu_with_error_field.pop(0)
            onus_with_errors_dict[i[1]] = dict(onu_with_error_field)

    port_inventory = {}

    port_inventory[f"gpon{port}"] = {}
    port_inventory[f"gpon{port}"]['without_errors'] = onus_without_errors_dict
    port_inventory[f"gpon{port}"]['with_errors'] = onus_with_errors_dict

    print(json.dumps(port_inventory, indent=2))
    show_inventory_status(
        without_errors=onus_without_errors_dict, with_errors=onus_with_errors_dict)
    save_to_jsonfile(port_inventory)


if __name__ == "__main__":
    main()
