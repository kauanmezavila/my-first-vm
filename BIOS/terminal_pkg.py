import os
import re
import shutil
import questionary
import time

from src.pkgs.colorme import *


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def visible_len(text: str) -> int:
    return len(ANSI_RE.sub("", text))


def print_centered(text: str, width: int):
    largura_visivel = visible_len(text)

    esquerda = max(0, (width - largura_visivel) // 2)
    direita = max(0, width - esquerda - largura_visivel)

    print(
        f"{BG_BLACK}"
        + (" " * esquerda)
        + text
        + (" " * direita)
        + RESET
    )


def main_splash() -> str:
    clear()

    opcoes = ["Start", "Exit"]

    largura_terminal, altura_terminal = shutil.get_terminal_size()

    banner = [
        f"███{RED}╗   {WHITE}███{RED}╗{WHITE}██{RED}╗   {WHITE}██{RED}╗    {WHITE}███████{RED}╗{WHITE}██{RED}╗{WHITE}██████{RED}╗ {WHITE}███████{RED}╗{WHITE}████████{RED}╗    {WHITE}██{RED}╗   {WHITE}██{RED}╗{WHITE}███{RED}╗   {WHITE}███{RED}╗",
        f"{WHITE}████{RED}╗ {WHITE}████{RED}║╚{WHITE}██{RED}╗ {WHITE}██{RED}╔╝    {WHITE}██{RED}╔════╝{WHITE}██║{WHITE}██{RED}╔══{WHITE}██{RED}╗{WHITE}██{RED}╔════╝╚══{WHITE}██{RED}╔══╝    {WHITE}██{RED}║   {WHITE}██{RED}║{WHITE}████{RED}╗ {WHITE}████{RED}║",
        f"{WHITE}██{RED}╔{WHITE}████{RED}╔{WHITE}██{RED}║ ╚{WHITE}████{RED}╔╝     {WHITE}█████{RED}╗  {WHITE}██{RED}║{WHITE}██████{RED}╔╝{WHITE}███████{RED}╗   {WHITE}██{RED}║       {WHITE}██{RED}║   {WHITE}██{RED}║{WHITE}██{RED}╔{WHITE}████{RED}╔{WHITE}██{RED}║",
        f"{WHITE}██{RED}║╚{WHITE}██{RED}╔╝{WHITE}██{RED}║  ╚{WHITE}██{RED}╔╝      {WHITE}██{RED}╔══╝  {WHITE}██{RED}║{WHITE}██{RED}╔══{WHITE}██{RED}╗╚════{WHITE}██{RED}║   {WHITE}██{RED}║       {RED}╚{WHITE}██{RED}╗ {WHITE}██{RED}╔╝{WHITE}██{RED}║╚{WHITE}██{RED}╔╝{WHITE}██{RED}║",
        f"{WHITE}██{RED}║ ╚═╝ {WHITE}██{RED}║   {WHITE}██{RED}║       {WHITE}██{RED}║     {WHITE}██{RED}║{WHITE}██{RED}║  {WHITE}██{RED}║{WHITE}███████{RED}║   {WHITE}██{RED}║        ╚{WHITE}████{RED}╔╝ {WHITE}██{RED}║ ╚═╝ {WHITE}██{RED}║",
        f"{RED}╚═╝     ╚═╝   ╚═╝       ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝         ╚═══╝  ╚═╝     ╚═╝",
    ]

    linhas_totais = len(banner) + len(opcoes) + 8
    padding_vertical = max(
        0,
        (altura_terminal - linhas_totais) // 2
    )

    print("\n" * padding_vertical, end="")

    # Barra superior
    print(
        f"{BG_BLACK}"
        + (" " * largura_terminal)
        + RESET
    )

    # Banner
    for linha in banner:
        print_centered(linha, largura_terminal)

    # Barra inferior
    print(
        f"{BG_BLACK}"
        + (" " * largura_terminal)
        + RESET
    )

    print()

    menu_padding = max(
        0,
        (largura_terminal // 2) - 8
    )

    opcoes_centralizadas = [
        questionary.Choice(
            title=(" " * menu_padding) + opcao,
            value=opcao
        )
        for opcao in opcoes
    ]

    escolha = questionary.select(
        "",
        choices=opcoes_centralizadas,
        qmark="»"
    ).ask()

    if escolha is None:
        return "Exit"

    time.sleep(0.2)

    return escolha


def bios_banner():
    print("""
[Award Modular BIOS v6.00PG]
Copyright (C) 1984-2026, Award Software, Inc.
""")