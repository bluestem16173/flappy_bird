# Flappy Bird Game

A Python implementation of the classic Flappy Bird game using Pygame.

## Features

- **Start Screen**: Click "Start" or press SPACE to begin
- **Player Controls**: 
  - SPACE key or Left Mouse Click to flap
  - Bird physics with gravity and jump mechanics
- **Obstacles**: 
  - Walls/pipes with gaps to navigate through
  - Flying enemies that move toward the player
- **Scoring System**: 
  - Points for passing walls
  - Bonus points for avoiding enemies
  - Persistent high score storage
- **Sound Effects**: 
  - Flap sound when jumping
  - Background music
  - Enemy collision sound
  - Game over sound
- **Multiple Levels**: Configurable difficulty levels
- **Game States**: Start screen, playing, and game over screens

## Requirements

- Python 3.7+
- Pygame 2.0+

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install pygame
```

## Assets

The game expects the following assets in the specified directories:

### Images (`assets/images/`)
- `hero.png` - Player character (bird)
- `enemy.png` - Enemy character
- `background.png` - Background image

### Sounds (`assets/mp4/`)
- `flap (1).mp3` - Flap sound effect
- `bg.mp3` - Background music
- `enemy.mp3` - Enemy sound effect
- `gameover.mp3` - Game over sound

## Configuration

Game settings can be modified in `game_config.json`:

- **Game Settings**: Window size, FPS, title
- **Player Settings**: Size, gravity, jump strength
- **Wall Settings**: Width, gap size, speed, spawn distance
- **Enemy Settings**: Size, speed, spawn rate
- **Levels**: Multiple difficulty levels with different parameters
- **Scoring**: Points per wall/enemy, high score file
- **Colors**: Customizable color scheme

## Running the Game

```bash
python flappy_bird.py
```

## Controls

- **SPACE** or **Left Mouse Click**: Flap/Jump
- **ESC** or **Close Window**: Quit game

## Game Mechanics

1. **Player Physics**: 
   - Bird falls due to gravity
   - Flapping provides upward thrust
   - Maximum fall speed prevents excessive acceleration

2. **Obstacles**:
   - Walls spawn at regular intervals with random gap positions
   - Enemies spawn less frequently and move toward the player
   - Both obstacles move from right to left

3. **Collision Detection**:
   - Player collides with walls, enemies, ground, and ceiling
   - Game ends on any collision

4. **Scoring**:
   - 10 points for each wall passed
   - 5 points for each enemy avoided
   - High score is automatically saved and loaded

## File Structure

```
Game-Development/
├── flappy_bird.py          # Main game file
├── game_config.json        # Game configuration
├── high_score.txt          # High score storage (auto-generated)
├── README.md              # This file
├── assets/
│   ├── images/
│   │   ├── hero.png
│   │   ├── enemy.png
│   │   └── background.png
│   └── mp4/
│       ├── flap (1).mp3
│       ├── bg.mp3
│       ├── enemy.mp3
│       └── gameover.mp3
└── venv/                  # Virtual environment
```

## Customization

### Adding New Levels

Edit `game_config.json` to add new levels in the `levels` array:

```json
{
  "level": 4,
  "name": "Expert",
  "wall_speed": 5,
  "enemy_speed": 3,
  "enemy_spawn_rate": 0.8,
  "wall_gap": 160,
  "description": "Extreme challenge for experts"
}
```

### Modifying Game Physics

Adjust player physics in the `player_settings` section:

```json
"player_settings": {
  "gravity": 0.5,        # How fast the bird falls
  "jump_strength": -8,   # How strong the jump is (negative = upward)
  "max_fall_speed": 10   # Maximum falling speed
}
```

### Changing Colors

Modify the color scheme in the `colors` section:

```json
"colors": {
  "background": [135, 206, 235],  # Sky blue
  "text": [255, 255, 255],        # White
  "wall": [34, 139, 34],          # Forest green
  "enemy": [255, 0, 0]            # Red
}
```

## Troubleshooting

### Common Issues

1. **Missing Assets**: If images or sounds are missing, the game will use colored rectangles and skip sound effects
2. **Performance Issues**: Reduce FPS in `game_config.json` or lower the number of enemies
3. **Sound Issues**: Ensure audio files are in the correct format (MP3) and location

### Error Messages

- "Could not load sound": Audio file missing or corrupted
- "Could not load image": Image file missing or corrupted

## Development

The game is structured with the following main classes:

- `FlappyBirdGame`: Main game controller
- `Player`: Player character with physics
- `Wall`: Obstacle walls with collision detection
- `Enemy`: Flying enemies
- `SoundManager`: Audio management
- `ScoreManager`: Scoring and high score persistence

## License

This project is open source and available under the MIT License.







