from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QPainterPath
import random
import math

class Particle:
    def __init__(self, pos, velocity, color):
        self.pos = pos
        self.velocity = velocity
        self.color = color
        self.life = 1.0  # Full life

    def update(self, dt):
        self.pos += self.velocity * dt
        self.life -= dt * 0.1  # Slowly fade out

class AnimatedBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.particles = []
        self.max_particles = 50
        self.colors = [
            QColor(108, 92, 231, 50),  # Primary color (semi-transparent)
            QColor(162, 155, 254, 40),  # Secondary color
            QColor(108, 92, 231, 30),   # Variations
        ]

        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS

    def update_animation(self):
        # Update existing particles
        dt = 0.016  # 16ms in seconds
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update(dt)

        # Add new particles if needed
        while len(self.particles) < self.max_particles:
            self.add_particle()

        self.update()  # Request repaint

    def add_particle(self):
        # Random position along the edges
        if random.random() < 0.5:
            x = random.randint(0, self.width())
            y = 0 if random.random() < 0.5 else self.height()
        else:
            x = 0 if random.random() < 0.5 else self.width()
            y = random.randint(0, self.height())

        # Velocity towards center with some randomness
        center = QPointF(self.width() / 2, self.height() / 2)
        direction = center - QPointF(x, y)
        angle = math.atan2(direction.y(), direction.x())
        angle += random.uniform(-0.5, 0.5)  # Add some randomness
        speed = random.uniform(20, 50)
        velocity = QPointF(math.cos(angle) * speed, math.sin(angle) * speed)

        self.particles.append(Particle(
            QPointF(x, y),
            velocity,
            random.choice(self.colors)
        ))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw connections between nearby particles
        max_distance = 150
        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i+1:]:
                distance = math.sqrt((p1.pos.x() - p2.pos.x())**2 + 
                                  (p1.pos.y() - p2.pos.y())**2)
                if distance < max_distance:
                    opacity = (1 - distance/max_distance) * min(p1.life, p2.life)
                    color = QColor(self.colors[0])
                    color.setAlpha(int(opacity * 25))  # Very faint connections
                    painter.setPen(color)
                    painter.drawLine(p1.pos, p2.pos)

        # Draw particles
        for particle in self.particles:
            color = QColor(particle.color)
            color.setAlpha(int(color.alpha() * particle.life))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)

            size = 4 + (1 - particle.life) * 4  # Particles grow as they fade
            painter.drawEllipse(particle.pos, size, size)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Clear particles when resizing to prevent artifacts
        self.particles.clear()
