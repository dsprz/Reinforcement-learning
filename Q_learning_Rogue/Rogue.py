# Porcel Koralie G2
import random
import copy
import math
from tkinter import *
import numpy as np


#To deep copy a list 
import copy

#random.seed(4)

window = Tk()  # Fenêtre de l'interface graphique
window.title("Rogue")  # Titre
window.configure(bg="black")  # Font
window.geometry("1200x800")  # Taille


# Effects des potions:
def heal(creature, power):  # Permet de soigner
    if creature.hp + 3 * power > 9 + creature.niveau:
        creature.hp = 9 + creature.niveau
    else:
        creature.hp += 3 * power
    return True


def teleport(creature, unique):  # Permet de se téléporter
    a = random.choice(theGame().floor._rooms).randEmptyCoord(theGame().floor)
    b = theGame().floor.pos(creature)
    c = a - b
    theGame().floor.move(creature, c)
    return unique


def force(creature):  # Permet d'augmenter la force
    creature.strength += 1
    return True


class Element:
    "Tout les éléments du jeu dépendent de cette classe"

    def __init__(self, name, abbrv=None, reward=0):
        self.name = name
        if abbrv:
            self.abbrv = abbrv
        else:
            self.abbrv = self.name[0]
    
        self.reward = reward

    def __repr__(self):  # représentation
        return self.abbrv
    
    def __int__(self):
        return self.reward
    

    def description(self):
        return "<" + self.name + ">"

    def meet(self, hero):
        # Escalier qui permet de changer d'étage, pour simplifier le code et ne pas creer une autre classe, je l'ai mit ici
        #theGame().level += 1
        #print("STAIRS REACHED")
        #theGame().play()
        pass


class Equipment(Element):
    "Equipement"

    def __init__(self, name, abbrv="", usage=None):
        Element.__init__(self, name, abbrv)
        self.usage = usage  # usage permet de voir si l'équipement peut s'utiliser et comment.

    def meet(self, hero):
        if hero.take(self):
            theGame().addMessage("Vous prenez un(e) " + str(self.name) + '\n')
            return True
        return False

    def use(self, creature):  # si l'équipement peut s'utiliser, il retournera son usage
        if self.usage:
            theGame().addMessage("Le " + str(creature.name) + " utilise " + str(self.name) + "\n")
            return self.usage(self, creature)
        theGame().addMessage(str(self.name) + " n'est pas utilisable" + "\n")
        return False


class Armure(Equipment):
    def __init__(self, name, abbrv="", armure=0):
        Equipment.__init__(self, name, abbrv, usage=None)
        self.armure = armure

    def use(self, creature):
        creature.armure = 0  # réinitialise l'armure
        if len(creature.equiper) == 1:  # Si une armure est déja équiper, la renvoie dans l'inventaire de la creature et la suprime de son équipement
            creature._inventory.append(creature.equiper[0])
            creature.equiper = []
        theGame().addMessage("Le " + str(creature.name) + " équipe " + str(self.name) + "\n")
        creature.equiper.append(self)
        creature.armure = self.armure
        return True


class Arme(Equipment):
    def __init__(self, name, abbrv="", force=0):
        Equipment.__init__(self, name, abbrv, usage=None)
        self.force = force

    def use(self, creature):
        if len(creature.equiper2) == 1:  # Si une armure est déja équiper, la renvoie dans l'inventaire de la creature et la suprime de son équipement
            creature.strength -= creature.equiper2[0].force
            creature._inventory.append(creature.equiper2[0])
            creature.equiper2 = []
        theGame().addMessage("Le " + str(creature.name) + " équipe " + str(self.name) + "\n")
        creature.equiper2.append(self)
        creature.strength += self.force
        return True


class Creature(Element):
    "Hérite de Element est correspond à toutes les créatures du jeu: monstres et héro"

    def __init__(self, name, hp, abbrv=None, strength=1, giveXP=1, effect=None, armure=0):
        Element.__init__(self, name, abbrv)
        self.hp = hp
        self.strength = strength
        self.giveXP = giveXP
        self.effect = effect
        self.armure = armure

    def __repr__(self):
        return Element.__repr__(self)

    def description(self):
        return Element.description(self) + "(" + str(self.hp) + ")"

    def meet(self, creature):  # lors d'une rencontre, les créatures vont s'attaquer
        if creature.strength - self.armure > 0:
            self.hp -= creature.strength - self.armure
        theGame().addMessage(creature.name + " attaque " + self.description() + "\n")
        if creature.effect:  # Si la creature a un effet, donne cet effet lorsqu'il attaque
            self.giveEffect(creature)
        if self.hp > 0:  # Si la creature est encore en vie return False
            return False
        if isinstance(creature, Hero):  # Si la creature est le héro, il ressoit de l'xp
            creature.xp += self.giveXP
            if creature.xp >= int(creature.niveau * 1.5 + 4):
                creature.lvlUp()  # Si l'xp du héro est superieur à un seuil, il change de niveau
        return True

    def lvlUpMonsters(self):
        # Augmenter la puissance des créatures au fils des étages
        if theGame().level != 1:
            if theGame().level % 2 == 0:
                self.hp += 1
            else:
                self.strength += 1

    def giveEffect(self, creature):  # pendant 3 tours, la creature sera affecté par l'effet poison
        if len(theGame().hero.equiper) != 0 and str(theGame().hero.equiper[0]) == "l":
            theGame().addMessage("Votre armure d'alchimiste vous protège contre l'effet " + str(creature.effect))
        elif str(creature.effect) == "poison":
            theGame().addMessage(str(creature.name) + " a donné l'effet poison" + "\n")
            self.affecter = [3, 1]
        else:
            theGame().addMessage("Diantre " + str(creature.name) + " vous a transmit la peste!" + "\n")
            self.affecter = [4, 2]


class Hero(Creature):
    ACTIONS = {
            "left": 0, 
            "right": 1, 
            "up": 2, 
            "down": 3
    }
    def __init__(self, name="Hero", hp=10, abbrv="HERO", strength=2, niveau=1, xp=0, affecter=[0, 0], reset_on_cliff = False):
        Creature.__init__(self, name, hp, abbrv, strength, giveXP=0, effect=None, armure=0)
        self._inventory = []
        self.niveau = niveau
        self.xp = xp
        self.affecter = affecter  # de base, le héro n'est pas affecté par un effet
        self.equiper = []
        self.equiper2 = []

        self.learning_rate = 0.99
        self.reset_on_cliff = reset_on_cliff

    def set_learning_rate(self, learning_rate):
        self.learning_rate = learning_rate

    def lvlUp(self):  # permet de faire monter de niveau le héro et lui rendre tout ses points de vie
        self.hp = 10 + self.niveau
        self.strength += 1
        self.xp = self.xp - int(self.niveau * 1.5 + 4)
        self.niveau += 1

    def take(self, elem):  # Si c'est un équipement, l'ajoute dans l'inventaire du héro
        if not isinstance(elem, Equipment):
            raise TypeError('Not a Equimpent')
        if len(self._inventory) < 9:
            self._inventory.append(elem)
            return True
        theGame().addMessage("Inventaire plein")

    def description(self):
        return Creature.description(self) + str(self._inventory)

    def fullDescription(self):
        res = ""
        for x in self.__dict__:
            if x == "name" or x == "strength" or x == "armure":
                res += "> " + str(x) + " : " + str(self.__dict__[x]) + "\n"
            elif x == "affecter":
                if (self.__dict__[x])[0] != 0:
                    res += "> " + str(x) + " : oui" + "\n"
                else:
                    res += "> " + str(x) + " : non" + "\n"
        res += "> Niveau d'étage : " + str(theGame().level)
        return res

    def use(self, item):
        if not isinstance(item, Equipment):
            raise TypeError('Not a Equimpent')
        if item not in self._inventory:
            raise ValueError('Not in Inventory')
        a = item.use(self)
        if a == True:
            self._inventory.remove(item)

    def remove(self, item):
        if item not in self._inventory:
            raise ValueError('Not in Inventory')
        self._inventory.remove(item)

    def move_left(self, game) -> bool:
        """
            The hero moves to the left.
            The function returns True if the destination point is a wall (a cliff)
        """
        return game.floor.move(self, Coord(-1, 0))

    def move_right(self, game):
        return game.floor.move(self, Coord(1, 0))

    def move_up(self, game):
        return game.floor.move(self, Coord(0, 1))

    def move_down(self, game):
        return game.floor.move(self, Coord(0, -1))

    def reset(self, game):
        game.floor.put(game.floor.hero_starting_coordinates, self)
    



class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if self.x is other.x and self.y is other.y:
            return True
        return False

    def __add__(self, other):
        z = self.x + other.x
        w = self.y + other.y
        return Coord(z, w)

    def __repr__(self):
        return "<" + str(self.x) + "," + str(self.y) + ">"

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Coord(x, y)

    def distance(self, other):
        return math.sqrt(math.pow(self.x - other.x, 2) + math.pow(self.y - other.y, 2))

    def direction(self, other):
        cos = (self.x - other.x) / float(self.distance(other))
        if cos > 1 / math.sqrt(2):
            return Coord(-1, 0)
        elif cos < -1 / math.sqrt(2):
            return Coord(1, 0)
        elif self.y - other.y > 0:
            return Coord(0, -1)
        else:
            return Coord(0, 1)


class Map:

    #Ground gives 0 reward
    GROUND_REWARD = 0
    ground = GROUND_REWARD

    #Walls give a huge malus
    CLIFF_REWARD = -99
    empty = CLIFF_REWARD
    dir = {'z': Coord(0, -1), 's': Coord(0, 1), 'd': Coord(1, 0), 'q': Coord(-1, 0)}
    #STAIRS = Element("escalier", "E", reward=1000)
    STAIRS_REWARD = 1000
    STAIRS = STAIRS_REWARD
    def __init__(self, size=20, hero=None):
        self._mat = []
        self._elem = {}
        self._rooms = []
        self._roomsToReach = []

        for i in range(size):
            self._mat.append([Map.empty] * size)
        if hero is None:
            hero = Hero()
        self.hero = hero
        self.generateRooms(7)
        self.reachAllRooms()

        self.hero_starting_coordinates = Room.center(self._rooms[0])
        self.put(self.hero_starting_coordinates, self.hero)

        b = random.randint(1, len(self._rooms) - 1)
        self.stairs_coordinates = Room.center(self._rooms[b])

        #self.put(self.stairs_coordinates, self.STAIRS)
        self._mat[self.stairs_coordinates.y][self.stairs_coordinates.x] = self.STAIRS
        """for x in theGame().monsters:  # A chaque étage, le niveau des monstres augmente
            for y in theGame().monsters[x]:
                y.lvlUpMonsters()
        """
        """for r in self._rooms:
            r.decorate(self)"""

    def reset_hero(self):
        orig = self.pos(self.hero)
        self._mat[orig.y][orig.x] = Map.ground
        self.put(self.hero_starting_coordinates, self.hero)

    def __repr__(self):
        res = ""
        for x in self._mat:
            for y in x:
                res += str(y)
            res += '\n'
        return res
    
    
    def __len__(self):
        return len(self._mat[0])

    def __contains__(self, item):
        # if item in Map
        if isinstance(item, Coord):  # vérifie si item est une instance de la classe Coord
            if 0 <= item.x < len(self) and 0 <= item.y < len(self):
                return True
            return False
        if item in self._elem:
            return True
        return False

    def get(self, c):
        # retourne l'élément aux coordonnées c
        self.checkCoord(c)
        return self._mat[c.y][c.x]

    def get_mat(self):
        return self._mat

    def get_rewards_map(self):
        rewards_map = copy.deepcopy(self._mat)
        rewards_map[self.hero_starting_coordinates.y][self.hero_starting_coordinates.x] = 0
        rewards_map[self.stairs_coordinates.y][self.stairs_coordinates.x] = self.STAIRS
        return rewards_map
    
    def pos(self, e):
        # retourne les coordonnées de l'élément e
        self.checkElement(e)
        for y in range(len(self._mat)):
            for x in range(len(self._mat[y])):
                if self._mat[y][x] == e:
                    return Coord(x, y)

    def put(self, c, e):
        # place l'élément e aux coordonnées c
        self.checkCoord(c)
        self.checkElement(e)
        """if self._mat[c.y][c.x] != self.ground:
            raise ValueError('Incorrect cell')
        
        
        if e in self:
            raise KeyError('Already placed')
        """
        self._mat[c.y][c.x] = e
        self._elem[e] = c

    def rm(self, c):
        # supprime l'élément aux coordonnées c
        self.checkCoord(c)
        if self._mat[c.y][c.x] != self.ground:
            del self._elem[self._mat[c.y][c.x]]
            self._mat[c.y][c.x] = self.ground

    def move(self, e, way):
        """Moves the element e in the direction way."""
        orig = self.pos(e)
        dest = orig + way
        if dest in self:
            if self.get(dest) == Map.ground:
                self._mat[orig.y][orig.x] = Map.ground
                self._mat[dest.y][dest.x] = e
                self._elem[e] = dest
                #print(f"{dest} is Map.ground")
            
            elif self.get(dest) == Map.STAIRS:
                #Make the stairs a passable tile
                self._mat[orig.y][orig.x] = Map.ground
                self._mat[dest.y][dest.x] = e
                self._elem[e] = dest
                #print("STAIRS REACHED")

            elif self.get(dest) != Map.empty and self.get(dest).meet(e) and self.get(dest) != self.hero:
                self.rm(dest)
            
            #Allows the hero to mistakenly walk into a wall (cliff)
            #The cliff "kills" the hero and makes him reset at its starting location
            elif self.get(dest) == Map.empty:
                
                #print(f"dest {dest} is a cliff !")
                
                if self.hero.reset_on_cliff:
                    #Resets the hero at its starting position if reset_on_cliff is set to True
                    #Must remove the hero by setting the cell to map.ground, otherwise there would be 2 heroes
                    self._mat[orig.y][orig.x] = Map.ground
                    self.put(self.hero_starting_coordinates, self.hero)

            return self.get(dest) == Map.empty
        
        #Return True if we get out of map
        return True

    def addRoom(self, room):
        # ajoute une salle dans la liste _roomsToReach
        self._roomsToReach.append(room)
        for x in range(room.c1.x, (room.c2.x) + 1):
            for y in range(room.c1.y, (room.c2.y) + 1):
                self._mat[y][x] = self.ground
        return self._roomsToReach

    def findRoom(self, coord):
        # retourne la salle, parmi _roomsToReach, qui contient la coordonnée coord
        for x in self._roomsToReach:
            if coord in x:
                return x
        return False

    def intersectNone(self, room):
        # retourne True si aucune salle, parmi _roomsToReach, a une intersection avec room
        for x in self._roomsToReach:
            if Room.intersect(room, x):
                return False
        return True

    def dig(self, coord):
        # creuse à une coordoné
        self._mat[coord.y][coord.x] = self.ground
        x = self.findRoom(coord)
        if x != False:
            self._rooms.append(x)
            self._roomsToReach.remove(x)

    def corridor(self, start, end):
        # creuse d'une room à une autre
        self.dig(start)
        while start.y != end.y:
            self.dig(start)
            if start.y > end.y:
                start.y -= 1
            else:
                start.y += 1
            self.dig(start)
        while start.x != end.x:
            if start.x > end.x:
                start.x -= 1
            else:
                start.x += 1
            self.dig(start)

    def reach(self):
        # creuse d'une room aléatoire à une autre aléatoirement
        roomA = random.choice(self._rooms)
        roomB = random.choice(self._roomsToReach)

        self.corridor(roomA.center(), roomB.center())

    def reachAllRooms(self):
        # enlève la première salle des salles à atteindre et la met dans les salles atteintes
        a = self._roomsToReach[0]
        self._roomsToReach.remove(a)
        self._rooms.append(a)
        while len(self._roomsToReach) != 0:
            self.reach()

    def randRoom(self):
        x1 = random.randint(0, len(self) - 3)
        y1 = random.randint(0, len(self) - 3)
        largeur = random.randint(3, 8)
        hauteur = random.randint(3, 8)
        x2 = min((len(self) - 1), (x1 + largeur))
        y2 = min((len(self) - 1), (y1 + hauteur))
        return Room(Coord(x1, y1), Coord(x2, y2))

    def generateRooms(self, n):
        # pour enlever le pb de parfois, qu'une seule salle se créer et j'en ai besoin de 2, une pour le héro et une pour les escaliers
        while len(self._roomsToReach) < 2:
            for i in range(n):
                room = self.randRoom()
                if self.intersectNone(room):
                    self.addRoom(room)

    def checkCoord(self, c):
        if not isinstance(c, Coord):
            raise TypeError('Not a Coord')
        if c not in self:
            pass
            #raise IndexError('Out of map coord')

    def checkElement(self, e):
        if not isinstance(e, Element):
            raise TypeError('Not a Element')

    def moveAllMonsters(self):
        h = self.pos(self.hero)
        for e in self._elem:
            c = self.pos(e)
            if isinstance(e, Creature) and e != self.hero and c.distance(h) < 6:
                d = c.direction(h)
                if self.get(c + d) in [Map.ground, self.hero]:
                    self.move(e, d)


class Room():
    def __init__(self, c1, c2):
        self.c1 = c1
        self.c2 = c2

    def __repr__(self):
        return "[<" + str(self.c1.x) + "," + str(self.c1.y) + ">, <" + str(self.c2.x) + "," + str(self.c2.y) + ">]"

    def __contains__(self, item):
        if isinstance(item, Coord):
            if self.c1.x <= item.x <= self.c2.x and self.c1.y <= item.y <= self.c2.y:
                return True
            return False

    def center(self):
        x = (self.c1.x + self.c2.x) // 2
        y = (self.c1.y + self.c2.y) // 2
        return Coord(x, y)

    def intersect(self, other):
        """Test if the room has an intersection with another room"""
        sc3 = Coord(self.c2.x, self.c1.y)
        sc4 = Coord(self.c1.x, self.c2.y)
        return self.c1 in other or self.c2 in other or sc3 in other or sc4 in other or other.c1 in self

    def randCoord(self):
        x = random.randint(self.c1.x, self.c2.x)
        y = random.randint(self.c1.y, self.c2.y)
        return Coord(x, y)

    def randEmptyCoord(self, map):
        x = self.randCoord()
        while x == self.center() or map.get(x) != Map.ground:
            x = self.randCoord()
        return x

    def decorate(self, map):
        map.put(self.randEmptyCoord(map), theGame().randEquipment())
        map.put(self.randEmptyCoord(map), theGame().randMonster())



class Game():
    equipments = {
        0: [Equipment("potion de soin", "p", usage=lambda equip, user: heal(user, 1)),
            Armure("Armure de paysant", "P", armure=0),
            Arme("dague", "d", force=1)],
        1: [Equipment("potion de téléportation", "t", usage=lambda equip, user: teleport(user, True)),
            Equipment("potion de soin", "p", usage=lambda equip, user: heal(user, 1))],
        2: [Equipment("grande potion de soin", "g", usage=lambda equip, user: heal(user, 2)),
            Arme("épée", "s", force=2),
            Armure("Armure d'Alchimist", "l", armure=1)],
        3: [Armure("Armure de chevalier", armure=3), Arme("Epée en fer massif", "m", force=3)],
        6: [Equipment("portoloin", "w", usage=lambda equip, user: teleport(user, False)),
            Equipment("potion de force", "f", usage=lambda equip, user: force(user))],
        7: [Armure("Armure Légendaire de chevalier", "L", armure=5),
            Arme("excalibur", "x", force=5),
            Equipment("potion de soin légendaire", "r", usage=lambda equip, user: heal(user, 3))]}
    monsters = {
        0: [Creature("Le Goblin", 4, "G"),
            Creature("La chauve-souris", 2, "W"),
            Creature("Le squelette", 3, "T")],
        1: [Creature("L'orque", 6, "O", strength=2, giveXP=2),
            Creature("Le blob", 10, "B", giveXP=2),
            Creature("L'elf noir", 4, "N", strength=3, giveXP=2)],
        2: [Creature("L'araignée", 2, "S", giveXP=2, effect="poison"),
            Creature("Le chevalier elf noir", 10, "C", strength=4, giveXP=3)],
        3: [Creature("Le rat", 1, "R", strength=0, giveXP=1, effect="peste")],
        4: [Creature("Le serpent", 5, "K", strength=3, giveXP=3, effect="poison")],
        5: [Creature("Le sphinx", 18, "X", strength=3, giveXP=4),
            Creature("Le golem", 35, "M", giveXP=4)],
        6: [Creature("Le dragon", 20, "D", strength=3, giveXP=5),
            Creature("Le troll", 35, "I", strength=2, giveXP=5)],
        7: [Creature("Le daeva", 25, "V", strength=5, giveXP=6),
            Creature("Le dragon", 20, "D", strength=3, giveXP=5)]}
    _actions = {
        'z': lambda hero: theGame().floor.move(hero, Coord(0, -1)),
        's': lambda hero: theGame().floor.move(hero, Coord(0, 1)),
        'q': lambda hero: theGame().floor.move(hero, Coord(-1, 0)),
        'd': lambda hero: theGame().floor.move(hero, Coord(1, 0)),
        'i': lambda hero: theGame().addMessage(hero.fullDescription()),
        'k': lambda hero: hero.__setattr__("hp", 0),
        'space': lambda hero: None,
        'u': lambda hero: hero.use(theGame().select(hero._inventory)),
        'ampersand': lambda hero: hero.use(theGame().hero._inventory[0]),
        'eacute': lambda hero: hero.use(theGame().hero._inventory[1]),
        'quotedbl': lambda hero: hero.use(theGame().hero._inventory[2]),
        'quoteright': lambda hero: hero.use(theGame().hero._inventory[3]),
        'parenleft': lambda hero: hero.use(theGame().hero._inventory[4]),
        'minus': lambda hero: hero.use(theGame().hero._inventory[5]),
        'egrave': lambda hero: hero.use(theGame().hero._inventory[6]),
        'underscore': lambda hero: hero.use(theGame().hero._inventory[7]),
        'ccedilla': lambda hero: hero.use(theGame().hero._inventory[8]),
        '1': lambda hero: hero.remove(theGame().hero._inventory[0]),
        '2': lambda hero: hero.remove(theGame().hero._inventory[1]),
        '3': lambda hero: hero.remove(theGame().hero._inventory[2]),
        '4': lambda hero: hero.remove(theGame().hero._inventory[3]),
        '5': lambda hero: hero.remove(theGame().hero._inventory[4]),
        '6': lambda hero: hero.remove(theGame().hero._inventory[5]),
        '7': lambda hero: hero.remove(theGame().hero._inventory[6]),
        '8': lambda hero: hero.remove(theGame().hero._inventory[7])}

    def __init__(self, hero=None, level=1):
        if hero == None:
            hero = Hero()
        self.hero = hero
        self.level = level
        self.floor = None
        self._message = []
        self.buildFloor()

    def buildFloor(self):
        self.floor = Map(hero=self.hero)

    def get_map(self):
        return self.floor
    
    def addMessage(self, msg):
        self._message.append(msg)

    def readMessages(self):
        if len(self._message) == 0:
            return ""
        res = ""
        for x in range(len(self._message)):
            res += self._message[x]
        self._message.clear()
        return res

    def randElement(self, collection):
        x = int(random.expovariate(1 / self.level))
        while x not in collection:
            x = x - 1
        return copy.copy(random.choice(collection[x]))

    def randEquipment(self):
        return self.randElement(self.equipments)

    def randMonster(self):
        return self.randElement(self.monsters)

    def get_hero(self):
        return self.hero
    
    def select(self, l):
        if len(l) == 0:
            return None
        liste = []
        for x in range(len(l)):
            liste.append(str(str(x) + ": " + l[x].name))

    def get_hero_coords(self):
        return self.floor.pos(self.hero)

    def play(self):  # La fonction Play a été changé pour l'interface graphique qui n'est pas encore finit
        """Main game loop"""
        pass
        #self.buildFloor()
        interfaceGraphique()



class interfaceGraphique():  # interface graphique en cours de creation, pour l'intant seul le menu principal jeu est fonctionel, on peut bougé grace aux claver, mais pas utiliser l'inventaire et autre
    "En cours de création"
    # Toutes les textures
    texture = {"coeur": PhotoImage(file="Images/coeur.png"),
               "coeurVide": PhotoImage(file="Images/coeur vide.png"),
               "gameOver": PhotoImage(file="Images/game over v1.png"),
               "sol": PhotoImage(file="Images/rect_gray0.png"),
               "HERO": PhotoImage(file="Images/donald.png"),
               "mur": PhotoImage(file="Images/stone_brick3.png"),
               "E": PhotoImage(file="Images/stone_stairs_up.png"),
               "p": PhotoImage(file="Images/ruby.png"),
               "g": PhotoImage(file="Images/grande potion de soin.png"),
               "r": PhotoImage(file="Images/potion légendaire de soin.png"),
               "t": PhotoImage(file="Images/cyan.png"),
               "f": PhotoImage(file="Images/orange.png"),
               "W": PhotoImage(file="Images/giant_bat.png"),
               "G": PhotoImage(file="Images/gobelin v2.png"),
               "O": PhotoImage(file="Images/blork_the_orc.png"),
               "B": PhotoImage(file="Images/blob.png"),
               "D": PhotoImage(file="Images/iron_dragon.png"),
               "w": PhotoImage(file="Images/portoloin.png"),
               "s": PhotoImage(file="Images/two_handed_sword.png"),
               "S": PhotoImage(file="Images/spider_form.png"),
               "R": PhotoImage(file="Images/Rat.png"),
               "T": PhotoImage(file="Images/skeleton_humanoid_small.png"),
               "N": PhotoImage(file="Images/deep_elf_fighter.png"),
               "C": PhotoImage(file="Images/deep_elf_knight.png"),
               "V": PhotoImage(file="Images/daeva.png"),
               "M": PhotoImage(file="Images/stone_golem.png"),
               "X": PhotoImage(file="Images/sphinx.png"),
               "I": PhotoImage(file="Images/iron_troll.png"),
               "K": PhotoImage(file="Images/water_moccasin.png"),
               "d": PhotoImage(file="Images/dagger.png"),
               "x": PhotoImage(file="Images/escalibur.png"),
               "m": PhotoImage(file="Images/spwpn_sword_of_zonguldrok.png"),
               "A": PhotoImage(file="Images/armure_chevalier.png"),
               "P": PhotoImage(file="Images/armure_paysan.png"),
               "L": PhotoImage(file="Images/Armure_legendaire.png"),
               "l": PhotoImage(file="Images/Armure_Alchimist.png"),
               "parchemin": PhotoImage(file="Images/parchemin.png"),
               "intentaire": PhotoImage(file="Images/equipement.png"),
               "croix": PhotoImage(file="Images/croix pour quitter.png"),
               "tutoriel": PhotoImage(file="Images/tutoriel.png"),
               "victoire": PhotoImage(file="Images/victory.png")}
    textureHero = {"hero": PhotoImage(file="Images/donald.png"),
                   "paysan": PhotoImage(file="Images/Paysan.png"),
                   "alchimist": PhotoImage(file="Images/alchimist.png"),
                   "chevalier": PhotoImage(file="Images/Chevalier.png"),
                   "legendaire": PhotoImage(file="Images/Chevalier legendaire.png"), }

    def __init__(self):
        self.finish = False
        self.action = False
        self.liste = theGame().floor._mat
        window.bind("<Key>", self.key_pressed)
        self.taille = 32 * 20
        self.interface()
        window.mainloop()  # affiche la fenetre

    def interface(self):
        canvasReset = Canvas(window, width=1800, height=1020, bg="black", highlightbackground="Black")
        canvasReset.place(x=0, y=0)
        self.interfaceJeu()
        self.interfaceInventaire()
        self.interfaceChat()

    def interfaceJeu(self):
        canvasJeu = Canvas(window, width=self.taille, height=self.taille)
        canvasJeu.place(x=0, y=0)
        ligne = 0
        for x in range(len(self.liste)):
            colone = 0
            for y in self.liste[x]:
                if y == Map.empty:
                    canvasJeu.create_image(colone * 32 + 18, ligne * 32 + 18, image=self.texture["mur"])
                else:
                    canvasJeu.create_image(colone * 32 + 18, ligne * 32 + 18, image=self.texture["sol"])
                    if str(y) == "HERO":
                        if theGame().hero.equiper == []:
                            canvasJeu.create_image(colone * 32 + 18, ligne * 32 + 18, image=self.textureHero["hero"])
                            self.avatar = "hero"
                        elif str(theGame().hero.equiper[0]) == "L":
                            canvasJeu.create_image(colone * 32 + 18, ligne * 32 + 18,
                                                   image=self.textureHero["legendaire"])
                            self.avatar = "legendaire"
                        elif str(theGame().hero.equiper[0]) == "l":
                            canvasJeu.create_image(colone * 32 + 18, ligne * 32 + 18,
                                                   image=self.textureHero["alchimist"])
                            self.avatar = "alchimist"
                        elif str(theGame().hero.equiper[0]) == "P":
                            canvasJeu.create_image(colone * 32 + 18, ligne * 32 + 18, image=self.textureHero["paysan"])
                            self.avatar = "paysan"
                        elif str(theGame().hero.equiper[0]) == "A":
                            canvasJeu.create_image(colone * 32 + 18, ligne * 32 + 18,
                                                   image=self.textureHero["chevalier"])
                            self.avatar = "chevalier"

                    elif y != Map.ground:
                        canvasJeu.create_image(colone * 32 + 18, ligne * 32 + 18, image=self.texture["E"])
                colone += 1
            ligne += 1

    def interfaceInventaire(self):
        canvasInventaire = Canvas(window, width=1000, height=1000, bg="Black", highlightbackground="Black")
        canvasInventaire.place(x=self.taille + 3, y=0)
        canvasInventaire.create_image(500, 500, image=self.texture["intentaire"])  # l'inventaire
        canvasInventaire.create_image(155, 160, image=self.textureHero[self.avatar])  # avatar du hero

        # armure équipée
        if len(theGame().hero.equiper) == 1:
            canvasInventaire.create_image(130, 250, image=self.texture[str(theGame().hero.equiper[0])])
        # Arme équipée
        if len(theGame().hero.equiper2) == 1:
            canvasInventaire.create_image(185, 250, image=self.texture[str(theGame().hero.equiper2[0])])

        # object dans l'inventaire
        i = 0
        k = 0
        for x in theGame().hero._inventory:
            if x != "0":
                canvasInventaire.create_image(58 * i + 288, 140 + 55 * k, image=self.texture[str(x)])
            i += 1
            if i == 3:
                k += 1
                i = 0

        # descritpions du héro
        canvasInventaire.create_text(5, 740, text=theGame().hero.fullDescription(), anchor="w", fill="Black",
                                     font=("CASTElLAR", 10, 'bold'))

        # les coeurs
        for x in range(theGame().hero.niveau + 9):
            if x >= 15:  # s'il y a plus de 15 coeur, il y a une seconde ligne de coeur
                i = 0
                if x <= theGame().hero.hp - 1:
                    canvasInventaire.create_image(i * 32 + 70, 480, image=self.texture["coeur"])
                else:
                    canvasInventaire.create_image(i * 32 + 70, 480, image=self.texture["coeurVide"])
                i += 1
            else:
                if x <= theGame().hero.hp - 1:
                    canvasInventaire.create_image(x * 32 + 70, 440, image=self.texture["coeur"])
                else:
                    canvasInventaire.create_image(x * 32 + 70, 440, image=self.texture["coeurVide"])

        # l'experience
        propor = (theGame().hero.xp) / (theGame().hero.niveau * 1.5 + 4)
        if propor != 0:
            canvasXP = Canvas(window, width=210 * propor, height=11, bg="Green", highlightbackground="Black")
            canvasXP.place(x=self.taille + 138, y=375)
        canvasInventaire.create_text(354, 371, text="lvl " + str(theGame().hero.niveau), anchor="nw", fill="Black",
                                     font="Verdana")

        # Tutoriel : quand tu click sur le bouton, le tuto apparaît
        def openTuto():  # ouvrir le tutoriel
            self.tutoriel()
        button = Button(window, text="Ouvrir le tutoriel", command=openTuto, bd=0)
        button.place(x=878, y=500)

    def tutoriel(self):
        # il y a une croix pour quitter
        def quitter():
            canvasTutoriel.destroy()
        canvasTutoriel = Canvas(window, width=1020, height=1020, bg="Red", highlightbackground="Red")
        canvasTutoriel.place(x=50, y=0)
        button = Button(canvasTutoriel, image=self.texture["croix"], command=quitter)
        button.place(x=960, y=0)
        canvasTutoriel.create_image(510, 510, image=self.texture["tutoriel"])

    def interfaceVictory(self):
        canvasVictory = Canvas(window, width=1200, height=1080, bg="Black", highlightbackground="Black")
        canvasVictory.pack()
        canvasVictory.create_image(600, 400, image=self.texture["victoire"])
        self.finish = True

    def interfaceChat(self): # l'interface des messages
        canvasChat = Canvas(window, width=32 * 20, height=32 * 19, bg="Red", highlightbackground="Black")
        canvasChat.place(x=0, y=self.taille)
        canvasChat.create_image(0, 0, image=self.texture["parchemin"])
        canvasChat.create_text(2, 5, text=theGame().readMessages(), anchor="nw", fill="Black",
                               font=("French Script MT", 20, 'bold'))

    def interfaceGameOver(self):
        canvasOver = Canvas(window, width=1200, height=1080, bg='black')
        canvasOver.place(x=0, y=0)
        canvasOver.create_image(600, 400, image=self.texture["gameOver"])
        self.finish = True

    def key_pressed(self, event):
        if event.keysym in theGame()._actions and self.finish != True:
            theGame()._actions[event.keysym](theGame().hero)
            if theGame().hero.affecter[0] != 0:
                theGame().hero.hp -= int(theGame().hero.affecter[1])
                theGame().hero.affecter[0] -= 1
            if theGame().hero.hp > 0 and theGame().floor != 10:
                theGame().floor.moveAllMonsters()
                self.interface()
                self.interfaceInventaire()
            if theGame().hero.hp <= 0:
                self.interfaceGameOver()
            if theGame().level == 10:
                self.interfaceVictory()

def theGame(game=Game()):
    return game


if __name__ == "__main__":
    theGame().play()

"""
reward_array = np.array(theGame().get_map().get_mat())
nb_actions = len(Hero.ACTIONS)
x_length = len(reward_array)
y_length = len(reward_array[0])

nb_states = x_length*y_length
q_table = np.zeros((nb_states, nb_actions))

print(reward_array)
#np.set_printoptions(threshold=np.inf)
print(q_table)
"""
