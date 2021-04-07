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
    print(f"ONUs without errors: {len(without_errors)}")
    print(f"ONUs with errors: {len(with_errors)}")


def save_to_jsonfile(file_dict):
    path = join(os.getcwd() + "/olt8820g", "onu_inventory.json")
    with open(path, "w") as jsonfile:
        json.dump(file_dict, jsonfile)


def run_onu_inventory_command(connect_handler=None, port=None):

    command = f'onu inventory 1/{port}'
    cli_output = run_command(command, connect_handler, sleep_time=2)

    if 'Do you want to continue?  (yes or no) [no] ' in cli_output.splitlines():
        command = "yes"
        cli_output += run_command(command, connect_handler, sleep_time=10)

        command = "a"
        cli_output += run_command(command, connect_handler,
                                  sleep_time=15, delay_factor=5)

    return cli_output


def _fit_goodline_to_10length(output=None):
    onus = []

    for output_line in output.splitlines()[10:-5]:
        tmp = output_line.split()
        # tmp[7:9] = [str([' '.join(tmp[7:9])])]

        # remove 'dbm' word from good lines
        if len(tmp) == 12:
            del(tmp[8])
            del(tmp[9])
        onus.append(tmp)

    return onus


def _clioutput_list_to_dict(output_list):

    list_to_dict = {}
    if output_list is not None:
        for row in output_list:
            # 'i' var is a tuple with len == 2. The second position(index == 1) is the key to dict 'list_to_dict'
            i = row.pop(0)
            list_to_dict[i[1]] = dict(row)

    return list_to_dict


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
        port = input("Type GPON port to command 'onu inventory' [1-8]: ")
        output = run_onu_inventory_command(connect_handler=device, port=port)

    onus = _fit_goodline_to_10length(output)

    onu_inventory_header = 'id port serial sernoID modelo hw_versao sw_versao olt_rx olt_tx distancia'.split()
    onus_with_errors = []
    onus_without_errors = []

    for onu in onus:
        # FIXME: corrigir para quando existir o valor 'ERROR' em uma/várias posições da variável 'onu'
        # if len(onu) != 10 and 'error' in onu:
        if 'error' in onu or 'dbm' in onu or '-' in onu:
            # poped_with_error_index.append(onu.pop(0))
            onus_with_errors.append(list(zip(onu_inventory_header, onu)))
        else:
            onus_without_errors.append(list(zip(onu_inventory_header, onu)))

    onus_without_errors_dict = _clioutput_list_to_dict(onus_without_errors)
    onus_with_errors_dict = _clioutput_list_to_dict(onus_with_errors)

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
