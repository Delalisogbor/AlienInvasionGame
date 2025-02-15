import sys
from time import sleep

import pygame

#import pyttsx3
from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien


class AlienInvasion:
    """Overall class to manage game assets and behavior."""
    sys.excepthook = sys.__excepthook__
    def __init__(self):
        """Initialize the game, and create game resources"""
        pygame.init()
        self.settings = Settings()
        
        #self.screen = pygame.display.set_mode((1200, 800))
        #self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        
        # Create an instance to store game statistics,
        #   and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        
        
        self.bullet_sound = pygame.mixer.Sound('gunsound.wav')
        self.sound_effect = pygame.mixer.Sound('explosion.wav')
        
        #self.speaker = pyttsx3.init()

        self._create_fleet()
        
        # Make the Play button
        self.play_button = Button(self, "Play")
        
        # Set the background color.
        #self.big_color = (230, 230, 230)
    
    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                
            self._update_screen()
            # Make the most recently drawn screen visible.
            
            # Get rid of bullets that have disappeared
            #for bullet in self.bullets.copy():
                #if bullet.rect.bottom <= 0:
                    #self.bullets.remove(bullet)
            #print(len(self.bullets))
            
    def _check_events(self):
        """Respond to keypresses and mouse events."""
            # Watch for keyboard and mouse events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try:
                    sys.exit()
                except:
                    pass 
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
    
    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
        #   if self.play_button.rect.collidepoint(mouse_pos):

            # Reset the game settings.
            self.settings.initialize_dynamic_settings()

            # Reset the game statistics.
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            # self.sb.prep_level()
            # self.sb.prep_ships()
            
            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            
            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)
    
    def _start_game(self, event):
        if event.key == pygame.K_p and not self.stats.game_active:
            
            self.stats.reset_stats()
            self.stats.game_active = True 
            
            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            
            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)
        
                    
    def _check_keydown_events(self, event):
        """Respond to keypresses."""            
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        #elif event.key == pygame.K_UP:
            #self.ship.moving_up = True
        #elif event.key == pygame.K_DOWN:
            #self.ship.moving_down = True 
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
            #self.bullet_sound.play()
            #self.bullet_sound.play()
        elif event.key == pygame.K_p:
            self._start_game(event)
            
    
    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        #elif event.key == pygame.K_UP:
            #self.ship.moving_up = False
        #elif event.key == pygame.K_DOWN:
           #self.ship.moving_down = False
            
    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            self.bullet_sound.play()
            #self.speaker.say('Bullet fired')
        #self.speaker.runAndWait()
        
    
    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()
        
        # Get rid of bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
                
        self._check_bullet_alien_collisions()
    
    #def start_new_level(self):
        
        #if not self.aliens:
            # Destroy existing bullets and create new fleet.
            #self.bullets.empty()
            #self._create_fleet()
            #self.settings.increase_speed()
            
            # Increase level.
            #self.stats.level += 1
            #self.sb.prep_level()
        
    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.prep_ships()
            self.sb.check_high_score()
            self.sound_effect.play()
            print(len(self.aliens))
        self.start_new_level()
            
    def start_new_level(self):
    
        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            
            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()
            
            #for aliens in collisions.values():
            
            # Resetting the score and resetting the number of ships
            #self.stats.score += self.settings.alien_points
            #self.sb.prep_score()
            #self.sb.prep_ships()
                
        # Check for any bullets that have hit aliens.
        #   If so, get rid of the bullet and the alien.
        
                
    def _update_aliens(self):
        """Update the position of all aliens in the fleet"""
        """
        Check if the fleet is at an edge,
          then update the positions of all aliens in the fleet.
        """
        self._check_fleet_edges()
        self.aliens.update()
        
        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
            #print("Ship hit!!!")
        self._check_aliens_bottom()
        
            # Testing to see if it could move up
                    
            #elif event.type == pygame.KEYDOWN:
             #   if event.key == pygame.K_UP:
              #      self.ship.moving_up = True
               # elif event.key == pygame.K_DOWN:
                #    self.ship.moving_down = True
            
            #elif event.type == pygame.KEYDOWN:
             #   if event.key == pygame.K_UP:
              #      self.ship.moving_up = False
               # elif event.key == pygame.K_DOWN:
                #    self.ship.moving_down = False
                    
                    
                    # Move the ship to the right. 
                    # self.ship.rect.x += 1
    
    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Make an alien.
        # Creating an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to the one alien width.
        alien = Alien(self)
        alien_width, alien_height =  alien.rect.size
        # """alien_width = alien.rect.width"""
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        
        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
         
        # Creat the first row of aliens.
        #for alien_number in range(number_aliens_x):
            # Create an alien and place it in the row.
            #self._create_alien(alien_number)
            
    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width, alien_height =  alien.rect.size
        #"""alien_width = alien.rect.width"""
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + (2 * alien.rect.height) * row_number
        self.aliens.add(alien)
        
    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break 
     
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
        
    
    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ship_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ship_left -= 1
            self.sb.prep_ships()

        
            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
        
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
        
            # Pause.
            sleep(0.5)
        else:
            self.stats.game_active = False
    
    
    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same if the ship got hit.
                self._ship_hit()
                break
        
    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        # Redraw the screen during each pass through the loop.
        
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        
        # Draw the score information.
        self.sb.show_score()
        
        # Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
    
        pygame.display.flip()
        
sys.excepthook = sys.__excepthook__

if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()

