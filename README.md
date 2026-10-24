<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=180&color=0:111111,50:b91c1c,100:ef4444&text=My%20First%20VM&fontColor=ffffff&fontAlignY=35&descAlignY=56" alt="Banner My First VM">
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Terminal" src="https://img.shields.io/badge/Terminal-BIOS%20VM-b91c1c?style=for-the-badge&logo=gnubash&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-111111?style=for-the-badge">
</p>

# My First VM

Um simulador interativo de BIOS e máquinas virtuais feito em Python. A BIOS tem um filesystem em memória e um menu de inicialização; nela, você escolhe uma ISO simulada para abrir um terminal de Debian, Kali Linux ou Ubuntu.

> As ISOs e os sistemas operacionais são simulados pelo projeto. Eles não iniciam uma máquina virtual real.

## Funcionalidades

- Menu de inicialização e prompt da BIOS (`root@main-vm`).
- Navegação e edição do filesystem simulado com `cd`, `ls`, `pwd`, `cat`, `mkdir`, `rmdir`, `touch` e `rm`.
- Deploy das imagens Debian 12.7.0, Kali Linux 2026.2 e Ubuntu 26.10.
- Terminais por distribuição, com comandos básicos, informações de sistema e persistência de arquivos em JSON.
- Gerenciador `apt` simulado para instalar, remover e listar pacotes.
- Pacotes de exemplo: `cowsay`, `neofetch`, `tree`, `nano`, `fortune`, `nmap`, `firefox` e `google`.

## Requisitos e execução

Requer Python 3 e um terminal interativo (TTY), pois o menu inicial usa `questionary`.

```bash
python3 -m pip install -r requirements.txt
cd BIOS
python3 terminal-bios.py
```

No menu, selecione **Start**. Na BIOS, use `ls` para ver o filesystem, `cd Ventoy` para entrar na pasta das imagens e `deploy <arquivo.iso>` para iniciar uma distribuição. Por exemplo:

```text
root@main-vm$: cd Ventoy
root@main-vm(Ventoy)$: ls
root@main-vm(Ventoy)$: deploy Debian-12.7.0-amd64-netinst.iso
```

As imagens disponíveis são:

| Distribuição | Arquivo ISO simulado |
| --- | --- |
| Debian 12.7.0 | `Debian-12.7.0-amd64-netinst.iso` |
| Kali Linux 2026.2 | `Kali-2026.2-amd64.iso` |
| Ubuntu 26.10 | `Ubuntu-26.10-amd64-netinst.iso` |

## Comandos

Na BIOS, `help` lista os comandos. Além dos comandos de filesystem, estão disponíveis `deploy <.iso>`, `config` (inclui `config cpu enable|disable`) e `exit`.

Nos terminais das distribuições, `help` mostra os comandos básicos. O gerenciador de pacotes oferece:

```text
apt list                 # lista pacotes locais
apt install <pacote>     # instala um pacote
apt rm <pacote>          # remove um pacote
apt update               # atualiza os arquivos de pacotes remotos
```

Para explorar os utilitários depois de instalá-los, consulte `help`, `nmap --help`, `firefox --help` ou `google --help`, conforme o pacote.

## Estrutura do projeto

```text
BIOS/
├── terminal-bios.py      # entrada e prompt da BIOS
├── deploy.py             # carrega uma imagem simulada
├── files_bios.py         # filesystem inicial da BIOS e imagens
├── VMs/                  # manifests e inicialização Debian, Kali e Ubuntu
└── src/
    ├── Debian/           # terminal, filesystem e pacotes da VM Debian
    ├── Kali/             # terminal, filesystem e pacotes da VM Kali
    ├── Ubuntu/           # terminal, filesystem e pacotes da VM Ubuntu
    └── pkgs/             # utilitários instaláveis
```

## Licença

MIT. Consulte [`LICENSE`](LICENSE).
