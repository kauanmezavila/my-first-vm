<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=180&color=0:111111,50:b91c1c,100:ef4444&text=My%20First%20VM&fontColor=ffffff&fontAlignY=35&desc=BIOS%20fake%20%2B%20terminal%20Debian%20em%20Python&descAlignY=56" alt="My First VM banner">
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Terminal" src="https://img.shields.io/badge/Terminal-BIOS%20VM-b91c1c?style=for-the-badge&logo=gnubash&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-111111?style=for-the-badge">
</p>

# My First VM

Um simulador de BIOS/VM feito em Python: voce inicia uma BIOS fake, navega por um mini filesystem, da deploy em uma ISO Debian simulada e entra em um terminal com comandos basicos e pacotes instalaveis.

## Preview

```text
root@main-vm~$: ls

Ventoy
etc
init-SHA265.txt

root@main-vm~$: deploy Debian-12.7.0-amd64-netinst.iso
[ OK ] Deploying and starting Debian-12.7.0-amd64-netinst.iso

user@linux-debian~$: neofetch
OS: Debian 12.7.0 amd64
Kernel: Linux 6.17.0-35-generic
ISO: Debian-12.7.0-amd64-netinst.iso
```

## Features

| Area | O que tem |
| --- | --- |
| BIOS | Splash screen, prompt `root@main-vm`, filesystem em memoria |
| Deploy | Carrega a ISO fake `Debian-12.7.0-amd64-netinst.iso` |
| Debian VM | Terminal com `cd`, `ls`, `pwd`, `cat`, `mkdir`, `touch`, `rm`, `rmdir` |
| Pacotes | `apt install <pkg>` para comandos em `BIOS/src/pkgs` |
| Extras | `neofetch`, `cowsay`, persistencia via JSON |

## Como rodar

```bash
cd BIOS
python3 -m pip install questionary
python3 terminal-bios.py
```

> Precisa rodar em um terminal interativo. Pipe/execucao sem TTY quebra o menu visual.

## Comandos

| Comando | Onde | Uso |
| --- | --- | --- |
| `help` | BIOS/Debian | Lista comandos disponiveis |
| `ls` | BIOS/Debian | Mostra arquivos e diretorios |
| `cd <dir>` | BIOS/Debian | Entra em um diretorio |
| `cat <file>` | BIOS/Debian | Mostra conteudo de arquivo |
| `deploy <.iso>` | BIOS | Inicia uma ISO simulada |
| `apt install cowsay` | Debian | Instala o pacote `cowsay` |
| `apt install neofetch` | Debian | Instala o pacote `neofetch` |
| `exit` | BIOS/Debian | Encerra o terminal atual |

## Estrutura

```text
BIOS/
├── terminal-bios.py        # entrada da BIOS
├── deploy.py               # executor da ISO fake
├── files_bios.py           # filesystem da BIOS
├── VMs/Debian/             # manifest e bootstrap da VM Debian
└── src/
    ├── Debian/             # terminal e filesystem da VM
    └── pkgs/               # pacotes instalaveis
```

## Licenca

MIT. Veja [`LICENSE`](LICENSE).
