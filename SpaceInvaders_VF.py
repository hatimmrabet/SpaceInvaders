#!/usr/bin/env python
# coding: utf-8

# In[3]:


#-------------------------------------------------#
#                                                 #
#   @author     : M'RABET EL KHOMSSI Hatim        #
#   Nom fichier : SpaceInvaders_VF                #
#   MÀJ         : 14/05/2020                      #   
#                                                 #
#-------------------------------------------------#


#les import
import tkinter as tk
from tkinter import *
import json
import random as rd
import time


class SpaceInvaders(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Space Invaders")
        self.root.resizable(0, 0)
        self.frame = tk.Frame(self.root)
        self.frame.pack(side="top", fill="both")
        self.game = Game(self.frame)
            
    def play(self):
        #fonction pour lancer le jeu apres que le joueur entre son nom
        def lancer(event):
            self.input_name.config(state='disabled') #desactiver le champs de saisie
            self.game.score.set_name(self.input_name.get()) #ajouter le nom de joueur au class Score()
            self.root.bind("<Key>", self.game.keypress) #deplacement et tire du defender
            self.game.start_animation() #debut d'annimation
                
        Lname = Label(self.frame, text="Merci d'enter votre Nom : ").pack(side = TOP) #message
        self.input_name = Entry(self.frame,bd =5)
        self.input_name.pack()
        self.input_name.focus_set()
        self.input_name.bind('<Return>',lancer) #si on clique sur entrer on appelle la fonction lancer   
        self.root.mainloop()
                        
#-------------------Game-------------------------
class Game(object):
    def __init__(self, frame):
        self.frame = frame
        self.fleet = Fleet()
        self.defender = Defender()
        self.bunckers= LesBunckers()        
        self.score = Score()
    #le canvas
        self.canvas_height = self.fleet.get_height() #initialisé dans la classe Fleet
        self.canvas_width = self.fleet.get_width()
        self.canvas = tk.Canvas(self.frame,width=self.canvas_width,height=self.canvas_height,bg='black')
        self.canvas.pack(padx=5,pady=5,side ="bottom")
    #les install_in
        self.defender.install_in(self.canvas)
        self.defender.display_defender_lifes(self.canvas)
        self.fleet.install_in(self.canvas)
        self.bunckers.install_in(self.canvas)
        
    def get_canvas_height(self):
        return self.canvas_height
    def get_canvas_width(self):
        return self.canvas_width
    
    #la gestion des touches
    def keypress(self, event):
        xcond = self.defender.xi  #pour ne pas depasser le cadre du jeu
        if event.keysym == 'Left':
            if xcond - self.defender.move_delta > 0:    #pour que le carre ne sort pas du cadre
                self.defender.xi = self.defender.xi - self.defender.move_delta    #changement de la valeur du x
                self.defender.move_in(self.canvas,-self.defender.move_delta)                
        elif event.keysym == 'Right':
            if xcond + self.defender.move_delta < self.defender.canvas_width:   #pour que le carre ne sort pas du cadre
                self.defender.xi = self.defender.xi + self.defender.move_delta    #changement de la valeur du x
                self.defender.move_in(self.canvas,self.defender.move_delta)
        elif event.keysym == 'space':    #la possibilité de tirer
            if len(self.fleet.aliens_fleet) != 0 and self.defender.lifes > 0: #le jeu n'est pas fini
                self.defender.fire(self.canvas)
                
    #fonction pour afficher le nom de joueur et un message de bienvenue
    def welcome(self):
        welcome_text = "Bienvenue : ' "+str(self.score.name) +" ' "        
        welcome_label = Label(self.canvas, text=welcome_text, bg="black", fg="white", font="Arial 13")
        self.canvas.create_window(110,25, window=welcome_label)
    
    #affichaege de score
    def affiche_score(self):
        self.score_actuel = StringVar()  #score actuel
        score_label = Label(self.canvas, textvariable = self.score_actuel, bg="black", fg="white", font="Arial 13")
        self.score_actuel.set("score : " + str(self.score.get_points())) #initialisation du score
        self.canvas.create_window(1050, 25, window = score_label)
    
    #l'enregistrement du score à la fin du jeu
    def saveFile(self):
        self.score.delai = int(time.time()) - self.score.start_time #le delai est la durée de jeu
        self.score.toFile("LastScore.json") #enregistrement du dernier score
        lastScore = self.score.fromFile("LastScore.json") #recuperation du dernir score
        self.resultats = Resultats.fromFile("AllResults.json")
        self.resultats.ajout(lastScore) #l'ajout du dernier score au resultat
        self.resultats.toFile("AllResults.json") #enregistrement de tous les resultats
    
    #si le joueur perd
    def player_lost(self):
        self.score.winning = False #on enregistre que le joueur a perdu
        self.saveFile() 
        w,h = int(self.canvas.cget("width"))//2 , int(self.canvas.cget("height"))//2
        self.canvas.delete("all") #on supprime tout
        self.canvas.create_text(w,h,text="Game Over, LoooSER", fill="white", font="Times 20 bold")
    
    #si le joueur a gagné
    def player_won(self):
        self.score.winning = True #on enregistre que le joueur a gagné
        self.saveFile()
        w,h = int(self.canvas.cget("width"))//2 , int(self.canvas.cget("height"))//2
        self.canvas.delete("all")
        self.canvas.create_text(w,h,text="You WON", fill="white", font="Times 20 bold")

    #debut d'animation
    def start_animation(self):
        self.welcome() #affichage du nom du joueur
        self.affiche_score() #affichage du score
        self.fleet.previous_shoot_time = float(time.time()) #l'ecart entre chaque tire alien doit etre 1s
        self.animation() #appelle de l'animation
    
    def animation(self):
        self.score_actuel.set("score : "+str(self.score.get_points())) #actualisation du score
        if len(self.fleet.aliens_fleet)!= 0: #il y a encore des aliens
            x1,y1,x2,y2 = self.canvas.bbox("alien")
            #fleet en dessus du defender et defender encore en vie
            if y2<=int(self.canvas.cget("height"))-self.defender.height and self.defender.lifes > 0:
                self.defender.move_bullet(self.canvas) 
                self.defender.manage_defender_touched_by(self.canvas,self.fleet)
                self.defender.collision_between_bullets(self.canvas, self.fleet)
                self.fleet.move_aliens_bullets(self.canvas)
                self.fleet.move_in(self.canvas)
                self.fleet.manage_touched_aliens_by(self.canvas,self.defender,self.score)
                self.fleet.install_aliens_bullets(self.canvas)
                self.fleet.animation_aliens_img(self.canvas)
                self.bunckers.manage_bunckers_statut(self.canvas,self.fleet)
                self.bunckers.buncker_touched_by_alien(self.canvas,self.fleet)
                self.canvas.after(50,self.animation) #appelle a la fonction apres 50ms
            else: #cas de perte
                self.player_lost()
        else: #liste vide -- gagner
            self.player_won()
            
            
#-------------------Fleet-------------------------
class Fleet(object):
    def __init__(self):
        #info sur la taille du canvas
        self.width = 1220 #largeur 
        self.height = 600 #hauteur 
        #la taille du fleet
        self.aliens_lines = 5
        self.aliens_columns = 6
        self.aliens_inner_gap = 10
        fleet_size = self.aliens_lines * self.aliens_columns
        self.aliens_fleet = [None] * fleet_size
        #deplacement
        self.alien_x_delta = 5
        self.alien_y_delta = 15
        #animation et changement d'images
        self.animation_start_time = float(time.time())
        #les balles des aliens
        self.temps_ecart = 1     #1 second, temps entre chaque tir d'alien
        self.previous_shoot_time = None    #cela sera initialisé à la classe Game()
        self.max_fired_bullets = 5  #nb de tires max
        self.aliens_fired_bullets = []
    
    #les accesseurs utilisés
    def get_width(self):
        return self.width
    def get_height(self):
        return self.height
    
    #installation du fleet
    def install_in(self, canvas):
        x, y = 50 , 75   #coord du position initial
        pos = 0 #l'indice dans la liste
        for i in range(0,self.aliens_lines):
            for j in range(0,self.aliens_columns):
                alien = Alien()
                self.aliens_fleet[pos] = alien.install_in(canvas,x,y) #return self
                pos += 1
                x += self.aliens_inner_gap + alien.alien_width
            x = 50
            y += self.aliens_inner_gap + alien.alien_height
            
    #deplacement du fleet
    def move_in(self, canvas): 
        if len(self.aliens_fleet) != 0:
            x1,y1,x2,y2 = canvas.bbox("alien")
            if x2 >= int(canvas.cget("width")): #coté droit
                self.alien_x_delta = -self.alien_x_delta
                dy = self.alien_y_delta
            elif x1 <= 0: #coté gauche
                self.alien_x_delta = -self.alien_x_delta
                dy = self.alien_y_delta
            else:
                dy = 0
            for i in range(0,len(self.aliens_fleet)):
                self.aliens_fleet[i].move_in(canvas,self.alien_x_delta,dy)
    
    #cas de collision entre alien et balles de defender
    def manage_touched_aliens_by(self,canvas,defender,score):
        sortir1 = False #condition d'arreter la 1er boucle "boucle de fleet"
        sortir2 = False #condition d'arreter la 2eme boucle "boucle de bullets"
        for i in range(len(self.aliens_fleet)): 
            x1,y1,x2,y2 = canvas.bbox(self.aliens_fleet[i].id) #coord de chaque alien
            overlapped = canvas.find_overlapping(x1, y1, x2, y2)
            if len(overlapped) > 1 : #il y a plus d'un seul element
                for j in range(len(defender.fired_bullets)):
                    for k in range(len(overlapped)):
                        if defender.fired_bullets[j].id == overlapped[k]: #l'indice j contient le self du l'alien voulu
                            self.effet_boom(canvas,defender.fired_bullets[j]) #effet de collision
                            self.aliens_fleet[i].touched_by(canvas,defender.fired_bullets[j]) #suppression du canvas
                            score.refresh_score(time.time()) #augumentation du score
                            del defender.fired_bullets[j]   #delete de valeur du liste
                            del self.aliens_fleet[i]
                            sortir1 = True
                            sortir2 = True
                            break; #sortir de la boucle overlapped
                    if sortir2 == True: #sortir de la boucle de fired_bullets
                        break;
                if sortir1 == True: #sortir de la boucle aliens_fleet
                    break;
    
    #le choix des aliens qui vont tirer
    def install_aliens_bullets(self, canvas):
        if len(self.aliens_fleet) != 0:   #s'il y a encore des aliens vivants
            if len(self.aliens_fired_bullets) < self.max_fired_bullets: #le respect du nombre max de tire
                choix = rd.randint(0,len(self.aliens_fleet)-1) #choix random d'alien qui va tirer
                x,y = canvas.coords(self.aliens_fleet[choix].id) #less coords de la bullet
                self.aliens_fire(canvas,x,y) #la fonction pour tirer
    
    #Tirer des balles par des aliens
    def aliens_fire(self, canvas, x, y):
        if float(time.time()) - self.previous_shoot_time >= self.temps_ecart: #respecter le temps entre chaque tire
            bullet = Bullet("alien")
            bullet = bullet.install_aliens_bullets(canvas,x,y) #return self
            self.aliens_fired_bullets.append(bullet) #l'ajout a la liste des blles tirées
            self.previous_shoot_time = float(time.time()) #modification de la valeur 
    
    #deplacer verticalement les balles des aliens 
    def move_aliens_bullets(self, canvas):
        for i in range(0,len(self.aliens_fired_bullets)):
            x1,y1,x2,y2 = canvas.bbox(self.aliens_fired_bullets[i].id) #les coords de chaque balle
            if y1>int(canvas.cget("height")): #si le bullet dehors du cadre du jeu
                canvas.delete(self.aliens_fired_bullets[i].id)  #suprression du dessin du bullet
                del self.aliens_fired_bullets[i]   #delete de sa valeur du liste
                break;
            else:
                self.aliens_fired_bullets[i].move_in(canvas) #deplacement du bullet
    
    #annimation des aliens
    def animation_aliens_img(self, canvas):
        temps = float(time.time()) #le temps actuel
        if temps - self.animation_start_time > 1: #1s d'ecart entre chaque changement d'image
            self.animation_start_time = temps #changement du l'instant de la derniere tire
            for i in range(len(self.aliens_fleet)):
                self.aliens_fleet[i].refresh_img(canvas) #changement de l'image de chaque alien
    
    #si l'alien est touché par une balle
    def effet_boom(self,canvas,projectile):
        self.boom = PhotoImage(file="explosion.gif")
        x1,y1,x2,y2 = canvas.bbox(projectile.id) #recuperation du coord du projectile
        x,y = x1+(x2-x1)/2, y1+(y2-y1)/2
        boom = canvas.create_image(x, y, image=self.boom, tags="boom")
        canvas.after(45,canvas.delete,boom) #suppression de l'effet de Boom
        
#------------- Alien ---------------#
class Alien(object):
    def __init__(self):
        self.id = None
        self.alive = True
        self.alien = PhotoImage(file="alien.gif") #image d'alien
        self.boom = PhotoImage(file="bunker.gif")
        self.alien_width = self.alien.width()
        self.alien_height = self.alien.height()
        
    def get_width(self):
        return self.alien_width
    def get_height(self):
        return self.alien_height
    
    #affichage de l'alien
    def install_in(self, canvas, x, y): 
        #w,h = self.alien_width , self.alien_height #pour le create_rectangle
        #self.id = canvas.create_rectangle(x, y,x+w, y+h, fill="white", tags="alien") #pour le dessin
        self.id = canvas.create_image(x, y, image=self.alien, tags="alien")
        #canvas.tag_lower(self.id)
        return self
    
    #movement de l'alien
    def move_in(self, canvas, dx, dy):
        canvas.move(self.id, dx, dy)
    
    #si l'alien est touché par une balle
    def touched_by(self,canvas,projectile):
        canvas.delete(projectile.id)  #suprression du bullet
        canvas.delete(self.id)    #supression de l'alien
        self.alive = False  #l'alien est mort
        
    #changement d'image pour l'animation
    def refresh_img(self, canvas):
        if (self.alien.cget("file") == "alien.gif"): #si c'est la 1ere image
            self.alien = PhotoImage(file="alien1.gif") #on modifie la variable de l'image
            canvas.itemconfigure(self.id, image=self.alien) #on change l'image
        else:
            self.alien = PhotoImage(file="alien.gif") #on modifie la variable de l'image
            canvas.itemconfigure(self.id, image=self.alien) #on change l'image
            
            
#------------- Defender ---------------#
class Defender(object):
    def __init__(self):
        #les images utilisés
        self.defender_img = PhotoImage(file="defender.gif")
        self.life_img = PhotoImage(file="life.gif")
        self.boom = PhotoImage(file="boom.png")
        self.width = self.defender_img.width()
        self.height = self.defender_img.height()
        #la taille du canvas
        self.canvas_height = Fleet().get_height()
        self.canvas_width = Fleet().get_width()
        #initialisation des varibales
        self.id = None
        self.lifes = 3
        self.xi = self.canvas_width//2 - self.width
        self.yi = self.canvas_height - self.height
        self.move_delta = self.width/2 #deplacement horizontale
        #tire des balles
        self.max_fired_bullets = 8
        self.fired_bullets = []
    
    #les accesseurs
    def get_height(self):
        return self.height
    def get_width(self):
        return self.width
    
    #l'affichage de l'image du defender
    def install_in(self, canvas):
        #w , h = self.width, self.height  #pour le create_rectangle
        #x1,y1,x2,y2 = self.xi-w/2 , self.yi-h/2 , self.xi+w/2 , self.yi+h/2 
        #self.id = canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="white")
        self.id = canvas.create_image(self.xi ,self.yi, image = self.defender_img , tags="defender")
    
    #affichage des vies de defender
    def display_defender_lifes(self, canvas):
        width = self.life_img.width() #width de l'image 
        height = self.life_img.height()
        inner_gap = width/2
        #initialisation des variables
        x = int(canvas.cget("width"))/2 - (width)*3/2 - inner_gap
        y = height * 3/4
        for i in range(self.lifes): #i < 3
            #life = canvas.create_rectangle(x,y,x+10,y+10,tags="lifes", fill="white" )
            life = canvas.create_image(x, y, image = self.life_img ,tags="lifes")
            x += width + inner_gap
            
    #deplacement horizontal du defender
    def move_in(self , canvas , dx):   
        canvas.move(self.id, dx, 0)
    
    #fonction de tire du defender
    def fire(self, canvas):
        if len(self.fired_bullets) < self.max_fired_bullets: #respect de nbr de bullets autorisé
            bullet = Bullet("defender")
            bullet = bullet.install_in(canvas)    #ajout des bullets a l'ecran
            self.fired_bullets.append(bullet)    #l'ajout des bullets tirers à la liste fired_bullets
    
    #deplacement verticale des balles
    def move_bullet(self,canvas):
        for i in range(0,len(self.fired_bullets)):
            x1,y1,x2,y2 = canvas.bbox(self.fired_bullets[i].id) #coord de chque balle
            if y1<0: #si le bullet dehors du cadre du jeu
                canvas.delete(self.fired_bullets[i].id) #suprression du dessin du bullet
                del self.fired_bullets[i] #delete de sa valeur du liste
                break
            else:
                self.fired_bullets[i].move_in(canvas)   #deplacement du bullet
    
    #si le defender est touché par une balle
    def manage_defender_touched_by(self, canvas, fleet):
        x1, y1, x2, y2 = canvas.bbox(self.id) #coords du defender
        overlapped = canvas.find_overlapping(x1, y1, x2, y2)
        if len(overlapped)>1: #s'il ya plus d'element au meme endroit
            sortir = False
            for i in range(len(overlapped)):
                for j in range(len(fleet.aliens_fired_bullets)):
                    if overlapped[i] == fleet.aliens_fired_bullets[j].id: #si c'est une balle d'alien
                        self.lifes -= 1 #perdre une vie
                        self.touched_by(canvas) #effect que le defender est touché
                        canvas.delete(fleet.aliens_fired_bullets[j].id) #supression de la balle
                        del fleet.aliens_fired_bullets[j]  #suppression de la balle de sa liste
                        all_lifes = canvas.find_withtag("lifes") #recuperation des images avec tag='lifes'
                        canvas.delete(all_lifes[-1]) #supression de la derniere image
                        sortir = True
                        break;
                if sortir == True: #sortir de la 2eme boucle
                    break;
    
    #collision entre 2 balles
    def collision_between_bullets(self, canvas, fleet):
        sortir1 = False
        sortir2 = False
        for i in range(len(self.fired_bullets)):
            x1, y1, x2, y2 = canvas.bbox(self.fired_bullets[i].id) #coords de la balle du defender
            overlapped = canvas.find_overlapping(x1, y1, x2, y2)
            if len(overlapped) > 1: #plus d'un element dans la meme place
                for j in range(len(fleet.aliens_fired_bullets)):
                    for k in range(len(overlapped)):
                        if overlapped[k] == fleet.aliens_fired_bullets[j].id: #si c'est une balle d'alien
                            self.boom_effect(canvas, x1, y1) #afficher l'effect de collision
                            canvas.delete(self.fired_bullets[i].id) #supression des 2 balles
                            canvas.delete(fleet.aliens_fired_bullets[j].id)
                            del self.fired_bullets[i] #liberation de sa place de la liste
                            del fleet.aliens_fired_bullets[j]
                            sortir1 = True
                            sortir2 = True
                            break;
                    if sortir1 == True: #sortir du 2eme boucle
                        break;
                if sortir2 == True: #3eme boucle
                    break;
    
    #effet si le defender est touché
    def touched_by(self,canvas):
        x,y = canvas.coords(self.id) #recuperation du coord du defender
        self.boom_effect(canvas,x,y) #appelle a la fonction de l'effect de collision    
    
    #effet de collision
    def boom_effect(self, canvas, x, y):
        boom = canvas.create_image(x, y, image=self.boom, tags="boom")
        canvas.after(45,canvas.delete,boom) #suppression de l'effet de Boom
                    
#------------- Bullet ---------------#
class Bullet(object):
    def __init__(self, shooter):
        self.shooter = shooter
        self.id = None
        if self.shooter == "defender": #pour le defender
            self.radius = 10
            self.color = "red"
            self.speed = 8
        elif self.shooter == "alien": #pour l'alien
            self.radius = 8
            self.color = "lime green"
            self.speed = 3
    
    #affichage du bullet du defender
    def install_in(self, canvas):
        if self.shooter=="defender":
            w,h = Defender().get_width() , Defender().get_height() #recuperation de la taille
            x,y = canvas.coords("defender") #recuperation des coords
            x,y = x - w/4 , y - h #positionnement au dessus du defender
            r = self.radius
            self.id = canvas.create_oval(x, y, x+r, y+r, fill = self.color)
            return self
    
    #les balles de l'alien
    def install_aliens_bullets(self, canvas, x, y):
        if self.shooter=="alien":
            r = self.radius
            self.id = canvas.create_oval(x,y,x+r, y+r,fill=self.color)
            canvas.tag_lower(self.id)
            return self
    
    #le mvt verticale des balles
    def move_in(self,canvas):
        if self.shooter=="defender":
            canvas.move(self.id, 0, -self.speed) #vers le haut pour le defender
        elif self.shooter=="alien":
            canvas.move(self.id, 0, self.speed) #vers le bas pour les aliens
             
#-------------Les Bunckers ---------------#

class LesBunckers(object):
    def __init__(self):
        self.damage = 25 #le damage de chaque tire
        self.nb_bunckers = 4
        self.bunckers_liste = [None] * self.nb_bunckers
        self.dx = Fleet().get_width()/5 #entre chaque buncker
    
    #fonction de print()
    def __str__(self):
        ch = "bunkcers id => "
        for elt in range(len(self.bunckers_liste)):
            ch = ch + str(self.bunckers_liste[elt].id) + " ; "
        return ch
    
    #l'installation des bunckers
    def install_in(self,canvas):
        xi = int(canvas.cget("width"))/5  # le x
        for i in range(0,self.nb_bunckers):
            buncker = Buncker()
            yi = int(canvas.cget("height")) - 2*Defender().get_height() - buncker.buncker_height #position dans y
            self.bunckers_liste[i] = buncker.install_in(canvas, xi, yi) #return le self, install pour chaque buncker
            xi += self.dx     
    
    #la collision entre bunkcer est alien
    def buncker_touched_by_alien(self, canvas, fleet):
        sortir1 = False
        sortir2 = False
        for i in range(len(self.bunckers_liste)):
            x1, y1, x2, y2 = canvas.bbox(self.bunckers_liste[i].id) #coords du buncker
            overlapped = canvas.find_overlapping(x1, y1, x2, y2)
            if len(overlapped) > 1:
                for j in range(len(fleet.aliens_fleet)):
                    for k in range(len(overlapped)):
                        if fleet.aliens_fleet[j].id == overlapped[k]: #si c'est un alien
                            self.touched_by(canvas, fleet.aliens_fleet[j]) #effet de collision
                            canvas.delete(self.bunckers_liste[i].id) #delete bancker
                            canvas.delete(fleet.aliens_fleet[j].id) #delate alien
                            self.bunckers_liste[i].health = 0
                            del self.bunckers_liste[i] #delete bancker from liste
                            del fleet.aliens_fleet[j]
                            sortir1 = True
                            sortir2 = True
                            break;
                    if sortir1 == True: #2eme boucle
                        break;
                if sortir2 == True: #3eme boucle
                    break;

    #buncker touché par balles des aliens
    def manage_bunckers_statut(self,canvas,fleet):
        sortir = False
        for a in range(len(self.bunckers_liste)):
            x1, y1, x2, y2 = canvas.bbox(self.bunckers_liste[a].id) #coords de chaque buncker
            overlapped = canvas.find_overlapping(x1, y1, x2, y2)
            if len(overlapped)>1:
                for i in range (len(fleet.aliens_fired_bullets)):
                    for k in range(len(overlapped)):
                        #trouver la meme bullet qui a touché le buncker
                        if fleet.aliens_fired_bullets[i].id == overlapped[k]:
                            x1,y1,x2,y2 = canvas.bbox(fleet.aliens_fired_bullets[i].id)
                            self.boom_effect(canvas,x1+(x2-x1),y2) #l'effect de collision
                            canvas.delete(fleet.aliens_fired_bullets[i].id) #supression de la balle
                            del fleet.aliens_fired_bullets[i] #et sa valeur de la liste
                            self.bunckers_liste[a].health -= self.damage #diminuer sa health
                            #changement de l'image
                            self.bunckers_liste[a] = self.bunckers_liste[a].refresh_buncker_img(canvas)
                            sortir = True
                            break; #les bullets tirées
                    if sortir == True:
                        break;
            if self.bunckers_liste[a].health <= 0: #cas de suppresion du buncker
                canvas.delete(self.bunckers_liste[a].id) #delete damaged bancker
                del self.bunckers_liste[a] #delete bancker from liste
                break;
    
    #pour la collison du buncker avec l'alien
    def touched_by(self,canvas, alien):
        self.boom = PhotoImage(file="explosion.gif")
        x,y = canvas.coords(alien.id)
        boom = canvas.create_image(x, y, image=self.boom, tags="boom")
        canvas.after(45,canvas.delete,boom)    #suppression de l'effet de Boom
    
    #pour la collision entre balles d'alien et buncker
    def boom_effect(self, canvas, x, y):
        self.boom = PhotoImage(file="boom.png")
        boom = canvas.create_image(x, y, image=self.boom, tags="boom")
        canvas.after(45,canvas.delete,boom)    #suppression de l'effet de Boom
        
#------------- Buncker ---------------#

class Buncker(object):
    def __init__(self):
        self.id = None
        self.health = 100
        #images
        self.buncker_img = PhotoImage(file="bunker.gif")
        self.buncker_25 = PhotoImage(file="bunker_25.gif")
        self.buncker_50 = PhotoImage(file="bunker_50.gif")
        self.buncker_75 = PhotoImage(file="bunker_75.gif")
        self.buncker_width = self.buncker_img.width()
        self.buncker_height = self.buncker_img.height()
    
    #affichage d'un buncker
    def install_in(self,canvas, xi, yi):
        #w , h = self.buncker_width//2 , self.buncker_height//2
        #self.id = canvas.create_rectangle(xi-w, yi-h, xi+w, yi+h, fill="green", tags="bunckers")
        self.id = canvas.create_image(xi, yi, image = self.buncker_img , tags="bunckers")
        return self
    
    #changement de l'image selon l'etat du buncker
    def refresh_buncker_img(self, canvas):
        if self.health == 25:
            canvas.itemconfigure(self.id, image=self.buncker_25)
        elif self.health == 50:
            canvas.itemconfigure(self.id, image=self.buncker_50)
        elif self.health == 75:
            canvas.itemconfigure(self.id, image=self.buncker_75)
        return self
            
#------------- Score ---------------#

class Score(object):
    def __init__(self):
        self.name = None
        self.points = 0
        self.winning = False #s'il a gagner ou pas
        self.delai = None #temps joué
        self.start_time = int(time.time())
        self.delai_recommended = 2*60   #delai preferable 2 min
    
    #les accesseurs utilisés
    def get_points(self):
        return self.points
    def set_name(self,Nname):
        self.name = Nname
    
    #changement du score selon le temps
    def refresh_score(self, end_time):
        temps = int(end_time)
        if self.delai_recommended - (temps - self.start_time) > 0: #s'il n'a pas encore depassé le delai preferable
            self.points += self.delai_recommended - (temps - self.start_time)
        else: #sinon, on ajout 10 pts / kill
            self.points += 10
    
    #enregistrement du fuchier
    def toFile(self,file):
        f = open(file,"w")
        json.dump(self.__dict__,f)
        f.close();
    
    #recuperation des donnes du fichier
    #on recupere que les données necessaires
    @classmethod
    def fromFile(cls, file):
        try: #cas normal
            f = open(file,"r")
        except FileNotFoundError:  #si le fichier n'existe pas
            print("Fichier introuvable")
            snew=Score() 
        else:
            d = json.load(f)  #chargement du fichier
            snew = Score()
            snew.name = d["name"] 
            snew.points = d["points"]
            snew.delai = d["delai"]
            snew.winning = d["winning"]
            f.close();
        finally:
            return snew  
    
    #affichage du print()
    def __str__(self):
        return str(self.name) +" -> "+ str(self.points)

        
#------------- Les Resultats ---------------#      
class Resultats(object):
    def __init__(self):
        self.lesResultats=[]
    
    #les accesseurs
    def get_resultats(self):
        return self.lesResultats
    def ajout(self,score):
        self.lesResultats.append(score)
    
    #affichage du print()
    def __str__(self):
        try:
            ch=str(self.lesResultats[0])
            for elt in self.lesResultats[1:]:
                ch=ch +" , "+ str(elt)
            return ch
        except IndexError: #si le fichier est vide, le score n'est pas enregistré
            return "Pas de score enregistré"
    
    #enregistrement dans le fichier
    def toFile(self,file):
        f = open(file,"w")
        tmp=[]
        for s in self.lesResultats:
            dic = {}
            dic["name"] = s.name
            dic["points"] = s.points
            dic["delai"] = s.delai
            dic["winning"] = s.winning
            tmp.append(dic)
        json.dump(tmp,f)
        f.close();
    
    #recuperation des donnes du fichier
    @classmethod
    def fromFile(cls,file):
        try:
            f = open(file, "r")
        except FileNotFoundError: #si le fichier n'existe pas
            print("Ce fichier n'existe pas")
            res=Resultats()
            res.lesResultats=[]
        else:
            tmp = json.load(f)
            liste = []
            for d in tmp:
                sc=Score()
                sc.name = d["name"]
                sc.points = d["points"]
                sc.delai = d["delai"]
                sc.winning = d["winning"]
                liste.append(sc)
            res = Resultats()
            res.lesResultats = liste
            f.close();
        finally:
            return res

#-- lancer le Jeu ---#
SpaceInvaders().play()


# In[ ]:




