# N-Body simulator

Requires Python >=3.6, Pygame >=2.0.0.dev4

This sim uses step-by-step iterative real-time simulation using Newton's law of gravitation.

## Running

Run `./main.py`.

## Usage

Click and hold the primary mouse button to create a body. Scroll while still holding to change its mass. Move the mouse and release to set the body moving at a velocity (i.e. to 'throw' it).

Alternatively, to prevent a body from moving when the mouse button is released, hold left Ctrl when releasing. This will set the body's velocity to be 0, initially.

### Camera

To pan the camera, use WASD.

[TODO] You cannot zoom the camera at the moment.

### Time scale

To change the time scale, use `,` to halve it and `.` to double it.
