# ===================================================================
#  EMOTIONS‑AS‑SENSORS EXPLORER v2
#  Expanded sensors · Cultural framings · BioGrid · Quantum export
#  ===================================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from ipywidgets import interact, FloatSlider, IntSlider, Dropdown, VBox, HBox, Output, Button, Checkbox
from IPython.display import display, clear_output, HTML
import warnings
warnings.filterwarnings('ignore')

# -------------------------------------------------------------------
# 1. Glyph System (octahedral, from Mandala Computing)
# -------------------------------------------------------------------
GLYPHS = ['◈', '◉', '◊', '○', '●', '◐', '◑', '◒']

def state_to_glyph(state, threshold=0.5):
    idx = int(np.clip(state * 8, 0, 7))
    return GLYPHS[idx]

# -------------------------------------------------------------------
# 2. Expanded Sensor Array
# -------------------------------------------------------------------
class ExpandedEmotionArray:
    def __init__(self, n_sensors=15, coupling_strength=0.3, decay_rate=0.05, cultural_mode='western'):
        self.n_sensors = n_sensors
        self.coupling_strength = coupling_strength
        self.decay_rate = decay_rate
        self.cultural_mode = cultural_mode
        
        # Extended sensor list (15 categories)
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
            'Privacy‑Preserving Analytics',
            'Non‑Local Pattern Correlation',  # new
            'Bio‑Synchrony',                  # new
            'Intuition / Field Sensing',      # new
            'Collective Coherence',           # new
            'Cultural Resonance'              # new
        ]
        # Ensure we have exactly n_sensors (if n_sensors > len, pad with generic)
        while len(self.sensor_names) < n_sensors:
            self.sensor_names.append(f'Sensor_{len(self.sensor_names)}')
        self.sensor_names = self.sensor_names[:n_sensors]
        
        # State: each sensor value 0-1
        self.state = np.random.rand(n_sensors) * 0.3
        
        # Coupling matrix (random, symmetric)
        np.random.seed(42)
        self.coupling = np.random.randn(n_sensors, n_sensors) * 0.2
        self.coupling = (self.coupling + self.coupling.T) / 2
        np.fill_diagonal(self.coupling, 0)
        
        # History
        self.history = {'state': [self.state.copy()], 'time': [0]}
        self.time = 0
        
        # U(t) – unknown / non‑local effects (cultural framing modulates this)
        self.U = 0.0
        
        # Cultural parameters
        self.set_cultural_mode(cultural_mode)
        
    def set_cultural_mode(self, mode):
        self.cultural_mode = mode
        if mode == 'western':
            self.U_amplitude = 0.1
            self.U_decay = 0.0
            self.U_memory = 0.0
            self.coupling_modifier = 1.0
        elif mode == 'vedana':
            self.U_amplitude = 0.2
            self.U_decay = 0.01
            self.U_memory = 0.3
            self.coupling_modifier = 0.8
        elif mode == 'indigenous':
            self.U_amplitude = 0.3
            self.U_decay = 0.02
            self.U_memory = 0.5
            self.coupling_modifier = 1.2
        elif mode == 'taoist':
            self.U_amplitude = 0.15
            self.U_decay = 0.005
            self.U_memory = 0.6
            self.coupling_modifier = 0.9
        else:
            self.U_amplitude = 0.1
            self.U_decay = 0.0
            self.U_memory = 0.0
            self.coupling_modifier = 1.0
            
    def step(self, dt=0.1, external_input=None, U_strength=None):
        self.time += dt
        
        # Coupling influence
        influence = self.coupling @ self.state * self.coupling_modifier
        
        # Decay
        decay = -self.decay_rate * self.state
        
        # External input
        if external_input is not None:
            external = np.array(external_input) * 0.1
        else:
            external = np.zeros(self.n_sensors)
        
        # U(t): cultural framing
        if U_strength is None:
            U_strength = self.U_amplitude
            
        if self.cultural_mode == 'western':
            # U(t) is pure noise (to be minimised)
            self.U = np.random.randn() * U_strength * 0.1
        elif self.cultural_mode == 'vedana':
            # U(t) is a slow oscillation with memory (meaningful signal)
            self.U = 0.05 * np.sin(self.time * 0.1) + 0.02 * np.random.randn()
        elif self.cultural_mode == 'indigenous':
            # U(t) carries ancestral patterns (low‑frequency)
            self.U = 0.1 * np.sin(self.time * 0.05) + 0.03 * np.sin(self.time * 0.2)
        elif self.cultural_mode == 'taoist':
            # U(t) is the interplay of yin‑yang (balanced noise)
            self.U = 0.1 * (np.sin(self.time * 0.08) + np.cos(self.time * 0.12)) * 0.5
        else:
            self.U = 0.0
        
        # Update state
        delta = influence + decay + external + self.U * 0.5
        self.state = np.clip(self.state + delta * dt, 0, 1)
        
        # Record
        self.history['state'].append(self.state.copy())
        self.history['time'].append(self.time)
        
        return self.state.copy()
    
    def inject_shock(self, sensor_idx, magnitude=0.5):
        self.state[sensor_idx] = np.clip(self.state[sensor_idx] + magnitude, 0, 1)
    
    def get_composite_emotion(self):
        # Weighted sum of sensors (prioritising coherence and coordination)
        weights = np.array([0.15, 0.1, 0.1, 0.2, 0.05, 0.1, 0.05, 0.05, 0.05, 0.05,
                            0.1, 0.1, 0.15, 0.2, 0.1])  # 15 sensors
        weights = weights[:self.n_sensors] / np.sum(weights[:self.n_sensors])
        return np.sum(self.state * weights)

# -------------------------------------------------------------------
# 3. BioGrid 2.0 – Multi‑Agent Emotional Community
# -------------------------------------------------------------------
class BioGrid:
    def __init__(self, n_agents=20, grid_size=10, array=None):
        self.n_agents = n_agents
        self.grid_size = grid_size
        self.array = array if array else ExpandedEmotionArray(n_sensors=15)
        # Each agent has a position and an emotional state (influenced by the array)
        np.random.seed(42)
        self.positions = np.random.rand(n_agents, 2) * grid_size
        self.emotion_values = np.random.rand(n_agents) * 0.5  # 0-1
        self.social_coupling = 0.3
        self.history = {'emotions': [self.emotion_values.copy()]}
        
    def step(self, dt=0.1):
        # Agents influence each other based on distance
        new_emotions = self.emotion_values.copy()
        for i in range(self.n_agents):
            for j in range(i+1, self.n_agents):
                dist = np.linalg.norm(self.positions[i] - self.positions[j])
                if dist < 2.0:
                    influence = self.social_coupling * (1 - dist/2.0) * (self.emotion_values[j] - self.emotion_values[i])
                    new_emotions[i] += influence * dt
                    new_emotions[j] -= influence * dt  # symmetric
        # Also influenced by the global sensor array (average)
        global_influence = np.mean(self.array.state) * 0.1
        new_emotions += global_influence * dt
        # Clamp
        self.emotion_values = np.clip(new_emotions, 0, 1)
        self.history['emotions'].append(self.emotion_values.copy())
        return self.emotion_values
    
    def get_avg_emotion(self):
        return np.mean(self.emotion_values)

# -------------------------------------------------------------------
# 4. Quantum State Export (OpenQASM)
# -------------------------------------------------------------------
def export_emotion_to_qasm(array, circuit_name='emotion_circuit'):
    """Map sensor states to qubit amplitudes (probabilities) and generate QASM."""
    n = min(array.n_sensors, 8)  # limit to 8 qubits for practicality
    qasm = f"// Emotions‑as‑Sensors Quantum Export: {circuit_name}\n"
    qasm += f"// Cultural mode: {array.cultural_mode}\n"
    qasm += f"// Sensor values: {array.state[:n]}\n\n"
    qasm += "OPENQASM 2.0;\n"
    qasm += f"include \"qelib1.inc\";\n"
    qasm += f"qreg q[{n}];\n"
    qasm += f"creg c[{n}];\n\n"
    
    # Map each sensor value to a rotation angle (0 to π)
    for i in range(n):
        angle = array.state[i] * np.pi
        qasm += f"ry({angle:.4f}) q[{i}];\n"
        qasm += f"rz({angle*0.5:.4f}) q[{i}];\n"
    
    # Entangle adjacent qubits to represent coupling
    for i in range(n-1):
        if abs(array.coupling[i, i+1]) > 0.1:
            qasm += f"cx q[{i}], q[{i+1}];\n"
            qasm += f"rz({array.coupling[i, i+1]:.4f}) q[{i+1}];\n"
            qasm += f"cx q[{i}], q[{i+1}];\n"
    
    # Measurement
    for i in range(n):
        qasm += f"measure q[{i}] -> c[{i}];\n"
    return qasm

# -------------------------------------------------------------------
# 5. Visualisation Engine (v2)
# -------------------------------------------------------------------
def plot_expanded_simulation(array, bigrid=None, show_quantum=True):
    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(3, 3, height_ratios=[1, 1, 0.8])
    
    # Panel 1: Sensor state (bar chart)
    ax = fig.add_subplot(gs[0, 0])
    colors = plt.cm.viridis(array.state)
    ax.barh(range(array.n_sensors), array.state, color=colors)
    ax.set_yticks(range(array.n_sensors))
    ax.set_yticklabels(array.sensor_names, fontsize=7)
    ax.set_xlim(0, 1)
    ax.set_xlabel('Activation')
    ax.set_title('Emotion Sensor Array')
    ax.grid(True, alpha=0.3)
    
    # Panel 2: Coupling matrix
    ax = fig.add_subplot(gs[0, 1])
    im = ax.imshow(array.coupling, cmap='RdBu_r', origin='lower', vmin=-1, vmax=1)
    ax.set_title('Coupling Matrix')
    plt.colorbar(im, ax=ax, fraction=0.05)
    
    # Panel 3: Glyph Mandala
    ax = fig.add_subplot(gs[0, 2])
    n = array.n_sensors
    angles = np.linspace(0, 2*np.pi, n, endpoint=False)
    radius = 0.4
    for i, (s, angle) in enumerate(zip(array.state, angles)):
        x = 0.5 + radius * np.cos(angle)
        y = 0.5 + radius * np.sin(angle)
        glyph = state_to_glyph(s)
        color = plt.cm.plasma(s)
        ax.text(x, y, glyph, fontsize=28, ha='center', va='center',
               bbox=dict(boxstyle='circle', facecolor=color, alpha=0.8))
        for j in range(i+1, n):
            w = abs(array.coupling[i, j]) * 3
            if w > 0.1:
                x2 = 0.5 + radius * np.cos(angles[j])
                y2 = 0.5 + radius * np.sin(angles[j])
                ax.plot([x, x2], [y, y2], 'k-', alpha=min(0.5, w), lw=min(2, w))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.set_aspect('equal')
    ax.axis('off'); ax.set_title('Emotional Mandala')
    
    # Panel 4: Sensor history
    ax = fig.add_subplot(gs[1, 0])
    if len(array.history['state']) > 1:
        hist = np.array(array.history['state'])
        times = np.array(array.history['time'])
        for i in range(min(array.n_sensors, 10)):
            ax.plot(times, hist[:, i], label=array.sensor_names[i][:12], alpha=0.7)
        ax.set_xlabel('Time'); ax.set_ylabel('Activation')
        ax.set_title('Sensor evolution')
        ax.legend(loc='upper right', fontsize=6)
        ax.grid(True, alpha=0.3)
    
    # Panel 5: BioGrid (if provided)
    ax = fig.add_subplot(gs[1, 1])
    if bigrid is not None:
        ax.scatter(bigrid.positions[:,0], bigrid.positions[:,1], 
                   c=bigrid.emotion_values, cmap='viridis', s=50, alpha=0.8)
        ax.set_xlim(0, bigrid.grid_size); ax.set_ylim(0, bigrid.grid_size)
        ax.set_title('BioGrid: Agent Emotions')
        ax.set_xlabel('x'); ax.set_ylabel('y')
        plt.colorbar(ax.collections[0], ax=ax, fraction=0.05, label='Emotion')
    else:
        ax.text(0.5, 0.5, 'No BioGrid', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('BioGrid')
    
    # Panel 6: Info & stats
    ax = fig.add_subplot(gs[1, 2])
    ax.axis('off')
    composite = array.get_composite_emotion()
    info = f"""
    📊 **Expanded Emotion Array**
    ──────────────────────────────
    Mode: {array.cultural_mode}
    Sensors: {array.n_sensors}
    U(t): {array.U:.4f}
    Composite emotion: {composite:.3f}
    """
    if bigrid:
        avg = bigrid.get_avg_emotion()
        info += f"\nBioGrid avg emotion: {avg:.3f}"
    ax.text(0.05, 0.95, info, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    # Panel 7: Quantum state export (preview)
    ax = fig.add_subplot(gs[2, 0])
    if show_quantum:
        qasm = export_emotion_to_qasm(array)
        lines = qasm.split('\n')[:10]
        ax.text(0.1, 0.9, '\n'.join(lines), fontsize=8, family='monospace',
                transform=ax.transAxes, verticalalignment='top')
        ax.set_title('OpenQASM preview')
    else:
        ax.text(0.5, 0.5, 'Export disabled', ha='center', va='center', transform=ax.transAxes)
    ax.axis('off')
    
    # Panel 8: Composite emotion over time (if history length > 1)
    ax = fig.add_subplot(gs[2, 1])
    if len(array.history['state']) > 1:
        hist = np.array(array.history['state'])
        composite_hist = []
        for t in range(len(hist)):
            # Compute weighted sum for each time step
            weights = np.array([0.15, 0.1, 0.1, 0.2, 0.05, 0.1, 0.05, 0.05, 0.05, 0.05,
                                0.1, 0.1, 0.15, 0.2, 0.1])[:array.n_sensors]
            weights = weights / np.sum(weights)
            composite_hist.append(np.sum(hist[t] * weights))
        ax.plot(array.history['time'], composite_hist, 'purple', lw=2)
        ax.set_xlabel('Time'); ax.set_ylabel('Composite emotion')
        ax.set_title('Composite Emotion Evolution')
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, 'Not enough data', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Composite Emotion')
    
    # Panel 9: Cultural mode legend
    ax = fig.add_subplot(gs[2, 2])
    ax.axis('off')
    legend = f"""
    🌍 **Cultural Framing**
    ─────────────────────────
    Current: {array.cultural_mode}
    
    Western:   U(t) = noise (control)
    Vedanā:    U(t) = meaningful signal
    Indigenous:U(t) = ancestral pattern
    Taoist:    U(t) = yin‑yang interplay
    """
    ax.text(0.05, 0.95, legend, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    plt.show()

# -------------------------------------------------------------------
# 6. Unified Explorer v2
# -------------------------------------------------------------------
class EmotionExplorerV2:
    def __init__(self):
        self.array = None
        self.bigrid = None
        
    def run(self, n_sensors=15, coupling=0.3, decay=0.05, cultural_mode='western',
            steps=100, dt=0.1, U_strength=0.1, shock=False, shock_sensor=0, shock_mag=0.5,
            enable_bigrid=True, n_agents=20, grid_size=10, export_quantum=True):
        
        self.array = ExpandedEmotionArray(n_sensors, coupling, decay, cultural_mode)
        if enable_bigrid:
            self.bigrid = BioGrid(n_agents, grid_size, self.array)
        else:
            self.bigrid = None
        
        for step in range(steps):
            if shock and step == steps // 2:
                self.array.inject_shock(shock_sensor, shock_mag)
            self.array.step(dt, U_strength=U_strength)
            if self.bigrid:
                self.bigrid.step(dt)
        
        plot_expanded_simulation(self.array, self.bigrid, show_quantum=export_quantum)
        
        # Print summary
        print(f"\n🧘 Simulation complete: {cultural_mode} mode, {steps} steps")
        print(f"   Final composite emotion: {self.array.get_composite_emotion():.3f}")
        if self.bigrid:
            print(f"   BioGrid avg emotion: {self.bigrid.get_avg_emotion():.3f}")

# -------------------------------------------------------------------
# 7. Interactive UI (v2)
# -------------------------------------------------------------------
explorer = EmotionExplorerV2()
output = Output()

def run_interactive(n_sensors, coupling, decay, cultural_mode, steps, dt, U_strength,
                    shock, shock_sensor, shock_mag, enable_bigrid, n_agents, grid_size, export_quantum):
    with output:
        clear_output(wait=True)
        explorer.run(n_sensors, coupling, decay, cultural_mode, steps, dt, U_strength,
                     shock, shock_sensor, shock_mag, enable_bigrid, n_agents, grid_size, export_quantum)

# Widgets
n_sensors_slider = IntSlider(value=15, min=10, max=25, step=1, description='Sensors:')
coupling_slider = FloatSlider(value=0.3, min=0.0, max=1.0, step=0.05, description='Coupling:')
decay_slider = FloatSlider(value=0.05, min=0.0, max=0.2, step=0.01, description='Decay:')
cultural_dropdown = Dropdown(options=['western', 'vedana', 'indigenous', 'taoist'], value='western', description='Cultural mode:')
steps_slider = IntSlider(value=100, min=20, max=300, step=10, description='Steps:')
dt_slider = FloatSlider(value=0.1, min=0.01, max=0.5, step=0.01, description='dt:')
U_strength_slider = FloatSlider(value=0.1, min=0.0, max=0.5, step=0.01, description='U(t) strength:')
shock_checkbox = Checkbox(value=False, description='Inject shock')
shock_sensor_slider = IntSlider(value=0, min=0, max=24, step=1, description='Shock sensor:')
shock_mag_slider = FloatSlider(value=0.5, min=0.1, max=1.0, step=0.1, description='Shock magnitude:')
bigrid_checkbox = Checkbox(value=True, description='Enable BioGrid')
n_agents_slider = IntSlider(value=20, min=5, max=50, step=1, description='Agents:')
grid_size_slider = IntSlider(value=10, min=5, max=20, step=1, description='Grid size:')
export_q_checkbox = Checkbox(value=True, description='Export quantum circuit')

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
        shock_mag_slider.value,
        bigrid_checkbox.value,
        n_agents_slider.value,
        grid_size_slider.value,
        export_q_checkbox.value
    )

def on_reset_clicked(b):
    with output:
        clear_output()
        print("🧘 Emotions‑as‑Sensors Explorer v2 ready.")

run_button.on_click(on_run_clicked)
reset_button.on_click(on_reset_clicked)

ui = VBox([
    HTML("<h2>🧘 Emotions‑as‑Sensors Explorer v2</h2>"),
    HTML("<i>Expanded sensors · Cultural framings · BioGrid · Quantum export</i>"),
    HBox([n_sensors_slider, coupling_slider, decay_slider]),
    HBox([cultural_dropdown, steps_slider, dt_slider]),
    HBox([U_strength_slider, shock_checkbox, shock_sensor_slider, shock_mag_slider]),
    HBox([bigrid_checkbox, n_agents_slider, grid_size_slider, export_q_checkbox]),
    HBox([run_button, reset_button]),
    output
])

display(ui)
print("🚀 Emotions‑as‑Sensors Explorer v2 loaded. Click 'Run Simulation' to start.")

# -------------------------------------------------------------------
# 8. Default demo: Vedanā mode with BioGrid and quantum export
# -------------------------------------------------------------------
print("\n🧪 Running default: Vedanā mode, 15 sensors, BioGrid enabled, quantum export...")
run_interactive(15, 0.3, 0.05, 'vedana', 100, 0.1, 0.1, True, 0, 0.5, True, 20, 10, True)
