**🏗️ Em construção 🏗️**

# Acesso de informações da OLT Intelbras 8820G

Os scripts deste repositório são para *estudo* de acesso remoto através do pacote [Netmiko](https://pypi.org/project/netmiko/).

A ideia geral é fazer um pequeno parser da CLI do equipamento e automatizar algumas rotinas como provisionamento e remoção de ONUs/ONTs, criação de VLANs, backup da configuração, entre outras tarefas. No momento, só existe a possibilidade de executar o comando *"onu inventory 1/x"*, onde "x" é uma porta GPON e então entregar um arquivo json.

Exemplo de saída do comando onu inventoryna porta GPON 3
```
iSH> onu inventory 1/3

Processing list of 64

This command may take several minutes to complete.
Do you want to continue?  (yes or no) [no] yes

                           Serial    Vendor  Model       ONT       Software    ONT       OLT     Distance
ID       Interface         Number      ID     ID       Version     Version   Rx Power  Rx Power   (KM)
=== ==================== ========== ======= ====== ============== ========== ========= ========= ===========
1   1-1-3-1              8B69A245   ITBS    110Gb   PON110B_v3.0 1.0-200522 -17.2 dBm -13.7 dBm      1.0870
2   1-1-3-2              8B6981B9   ITBS    110Gb   PON110B_v3.0 1.0-200522 -12.0 dBm -12.0 dBm      1.0541
3   1-1-3-3              326237CA   ITBS    110Gb   PON110B_v3.0 1.0-200522 -10.8 dBm -12.2 dBm      1.0829
4   1-1-3-4              326237E0   ITBS    110Gb   PON110B_v3.0 1.0-200522 -12.4 dBm -11.0 dBm      1.1849
5   1-1-3-5              326237E2   ITBS    110Gb   PON110B_v3.0 1.0-200522 -11.2 dBm -11.4 dBm      1.2049
6   1-1-3-6              326237E4   ITBS    110Gb   PON110B_v3.0 1.0-200522 -11.0 dBm -11.7 dBm      1.1696
7   1-1-3-7              8B693819   ITBS      -          -           - error error error
8   1-1-3-8              E86CC854   ITBS    110Gb   PON110B_v3.0 1.0-200522 -11.1 dBm -11.6 dBm      1.1577
9   1-1-3-9              3252E03E   ITBS    110Gb   PON110B_v3.0 1.0-200522 -11.2 dBm -12.8 dBm      1.1533
10  1-1-3-10             32626F5E   ITBS    110Gb   PON110B_v3.0 1.0-200522 -10.8 dBm -11.5 dBm      1.0947
11  1-1-3-11             326237C4   ITBS    110Gb   PON110B_v3.0 1.0-200522 -14.6 dBm -12.8 dBm      1.0703
13  1-1-3-13             3252E035   ITBS    110Gb   PON110B_v3.0 1.0-200522 -12.4 dBm -13.7 dBm      1.0680
14  1-1-3-14             3252E02B   ITBS    110Gb   PON110B_v3.0 1.0-200522 -15.8 dBm -12.7 dBm      1.0930
Total ONUs = 13

iSH> 
```

## Dependências
- [DotEnv](https://pypi.org/project/python-dotenv/) >= 0.17.0
- [Netmiko](https://pypi.org/project/netmiko/) >= 3.3.3
- [Python](https://www.python.org/) >= 3.7

## Setup do *virtualenv*

1. Clone o repo e entre na pasta 
```
git clone https://github.com/ojpojao/olt8820g.git
cd olt8820g
```
2. instalar, criar e ativar o pacote virtualenv

2.1 Ubuntu, Debian, Mint
```
sudo apt update
sudo apt install -y python3-pip python3-venv
python3 -m venv venv
```
2.2 Fedora
```
sudo dnf install -y python3-virtualenv
python3 -m virtualenv venv
```
2.3
```
source venv/bin/actvate
```

## Instale as dependências

Com o virtualenv ativo, instale as dependências:
```
pip install -r requirements.txt
```

## Preparando para conectar por SSH na OLT 8820G

Comente as linhas 269 até 272 no arquivo: 

```sh
vim $PWD/venv/lib64/pythonx.y/site-packages/cryptography/hazmat/primitives/asymetric/dsa.py
```

```python
def _check_dsa_parameters(parameters: DSAParameterNumbers):
    # if parameters.p.bit_length() not in [1024, 2048, 3072, 4096]:
    #     raise ValueError(
    #         "p must be exactly 1024, 2048, 3072, or 4096 bits long"
    #     )
    if parameters.q.bit_length() not in [160, 224, 256]:
        raise ValueError("q must be exactly 160, 224, or 256 bits long")

    if not (1 < parameters.g < parameters.p):
        raise ValueError("g, p don't satisfy 1 < 
```
x e y refere-se a sua versão do Python.

As credenciais devem ser colocadas no arquivo '*.env*', usuário, senha e o ip do dispositivo. Por exemplo:
```
vim $PWD/.env
```

```
DEVICE_IP="192.168.1.254"
DEVICE_USERNAME="root"
DEVICE_PASSWORD="abcdef"
```

## Rodando o script
Os scripts main00.py e main01.py fazem a mesma coisa
```sh
python main00.py
```
```sh
python main01.py
```
Será solicitado a porta GPON para buscar as informações. 
```
Type GPON port to command 'onu inventory' [1-8]: 8
```

Ao término da execução do script, será criado um arquivo json com as informações solicitadas da porta.