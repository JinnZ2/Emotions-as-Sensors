# ===================================================================
#  EMOTIONS‑AS‑SENSORS EXPLORER
#  A dynamical systems model of emotional intelligence
#  ===================================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from ipywidgets import interact, FloatSlider, IntSlider, Dropdown, VBox, HBox, Output, Button, Checkbox
from IPython.display import display, clear_output, HTML
import warnings
warnings.filterwarnings('ignore')

# -------------------------------------------------------------------
# 1. Glyph System (octahedral, borrowed from Mandala Computing)
# -------------------------------------------------------------------
GLYPHS = ['◈', '◉', '◊', '○', '●', '◐', '◑', '◒']

def state_to_glyph(state, threshold=0.5):
    """Map a continuous sensor value (0-1) to a glyph."""
    idx = int(np.clip(state * 8, 0, 7))
    return GLYPHS[idx]

# -------------------------------------------------------------------
# 2. Emotion Sensor Array
# -------------------------------------------------------------------
class EmotionSensorArray:
    def __init__(self, n_sensors=10, coupling_strength=0.3, decay_rate=0.05, cultural_mode='western'):
        """
        n_sensors: number of sensor nodes (default 10, one per category)
        coupling_strength: how strongly sensors influence each other
        decay_rate: how quickly emotional signals decay over time
        cultural_mode: 'western' or 'vedana' (changes how U(t) is interpreted)
        """
        self.n_sensors = n_sensors
        self.coupling_strength = coupling_strength
        self.decay_rate = decay_rate
        self.cultural_mode = cultural_mode
        
        # Sensor names
        self.sensor_names = [
            'Information Flow',
            'Energy Flow',
            'Network Topology',
            'Emotional Coordination',
            'Specialized Contexts',
            'Advanced Pattern Recognition',
            'Predictive Models',
            'Real‑Time Processing',
            'Validation & Calibration',
            'Privacy‑Preserving Analytics'
        ]
        
        # State: each sensor has a value between 0 and 1
        self.state = np.random.rand(n_sensors) * 0.3  # start low
        
        # Coupling matrix (random, but symmetric)
        np.random.seed(42)
        self.coupling = np.random.randn(n_sensors, n_sensors) * 0.2
        self.coupling = (self.coupling + self.coupling.T) / 2
        np.fill_diagonal(self.coupling, 0)
        
        # History
        self.history = {'state': [self.state.copy()], 'time': [0]}
        self.time = 0
        
        # U(t) — unknown / non‑local effects
        self.U = 0.0
        
    def step(self, dt=0.1, external_input=None, U_strength=0.1):
        """
        Advance the system by one time step.
        external_input: array of length n_sensors, or None
        U_strength: amplitude of the stochastic U(t) term
        """
        self.time += dt
        
        # Compute influence from other sensors (coupling)
        influence = self.coupling @ self.state
        
        # Decay (towards zero)
        decay = -self.decay_rate * self.state
        
        # External input (if provided)
        if external_input is not None:
            external = np.array(external_input) * 0.1
        else:
            external = np.zeros(self.n_sensors)
        
        # U(t): unknown / non‑local effects (stochastic, with cultural modulation)
        if self.cultural_mode == 'western':
            # Western: U(t) is noise to be minimised
            self.U = np.random.randn() * U_strength * 0.1
        else:  # vedana
            # Vedanā: U(t) is a signal of mystery, not an error term[reference:17]
            # It carries meaning — we model it as a slow oscillation
            self.U = 0.05 * np.sin(self.time * 0.1) + 0.02 * np.random.randn()
        
        # Update state (with U(t) injected as a global offset)
        delta = influence + decay + external + self.U * 0.5
        self.state = np.clip(self.state + delta * dt, 0, 1)
        
        # Record history
        self.history['state'].append(self.state.copy())
        self.history['time'].append(self.time)
        
        return self.state.copy()
    
    def inject_shock(self, sensor_idx, magnitude=0.5):
        """Inject a sudden perturbation into a specific sensor."""
        self.state[sensor_idx] = np.clip(self.state[sensor_idx] + magnitude, 0, 1)
    
    def get_sensor_value(self, idx):
        return self.state[idx]
    
    def get_all_states(self):
        return self.state.copy()

# -------------------------------------------------------------------
# 3. Visualisation Engine
# -------------------------------------------------------------------
def plot_sensor_array(array, show_history=True, show_mandala=True):
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(2, 3, height_ratios=[1, 1])
    
    # ---- Panel 1: Sensor state bar chart ----
    ax = fig.add_subplot(gs[0, 0])
    colors = plt.cm.viridis(array.state)
    ax.barh(range(array.n_sensors), array.state, color=colors)
    ax.set_yticks(range(array.n_sensors))
    ax.set_yticklabels(array.sensor_names, fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_xlabel('Sensor activation')
    ax.set_title('Emotion Sensor Array State')
    ax.grid(True, alpha=0.3)
    
    # ---- Panel 2: Coupling matrix ----
    ax = fig.add_subplot(gs[0, 1])
    im = ax.imshow(array.coupling, cmap='RdBu_r', origin='lower', vmin=-1, vmax=1)
    ax.set_title('Sensor Coupling Matrix')
    ax.set_xlabel('Sensor')
    ax.set_ylabel('Sensor')
    plt.colorbar(im, ax=ax, fraction=0.05)
    
    # ---- Panel 3: Glyph Mandala ----
    ax = fig.add_subplot(gs[0, 2])
    n = array.n_sensors
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    radius = 0.4
    for i, (s, angle) in enumerate(zip(array.state, angles)):
        x = 0.5 + radius * np.cos(angle)
        y = 0.5 + radius * np.sin(angle)
        glyph = state_to_glyph(s)
        # Colour based on value
        color = plt.cm.plasma(s)
        ax.text(x, y, glyph, fontsize=28, ha='center', va='center',
               bbox=dict(boxstyle='circle', facecolor=color, alpha=0.8, edgecolor='black'))
        # Draw connecting lines
        for j in range(i+1, n):
            x2 = 0.5 + radius * np.cos(angles[j])
            y2 = 0.5 + radius * np.sin(angles[j])
            # Line thickness based on coupling strength
            weight = abs(array.coupling[i, j]) * 3
            if weight > 0.1:
                ax.plot([x, x2], [y, y2], 'k-', alpha=min(0.5, weight), lw=min(2, weight))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Emotional Mandala (glyphs = sensor states)')
    
    # ---- Panel 4: Time history (if available) ----
    ax = fig.add_subplot(gs[1, 0])
    if len(array.history['state']) > 1:
        hist = np.array(array.history['state'])
        times = np.array(array.history['time'])
        for i in range(min(array.n_sensors, 10)):
            ax.plot(times, hist[:, i], label=array.sensor_names[i][:15], alpha=0.7)
        ax.set_xlabel('Time')
        ax.set_ylabel('Sensor activation')
        ax.set_title('Sensor evolution over time')
        ax.legend(loc='upper right', fontsize=6)
        ax.grid(True, alpha=0.3)
    
    # ---- Panel 5: U(t) and cultural mode ----
    ax = fig.add_subplot(gs[1, 1])
    ax.axis('off')
    info = f"""
    📊 **Emotion Sensor Array**
    ──────────────────────────
    Sensors: {array.n_sensors}
    Cultural mode: {array.cultural_mode}
    Decay rate: {array.decay_rate:.3f}
    Coupling strength: {array.coupling_strength:.3f}
    U(t) (current): {array.U:.4f}
    
    🔍 **Sensor values:**
    """
    for i, name in enumerate(array.sensor_names):
        info += f"\n  {name[:20]}: {array.state[i]:.3f}"
    ax.text(0.05, 0.95, info, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    # ---- Panel 6: Composite emotion (emergent field) ----
    ax = fig.add_subplot(gs[1, 2])
    # Compute a "composite emotion" as a weighted sum of sensor states
    # Inspired by: ["fear", "surprise", "longing"] → "anxious_anticipation"[reference:18]
    weights = np.array([0.2, 0.1, 0.15, 0.2, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05])
    composite = np.sum(array.state * weights)
    # Map to a colour and glyph
    glyph = state_to_glyph(composite)
    color = plt.cm.plasma(composite)
    ax.text(0.5, 0.7, glyph, fontsize=60, ha='center', va='center',
           bbox=dict(boxstyle='circle', facecolor=color, alpha=0.8, edgecolor='black'))
    ax.text(0.5, 0.3, f'Composite emotion: {composite:.2f}', ha='center', va='center', fontsize=12)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Emergent Composite Emotion')
    
    plt.tight_layout()
    plt.show()

# -------------------------------------------------------------------
# 4. Interactive Simulation
# -------------------------------------------------------------------
class EmotionExplorer:
    def __init__(self):
        self.array = None
        self.history = None
        
    def run(self, n_sensors=10, coupling=0.3, decay=0.05, cultural_mode='western',
            steps=100, dt=0.1, U_strength=0.1, inject_shock=False, shock_sensor=0, shock_magnitude=0.5):
        
        self.array = EmotionSensorArray(n_sensors, coupling, decay, cultural_mode)
        
        # Run simulation
        for step in range(steps):
            # Optional shock
            if inject_shock and step == steps // 2:
                self.array.inject_shock(shock_sensor, shock_magnitude)
            self.array.step(dt=dt, U_strength=U_strength)
        
        # Plot
        plot_sensor_array(self.array)
        
        # Print summary
        print(f"\n🧘 Simulation complete: {steps} steps, {cultural_mode} mode")
        print(f"   Final U(t): {self.array.U:.4f}")
        print(f"   Composite emotion: {np.mean(self.array.state):.3f}")

# -------------------------------------------------------------------
# 5. Interactive Widgets
# -------------------------------------------------------------------
explorer = EmotionExplorer()
output = Output()

def run_interactive(n_sensors, coupling, decay, cultural_mode, steps, dt, U_strength,
                    inject_shock, shock_sensor, shock_magnitude):
    with output:
        clear_output(wait=True)
        explorer.run(n_sensors, coupling, decay, cultural_mode, steps, dt, U_strength,
                     inject_shock, shock_sensor, shock_magnitude)

# Widgets
n_sensors_slider = IntSlider(value=10, min=4, max=20, step=1, description='Sensors:')
coupling_slider = FloatSlider(value=0.3, min=0.0, max=1.0, step=0.05, description='Coupling:')
decay_slider = FloatSlider(value=0.05, min=0.0, max=0.2, step=0.01, description='Decay:')
cultural_dropdown = Dropdown(options=['western', 'vedana'], value='western', description='Cultural mode:')
steps_slider = IntSlider(value=100, min=20, max=300, step=10, description='Steps:')
dt_slider = FloatSlider(value=0.1, min=0.01, max=0.5, step=0.01, description='dt:')
U_strength_slider = FloatSlider(value=0.1, min=0.0, max=0.5, step=0.01, description='U(t) strength:')
shock_checkbox = Checkbox(value=False, description='Inject shock')
shock_sensor_slider = IntSlider(value=0, min=0, max=9, step=1, description='Shock sensor:')
shock_magnitude_slider = FloatSlider(value=0.5, min=0.1, max=1.0, step=0.1, description='Shock magnitude:')

run_button = Button(description='Run Simulation', button_style='primary')
reset_button = Button(description='Reset', button_style='warning')

def on_run_clicked(b):
    run_interactive(
        n_sensors_slider.value,
        coupling_slider.value,
        decay_slider.value,
        cultural_dropdown.value,
        steps_slider.value,
        dt_slider.value,
        U_strength_slider.value,
        shock_checkbox.value,
        shock_sensor_slider.value,
        shock_magnitude_slider.value
    )

def on_reset_clicked(b):
    with output:
        clear_output()
        print("🧘 Emotions‑as‑Sensors Explorer ready.")

run_button.on_click(on_run_clicked)
reset_button.on_click(on_reset_clicked)

ui = VBox([
    HTML("<h2>🧘 Emotions‑as‑Sensors Explorer</h2>"),
    HTML("<i>Treating emotions as real‑time, adaptive information‑processing systems</i>"),
    HBox([n_sensors_slider, coupling_slider, decay_slider]),
    HBox([cultural_dropdown, steps_slider, dt_slider]),
    HBox([U_strength_slider, shock_checkbox, shock_sensor_slider, shock_magnitude_slider]),
    HBox([run_button, reset_button]),
    output
])

display(ui)
print("🚀 Emotions‑as‑Sensors Explorer loaded. Click 'Run Simulation' to start.")

# -------------------------------------------------------------------
# 6. Default demo: Western mode with a shock
# -------------------------------------------------------------------
print("\n🧪 Running default: 10 sensors, western mode, with a shock at mid‑point...")
run_interactive(10, 0.3, 0.05, 'western', 100, 0.1, 0.1, True, 0, 0.5)
