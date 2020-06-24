#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import discord
import requests
from discord.ext import commands
import asyncio
import datetime
import time
import os
from ast import literal_eval
from src.rune import *
from src.interface import *

# ╦  ┌─┐┌─┐  ╔═╗┬ ┬┬ ┬  ┬┬┌┬┐┬─┐┌─┐┌─┐
# ║  ├┤ └─┐  ╚═╗└┬┘│ └┐┌┘│ ││├┬┘├┤ └─┐
# ╩═╝└─┘└─┘  ╚═╝ ┴ ┴─┘└┘ ┴─┴┘┴└─└─┘└─┘

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ ENV @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# rootme_list = literal_eval(os.environ['arena_rm_list'])
# wechall_list = literal_eval(os.environ['arena_wc_list'])

# codeanon_id = int(os.environ['arena_ca_id'])
# ctf_chan_id = int(os.environ['arena_ctf_id'])
# test_chan_id = int(os.environ['arena_test_id'])

# flag_ctf_rentree = os.environ['arena_flag']
# token = os.environ['arena_token']
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# -------------------------------- INTRO ------------------------------------
# C'est ici qu'est initialisé le bot, qu'on lui donne naissance
description = """LaForge - Assistant de forgemagie pour le MMORPG Dofus v2.5"""
laforge_bot = commands.Bot(command_prefix='$', description=description) # descripteur du bot

print('---------------') # armorçage du bot, côté serveur donc invisible sur discord
print(' *-= Arena =-* ')
print('---------------')
print('Starting Bot...')


@laforge_bot.event
async def on_ready():  # quand le bot est prêt...
    game = discord.Game("chauffer la forge")
    await laforge_bot.change_presence(status=discord.Status.idle, activity=game) # ...affiche le statut idle:"Joue à chauffer la forge"...
    print('*Bot is ready*')  # ... et affiche dans le terminal du serveur *Bot is ready*
# -------------------------------- -=*=- ------------------------------------

# -------------------------------- ROLES ------------------------------------
# TODO: Configurer un ID pour un message de bienvenue, qui via des réactions 
# attribuent des rôles de forgemagie (pour commencer 'forgemage', mais 
# pourquoi pas après joalliomage, cordomage... etc)

# @laforge_bot.event
# async def on_raw_reaction_add(payload):
#     message_id = payload.message_id
#     if message_id == 619522439545749514:
#         server = laforge_bot.get_guild(codeanon_id)  # on sélectionne le serveur CodeAnon
#         role = None

#         # on crée les associations emoji/role a l'aide de leur code point
#         # on peut l'obtenir en tapant dans discord :
#         #              \:poop:
#         if payload.emoji.name == '🇨':
#             role = discord.utils.get(server.roles, name='cybersec')
#         elif payload.emoji.name == '🇵':
#             role = discord.utils.get(server.roles, name='programmation')
#         elif payload.emoji.name == '🇷':
#             role = discord.utils.get(server.roles, name='réseau&web')
#         elif payload.emoji.name == '🇸':
#             role = discord.utils.get(server.roles, name='système')
#         elif payload.emoji.name == '🇮':
#             role = discord.utils.get(server.roles, name='ia&maths')

#         if role is not None:  # si le role choisi ne fait pas parti des 5 ci-dessus
#             member = discord.utils.find(lambda m: m.id == payload.user_id, server.members)
#             await member.add_roles(role)
#         print("done")


# @laforge_bot.event
# async def on_raw_reaction_remove(payload):
#     message_id = payload.message_id
#     if message_id == 619522439545749514:
#         server = laforge_bot.get_guild(codeanon_id)  # on sélectionne le serveur CodeAnon
#         role = None

#         # on crée les associations emoji/role a l'aide de leur code point
#         # on peut l'obtenir en tapant dans discord :
#         #              \:poop:
#         if payload.emoji.name == '🇨':
#             role = discord.utils.get(server.roles, name='cybersec')
#         elif payload.emoji.name == '🇵':
#             role = discord.utils.get(server.roles, name='programmation')
#         elif payload.emoji.name == '🇷':
#             role = discord.utils.get(server.roles, name='réseau&web')
#         elif payload.emoji.name == '🇸':
#             role = discord.utils.get(server.roles, name='système')
#         elif payload.emoji.name == '🇮':
#             role = discord.utils.get(server.roles, name='ia&maths')

#         if role is not None:  # si le role est choisi fait parti des 5 ci-dessus
#             member = discord.utils.find(lambda m: m.id == payload.user_id, server.members)
#             await member.remove_roles(role)
#         print("done")

# -------------------------------- -=*=- ------------------------------------

# ----------------------------- DEFINITIONS ---------------------------------
# Ici sont définies l'ensemble des fonctions nécessaires à l'exécution des 
# commandes construites plus bas

def decoupage(entree):
    """Découpe l'entrée et retourne une liste contenant les différents paramètres à prendre en compte lors du calcul"""
    termes = entree.split(", ")
    elements = []
    for elem in termes:
        elements.append(elem.split(" ", 1))
    return elements


def pesee(carac, tableau_rune):
    """Retourne le poid de base d'une rune dont la caractéristique est passée en entrée"""
    resultat = 0
    for rune in tableau_rune:
        if carac == rune.getCarac():
            resultat = rune.getPoids()
    return resultat

def poid_terme(terme, tableau_rune):
    """Retourne le poid effectif d'une perte ou d'un gain d'un terme suite à l'application d'une rune"""
    """Exemple : ["+10", "Sagesse"], poid effectif : 10*3=30"""
    if "%" in terme[0]:
        coefficient = float(terme[0].replace("%", ""))  # On retire le caractère % si présent
    else:
        coefficient = float(terme[0])
    poids = pesee(terme[1], tableau_rune)
    return int(coefficient * poids)


def calcul_reliquat(saisie, tableau_rune):
    """Retourne le reliquat généré par la forge"""
    resultat = 0
    decoupe = decoupage(saisie)
    for terme in decoupe[:-1]:
        resultat += -poid_terme(terme, tableau_rune)
    return resultat

# -------------------------------- -=*=- ------------------------------------

# ------------------------------ COMMANDES ----------------------------------
# Les commandes du bots, c'est cette partie qui sera éditée en cas d'ajout de
# nouvelles fonctionnalités
session = 0 # indique si une session est en cours ou non
pui = 0     # indique l'historique du pui ou reliquat
tableau = init_rune_tab()  # initialisation du tableau des runes (cf src/rune.py)


@laforge_bot.command()
async def ping(ctx):
    """Ping le bot, permet de savoir s'il est actif ou non"""
    await ctx.send(f"*Pong, vitesse de {round(laforge_bot.latency * 1000)}ms*")

@laforge_bot.command()
async def start(ctx):
	"""Démarre une session de forgemagie"""
	if session:
		await ctx.send("""*Une session est déjà en cours !
Fermez la précédente avec la commande `$stop`*""")
	else:
		pui = 0  # réinitialisation du reliquat
		await ctx.send("""*Session de forgemagie prête ☘️
L'historique du reliquat sera conservé.*""")

@laforge_bot.command()
async def pui(ctx, historique):
	"""Retourne le reliquat généré par la forge"""
	pui += calcul_reliquat(historique, tableau)
	await ctx.send("*Votre reliquat est désormais de " + pui + ".*")

@laforge_bot.command()
async def stop(ctx):
	"""Stoppe une session de forgemagie"""
	if not session:
		await ctx.send("""*Aucune session en cours.
Vous pouvez en démarrer une avec la commande `$start`*""")
	else:
		await ctx.send("""*Session de forgemagie terminée 🦾
A très vite !*""")

# @laforge_bot.command()
# async def bienvenue(ctx):
#     await ctx.send("""
#     Ce discord possède 5 thématiques principales qui sont :
#         - La Cybersécurité
#         - La Programmation
#         - Réseau & Web
#         - Système
#         - IA & Maths
#
# Pour vous abonner à une section, n'hésitez pas à réagir à ce message avec \
# la lettre correspondante !""")
# -------------------------------- MAIN ------------------------------------
laforge_bot.run(token)  # allume le bot