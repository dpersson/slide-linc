#Slide 0.71 a simple slideshow program
#Copyright (C) 2004  Giorgos Tzambanakis
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import Image
import pygame
import sys
import time
from pygame.locals import*
from os import walk, getcwd
import random
import re

def blit_center(surf, surf_to_blit):
    """
    This takes two surfaces, and blits the second one onto the first
    on the center.
    """
    destpos= (  (surf.get_width()/2 - surf_to_blit.get_width()/2), (surf.get_height()/2 - surf_to_blit.get_height()/2)   )
    surf.blit(surf_to_blit, destpos)
    return pygame.Rect( destpos, surf_to_blit.get_size() )

def int_tuple(tuple):
    """
    This takes a 2 number sequence and returns it into
    integers.
    """
    return (int(tuple[0]), int(tuple[1]))

def create_image_list(rootdir_list):
    """
    This takes a list of directories to walk and
    returns the list with the jpg files in them.
    """
    import random, os
    image_list=[]
    for rootdir in rootdir_list:
        if rootdir[:1] != "#": #this allows commenting out directories
            walker = os.walk(rootdir)
            try:
                while(1):
                    current_tuple = walker.next() #to avoid calling next() more than once in one iteration
                    for filename in current_tuple[2]:
                        if filename[-3:] == "jpg" or filename[-3:] == "JPG": #to filter out other files
                            image_list.append( current_tuple[0] + '/' + filename )
            except StopIteration:
                pass #this will stop when no more files are left in the dirs

    image_list.sort()

    return image_list


def check_list_against_cache(image_list, CACHING_LEVEL):
    """
    This checks the image_list and raises an exception if there are problems.
    Otherwise the return
    value is CACHING_LEVEL. It's job is to ensure that CACHING_LEVEL is lower than
    len(image_list)
    """
    if len(image_list) <= (CACHING_LEVEL):
        CACHING_LEVEL = len(image_list)-1
    if CACHING_LEVEL <= 0:
        raise RuntimeError, "Empty or too short image_list, load more files"
    else:
        return CACHING_LEVEL
 
def main():
    rootdir_list=[]
    rootdir_list.append("/home/daniel/Pictures")

    interval = 5

    LOAD = 0
    BLIT = 2
    MY_EVENT = 25
    ##
    resize = 1
    #################
    WIDTH = 1920
    HEIGHT = 1024
    event = LOAD
    to_blit = -1

    # The following three constants hold the values that
    # will be passed to range() so we can get the alpha values to use
    # for every image we blit. Due to my way of blitting every alpha version
    # of the image on top of the other (see below where we blit) we don't need
    # an ENDING_ALPHA of nowhere near 255. For example (40,100,2) works very
    # well.
    # NOTE: If the range contains too many values it will cause the program
    # not to respond to user input, reason unknown
    STARTING_ALPHA = 0
    ENDING_ALPHA = 255
    ALPHA_STEP = 1

    CACHING_LEVEL = 10
    cache_list = []

    screen =  pygame.display.set_mode( (WIDTH,HEIGHT), FULLSCREEN )
    pygame.mouse.set_visible(0)

    image_list = create_image_list(rootdir_list)
    check_list_against_cache(image_list, CACHING_LEVEL)
    
    pygame.event.set_blocked( (KEYUP, MOUSEMOTION, MOUSEBUTTONUP,
                               MOUSEBUTTONDOWN,
                               VIDEOEXPOSE, ACTIVEEVENT) )

    pygame.time.set_timer( MY_EVENT, interval*500 )

    while(1):
        my_event = pygame.event.wait()
        if my_event.type == QUIT:
            pygame.quit()
            return
        elif my_event.type == KEYDOWN:
            if my_event.key == K_ESCAPE:
                pygame.quit()
                return
            elif my_event.key == K_F4:
                if resize:
                    resize = 0
                else:
                    resize = 1
                
        elif my_event.type == VIDEORESIZE:
            WIDTH = my_event.size[0]
            HEIGHT = my_event.size[1]
            screen =  pygame.display.set_mode( (WIDTH,HEIGHT), RESIZABLE )
        elif my_event.type == MY_EVENT:
            if event == LOAD:
                                        
                while len(cache_list) == 0:
                    # The following code gives us the option to load 
                    # images equal to CACHING_LEVEL instead of one.
                    # This is done to ease up on HD usage when running this
                    # for a long time. cache_list is used as a stack (we could
                    # use it as a queue and it would be the same. If it is empty,
                    # it is filled with images, and then every time a new image
                    # is needed one is popped() and given to the resizing etc. routines
                    to_blit += CACHING_LEVEL
                    if (to_blit >= ( len(image_list) ) ):
                        to_blit = 0
                            
                    for i in range(CACHING_LEVEL):
                        try:
                            cache_list.append(Image.open(image_list[to_blit+i]))
                        except IndexError:
                            break # this will break out of the loop when the end of image_list is reached
                        except IOError:
                            print "IOError on Image.open()"
                            image_list.pop(to_blit+i) #this removes dummy jpg's from the image_list
                            CACHING_LEVEL = check_list_against_cache(image_list, CACHING_LEVEL)
                            continue #this continues, skipping .jpg files that are not really images                        
                ##### END OF Caching code
                #########################
                        
                if len(cache_list) > 0:        
                    impil = cache_list.pop()
                    impil.ar = float(impil.size[0]) / float(impil.size[1]) # (aspect ratio)
                    
                if resize:                    
                    resize_filter = Image.ANTIALIAS
                 
                    try:
                        if impil.size[0] <= WIDTH and impil.size[1] <= HEIGHT:
                            pass
                        elif impil.size[0] >= WIDTH and impil.size[1] <= HEIGHT:
                            impil = impil.resize( int_tuple((WIDTH, WIDTH/impil.ar)), resize_filter )
                        elif impil.size[0] <= WIDTH and impil.size[1] >= HEIGHT:
                            impil = impil.resize( int_tuple((HEIGHT*impil.ar, HEIGHT)), resize_filter )
                            
                        elif impil.size[0] >= WIDTH and impil.size[1] >= HEIGHT:
                            # i need to modify the size twice to get this to fit
                            # on screen. To optimize, I do this by first calculating the desired
                            # size and then resize to avoid resizing the image twice
                            if impil.size[0] > WIDTH: 
                                desired_size = ( WIDTH, WIDTH/impil.ar ) # first we bring width within bounds
                            if desired_size[1] > HEIGHT:
                                desired_size = ( HEIGHT * impil.ar , HEIGHT ) # then, if desired_size's height is out of bounds we correct it. (desired_size[0]/desired_size[1]) == aspect ratio of desired_size
                            impil = impil.resize( int_tuple(desired_size), resize_filter )
                    except IOError:
                        print "IOError!"
                
                try:
                    impyg = pygame.image.fromstring(impil.tostring(), (impil.size[0], impil.size[1]), 'RGB').convert()
                except (ValueError, IOError):
                    #this will keep the program from exiting and will keep impyg set to the
                    #previous pic safely continuing
                    print "Error on fromstring() or tostring()!"
                    
                buffer = pygame.Surface((WIDTH,HEIGHT)).convert()        
                blit_center(buffer, impyg)
                buffer.set_alpha(STARTING_ALPHA)

                event = BLIT

            elif event == BLIT:

                for alpha in range(STARTING_ALPHA, ENDING_ALPHA, ALPHA_STEP):
                    # This creates a fade-in transition effect. The display appears to be showing the
                    # opaque image quite fast, and that's because we're blitting different alpha
                    # versions of the same image on the screen. If I was to blacken the display
                    # before I blit every alpha version of the image it would appear in a different
                    # way. Or at least that's what I think, because testing it this way results in
                    # too much flickering. It doesn't matter anyway, this way is much faster as it
                    # allows for fewer blits to get to a sufficiently opaque image and calls update()
                    # only once for every iteration.
                    buffer.set_alpha(alpha)
                    blit_center(screen, buffer)
                    pygame.display.update()
                    time.sleep(0.03)
                
                event = LOAD
main()
