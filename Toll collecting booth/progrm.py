import pygame
from pygame.locals import *
import sys
import time
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Toll rates and payment methods
CAR_TOLL = 50
BUS_TOLL = 100
TRUCK_TOLL = 150
PAYMENT_METHODS = ['CASH', 'CARD']
CASH_PROCESSING_TIME = 3000  # milliseconds
CARD_PROCESSING_TIME = 1500  # milliseconds

# Lane configuration
NUM_LANES = 3
LANE_WIDTH = 150
LANE_SPACING = 50

# Statistics tracking
class Statistics:
    def __init__(self):
        self.daily_vehicles = {}
        self.daily_revenue = {}
        self.payment_method_counts = {'CASH': 0, 'CARD': 0}
        
    def update(self, vehicle_type, payment_method, toll_amount):
        current_date = time.strftime("%Y-%m-%d")
        if current_date not in self.daily_vehicles:
            self.daily_vehicles[current_date] = {'CAR': 0, 'BUS': 0, 'TRUCK': 0}
            self.daily_revenue[current_date] = 0
        
        self.daily_vehicles[current_date][vehicle_type] += 1
        self.daily_revenue[current_date] += toll_amount
        self.payment_method_counts[payment_method] += 1

class Lane:
    def __init__(self, lane_number):
        self.number = lane_number
        self.x = (SCREEN_WIDTH // 4) + (lane_number * (LANE_WIDTH + LANE_SPACING))
        self.queue = []
        self.processing = False
        self.processing_time = 0
        self.light_color = RED
        self.light_timer = 0
        
    def update(self, dt):
        self.light_timer += dt
        if self.light_timer >= 5000:  # Change light every 5 seconds
            if self.light_color == RED:
                self.light_color = GREEN
            elif self.light_color == GREEN:
                self.light_color = YELLOW
            elif self.light_color == YELLOW:
                self.light_color = RED
            self.light_timer = 0

# Vehicle constants
CAR_WIDTH = 60
CAR_HEIGHT = 40
BUS_WIDTH = 100
BUS_HEIGHT = 50
TRUCK_WIDTH = 120
TRUCK_HEIGHT = 60

# Initialize the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Toll Booth Simulator')

# Clock for controlling the traffic light timer
clock = pygame.time.Clock()

# Load background image
background_image = pygame.image.load(r"C:\Users\roysa\OneDrive\Desktop\toll collecting booth\background.jpg")
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Initialize variables for tracking
total_vehicles = 0
total_toll_collected = 0
light_color = RED  # Starting with red light
light_timer = 0

pygame.mixer.init()
beep_sound = pygame.mixer.Sound(r"C:\Users\roysa\OneDrive\Desktop\toll collecting booth\collect-ring-15982.mp3") 

# Function to draw the toll booth
def draw_toll_booth(lane):
    # Draw booth structure
    booth_x = lane.x - LANE_WIDTH//2
    pygame.draw.rect(screen, GRAY, (booth_x, SCREEN_HEIGHT // 4, LANE_WIDTH, 200))
    
    # Draw traffic lights
    light_width = LANE_WIDTH // 2
    light_x = booth_x + (LANE_WIDTH - light_width) // 2
    pygame.draw.rect(screen, RED if lane.light_color == RED else BLACK, 
                    (light_x, SCREEN_HEIGHT // 4, light_width, 50))
    pygame.draw.rect(screen, YELLOW if lane.light_color == YELLOW else BLACK,
                    (light_x, SCREEN_HEIGHT // 4 + 75, light_width, 50))
    pygame.draw.rect(screen, GREEN if lane.light_color == GREEN else BLACK,
                    (light_x, SCREEN_HEIGHT // 4 + 150, light_width, 50))
    
    # Draw lane number
    font = pygame.font.Font(None, 36)
    text = font.render(f'Lane {lane.number + 1}', True, WHITE)
    screen.blit(text, (booth_x + LANE_WIDTH//4, SCREEN_HEIGHT // 4 - 30))

# Function to draw a vehicle
def draw_vehicle(color, x, y, width, height):
    pygame.draw.rect(screen, color, (x, y, width, height))

# Function to simulate vehicle passing through toll booth
def process_vehicle(lane, vehicle_type, payment_method):
    global total_vehicles, total_toll_collected, stats
    
    vehicle_width = CAR_WIDTH if vehicle_type == 'CAR' else BUS_WIDTH if vehicle_type == 'BUS' else TRUCK_WIDTH
    vehicle_height = CAR_HEIGHT if vehicle_type == 'CAR' else BUS_HEIGHT if vehicle_type == 'BUS' else TRUCK_HEIGHT
    vehicle_color = BLUE if vehicle_type == 'CAR' else GREEN if vehicle_type == 'BUS' else RED
    
    # Calculate toll and processing time
    toll_collected = CAR_TOLL if vehicle_type == 'CAR' else BUS_TOLL if vehicle_type == 'BUS' else TRUCK_TOLL
    processing_time = CASH_PROCESSING_TIME if payment_method == 'CASH' else CARD_PROCESSING_TIME
    
    # Update statistics
    total_vehicles += 1
    total_toll_collected += toll_collected
    stats.update(vehicle_type, payment_method, toll_collected)
    
    # Animate vehicle movement
    x = -vehicle_width
    target_x = lane.x - vehicle_width // 2
    y = SCREEN_HEIGHT // 2 - vehicle_height // 2
    
    # Move to toll booth
    while x < target_x:
        screen.blit(background_image, (0, 0))
        for l in lanes:
            draw_toll_booth(l)
            for i, (v_type, v_color, v_width, v_height, v_x, v_y) in enumerate(l.queue):
                draw_vehicle(v_color, v_x, v_y, v_width, v_height)
        draw_vehicle(vehicle_color, x, y, vehicle_width, vehicle_height)
        display_stats()
        pygame.display.flip()
        pygame.time.delay(30)
        x += 5
    
    # Process payment
    font = pygame.font.Font(None, 36)
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < processing_time:
        screen.blit(background_image, (0, 0))
        for l in lanes:
            draw_toll_booth(l)
            for i, (v_type, v_color, v_width, v_height, v_x, v_y) in enumerate(l.queue):
                draw_vehicle(v_color, v_x, v_y, v_width, v_height)
        draw_vehicle(vehicle_color, x, y, vehicle_width, vehicle_height)
        text = font.render(f"Processing {payment_method} payment: Rs.{toll_collected}", True, WHITE)
        screen.blit(text, (x - 50, y - 30))
        display_stats()
        pygame.display.flip()
        pygame.time.delay(30)
    
    beep_sound.play()
    
    # Move through booth
    while x < SCREEN_WIDTH + vehicle_width:
        screen.blit(background_image, (0, 0))
        for l in lanes:
            draw_toll_booth(l)
            for i, (v_type, v_color, v_width, v_height, v_x, v_y) in enumerate(l.queue):
                draw_vehicle(v_color, v_x, v_y, v_width, v_height)
        draw_vehicle(vehicle_color, x, y, vehicle_width, vehicle_height)
        display_stats()
        pygame.display.flip()
        pygame.time.delay(30)
        x += 5

# Function to display statistics
def display_stats():
    font = pygame.font.Font(None, 24)
    y_pos = 10
    
    # Display total stats
    text = font.render(f"Total vehicles: {total_vehicles}, Total toll: Rs.{total_toll_collected}", True, WHITE)
    screen.blit(text, (10, y_pos))
    y_pos += 30
    
    # Display today's stats
    current_date = time.strftime("%Y-%m-%d")
    if current_date in stats.daily_vehicles:
        text = font.render(f"Today's vehicles - Car: {stats.daily_vehicles[current_date]['CAR']}, "
                          f"Bus: {stats.daily_vehicles[current_date]['BUS']}, "
                          f"Truck: {stats.daily_vehicles[current_date]['TRUCK']}", True, WHITE)
        screen.blit(text, (10, y_pos))
        y_pos += 30
        text = font.render(f"Today's revenue: Rs.{stats.daily_revenue[current_date]}", True, WHITE)
        screen.blit(text, (10, y_pos))
        y_pos += 30
    
    # Display payment method stats
    text = font.render(f"Payment methods - Cash: {stats.payment_method_counts['CASH']}, "
                      f"Card: {stats.payment_method_counts['CARD']}", True, WHITE)
    screen.blit(text, (10, y_pos))

# Main function to run the toll booth simulation
def main():
    global lanes, stats
    
    # Initialize lanes and statistics
    lanes = [Lane(i) for i in range(NUM_LANES)]
    stats = Statistics()
    
    running = True
    while running:
        dt = clock.get_time()
        screen.blit(background_image, (0, 0))
        
        # Update and draw lanes
        for lane in lanes:
            lane.update(dt)
            draw_toll_booth(lane)
            
            # Process queued vehicles
            if lane.queue and not lane.processing and lane.light_color == GREEN:
                vehicle_info = lane.queue.pop(0)
                process_vehicle(lane, vehicle_info[0], 'CARD' if random.random() > 0.5 else 'CASH')
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_e:  # Emergency vehicle
                    # Find lane with shortest queue
                    target_lane = min(lanes, key=lambda x: len(x.queue))
                    target_lane.light_color = GREEN
                    process_vehicle(target_lane, 'CAR', 'CARD')
                else:
                    # Add vehicle to shortest queue
                    target_lane = min(lanes, key=lambda x: len(x.queue))
                    vehicle_type = None
                    if event.key == pygame.K_c:
                        vehicle_type = 'CAR'
                    elif event.key == pygame.K_b:
                        vehicle_type = 'BUS'
                    elif event.key == pygame.K_t:
                        vehicle_type = 'TRUCK'
                    
                    if vehicle_type:
                        vehicle_width = CAR_WIDTH if vehicle_type == 'CAR' else BUS_WIDTH if vehicle_type == 'BUS' else TRUCK_WIDTH
                        vehicle_height = CAR_HEIGHT if vehicle_type == 'CAR' else BUS_HEIGHT if vehicle_type == 'BUS' else TRUCK_HEIGHT
                        vehicle_color = BLUE if vehicle_type == 'CAR' else GREEN if vehicle_type == 'BUS' else RED
                        queue_pos = len(target_lane.queue)
                        x = target_lane.x - vehicle_width // 2
                        y = SCREEN_HEIGHT // 2 + 100 + (queue_pos * (vehicle_height + 20))
                        target_lane.queue.append((vehicle_type, vehicle_color, vehicle_width, vehicle_height, x, y))
        
        display_stats()
        pygame.display.flip()
        clock.tick(30)  # Limit the loop to 30 frames per second

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
